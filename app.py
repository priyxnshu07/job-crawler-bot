# app.py
from flask import (
    Flask, render_template, jsonify, request, 
    redirect, url_for, flash
)
from flask_login import (
    LoginManager, UserMixin, login_user, 
    logout_user, login_required, current_user
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import psycopg2
import psycopg2.extras
from config import DATABASE_CONFIG, EMAIL_CONFIG
from tasks import scrape_jobs_task
import os
# --- NEW IMPORTS ---
import re
import spacy
from werkzeug.utils import secure_filename

# Try to load spaCy model, download if not available
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("spaCy model 'en_core_web_sm' not found. Please install it with:")
    print("python -m spacy download en_core_web_sm")
    print("For now, continuing without spaCy NER...")
    nlp = None

# Import file reading utilities
from PyPDF2 import PdfReader
import docx

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key-that-you-should-change')

# Configure Flask-Mail
app.config.update(EMAIL_CONFIG)
mail = Mail(app)

# --- NEW: Upload Folder Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Login, Bcrypt, and Form Setup ---
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info' 

# --- User Model ---
class User(UserMixin):
    def __init__(self, id, email, skills=None, email_alerts_enabled=None):
        self.id = id
        self.email = email
        self.skills = skills if skills is not None else []
        self.email_alerts_enabled = email_alerts_enabled if email_alerts_enabled is not None else False

@login_manager.user_loader
def load_user(user_id):
    """Loads the user from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        return User(
            id=user_data['id'], 
            email=user_data['email'], 
            skills=user_data['skills'],
            email_alerts_enabled=user_data.get('email_alerts_enabled', False)
        )
    return None

# --- Forms ---
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# --- Database Connection ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn

# --- Helper Function for File Upload ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Resume Parsing Functions ---
def extract_text_from_pdf(filepath):
    """Extract text from PDF file."""
    try:
        text = ""
        reader = PdfReader(filepath)
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def extract_text_from_docx(filepath):
    """Extract text from DOCX file."""
    try:
        doc = docx.Document(filepath)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")

def extract_skills_from_text(text):
    """
    Extract technical skills from resume text, filtering out non-skills like
    company names, job titles, dates, and descriptive phrases.
    """
    if not text:
        return []
    
    skills_found = set()
    text_lower = text.lower()
    
    # Comprehensive technical skills database
    technical_skills = {
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'html', 'css', 'go', 'rust', 
        'c++', 'c#', '.net', 'php', 'ruby', 'swift', 'kotlin', 'dart',
        # Web Frameworks & Libraries
        'react', 'angular', 'vue', 'next.js', 'nuxt.js', 'svelte', 
        'node.js', 'express', 'django', 'flask', 'fastapi', 'spring', 
        'laravel', 'symfony', 'rails', 'asp.net', 'ember', 'backbone',
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 
        'dynamodb', 'elasticsearch', 'neo4j', 'sqlite', 'oracle',
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 
        'jenkins', 'gitlab ci', 'github actions', 'ansible', 'puppet',
        'chef', 'vagrant', 'consul', 'vault',
        # Data Science & ML
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 
        'scikit-learn', 'scipy', 'tensorflow', 'pytorch', 'keras',
        'xgboost', 'lightgbm', 'opencv', 'nltk', 'spaCy',
        # Machine Learning & AI
        'machine learning', 'deep learning', 'neural networks', 
        'computer vision', 'nlp', 'natural language processing',
        # Frontend Tools
        'sass', 'scss', 'less', 'webpack', 'babel', 'gulp', 'grunt',
        'tailwind css', 'bootstrap', 'material-ui', 'chakra ui',
        # Testing
        'jest', 'mocha', 'jasmine', 'cypress', 'selenium', 'pytest',
        'unittest', 'junit', 'testng',
        # Version Control & Tools
        'git', 'svn', 'mercurial', 'perforce',
        # Agile & Project Management
        'agile', 'scrum', 'kanban', 'jira', 'confluence', 'trello',
        'asana', 'monday.com',
        # APIs & Protocols
        'rest', 'graphql', 'soap', 'grpc', 'websocket', 'rest api',
        # Operating Systems
        'linux', 'unix', 'bash', 'powershell', 'shell scripting',
        # Other Tools
        'postman', 'insomnia', 'swagger', 'docker compose', 'kubectl',
        'helm', 'terraform', 'vagrant', 'vagrantfile'
    }
    
    # Only look for technical skills in the text
    for skill in technical_skills:
        if skill in text_lower:
            skills_found.add(skill.title() if skill.islower() else skill)
    
    # Extract skills from "Skills:" sections with better filtering
    skills_pattern = r'(?:technical\s+)?skills?[:\-]?\s*([^\n]{20,500})'
    matches = re.findall(skills_pattern, text_lower, re.IGNORECASE)
    
    for match in matches:
        # Clean up prefixes and split
        clean_match = re.sub(r'^(programming|tools?|frameworks?|databases?|libraries?):\s*', '', match, flags=re.IGNORECASE)
        
        # Split by various delimiters
        potential_skills = re.split(r'[,;•\n]', clean_match)
        
        for skill in potential_skills:
            skill = skill.strip().lower()
            
            # Filter out non-skills
            if not skill or len(skill) < 2 or len(skill) > 40:
                continue
            
            # Skip if it contains job-related keywords
            if any(word in skill for word in ['intern', 'junior', 'senior', 'developer', 
                                                'engineer', 'manager', 'analyst', 'qa', 'quality']):
                continue
            
            # Skip dates, company names, and long descriptions
            if re.search(r'\d{4}', skill):  # Contains year
                continue
            
            # Skip if it's a library name that we already know about
            if any(sk in skill for sk in ['library', 'libraries', 'framework', 'tool', 'tools']):
                continue
            
            # Only add if it's in our technical skills list or looks like one
            if any(ts in skill or skill in ts for ts in technical_skills):
                skills_found.add(skill.title())
    
    # Clean up results - remove any remaining non-skills
    filtered_skills = []
    for skill in skills_found:
        skill_lower = skill.lower()
        
        # Skip library names that look like code
        if skill_lower.startswith('py') and len(skill) > 8:
            continue
        
        # Skip if it looks like a company name (has 'ltd', 'inc', 'corp', etc.)
        if any(word in skill_lower for word in ['ltd', 'inc', 'corp', 'international', 'global']):
            continue
        
        # Skip job titles
        if any(word in skill_lower for word in ['intern', 'associate', 'specialist', 'officer']):
            continue
        
        # Skip dates and time periods
        if re.search(r'\d{4}|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\b', skill_lower):
            continue
        
        # Skip generic tools that aren't technical skills
        if skill_lower in ['ms office', 'office', 'windows', 'mac', 'linux operating system']:
            continue
        
        filtered_skills.append(skill)
    
    # Return sorted, unique skills
    return sorted(list(set(filtered_skills)))

# --- Core App Routes ---
@app.route('/')
@login_required
def index():
    """
    Serves the main job dashboard.
    NOW ALSO fetches and displays the user's current skills.
    """
    # current_user is available from Flask-Login
    # and our load_user function populates it.
    user_skills = current_user.skills
    return render_template('index.html', skills=user_skills)

# --- NEW: Resume Upload Route ---
@app.route('/upload_resume', methods=['POST'])
@login_required
def upload_resume():
    """Handles the resume file upload and parsing."""
    if 'resume' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    
    file = request.files['resume']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # --- Extract Text from Resume ---
            file_ext = filename.rsplit('.', 1)[1].lower()
            text = ""
            
            if file_ext == 'pdf':
                text = extract_text_from_pdf(filepath)
            elif file_ext in ['doc', 'docx']:
                text = extract_text_from_docx(filepath)
            else:
                flash('Unsupported file type.', 'error')
                return redirect(url_for('index'))
            
            # Debug: Show text length
            print(f"Extracted {len(text)} characters from resume")
            print(f"First 500 chars: {text[:500]}")
            
            # --- Extract Skills from Text ---
            skills = extract_skills_from_text(text)
            
            print(f"Extracted {len(skills)} skills: {skills}")
            
            if not skills:
                flash('Could not extract any skills from the resume. Please ensure your resume mentions technical skills or keywords.', 'error')
                return redirect(url_for('index'))

            # --- Save Skills to Database ---
            conn = get_db_connection()
            cursor = conn.cursor()
            # Update the user's skills column in the 'users' table
            cursor.execute(
                "UPDATE users SET skills = %s WHERE id = %s;", 
                (skills, current_user.id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            flash(f'Resume uploaded successfully! Extracted {len(skills)} skill(s).', 'success')
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Detailed error during parsing: {error_details}")  # For debugging
            flash(f'An error occurred during parsing: {str(e)}', 'error')
        finally:
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
                
        return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload a PDF, DOC, or DOCX file.', 'error')
        return redirect(url_for('index'))

# --- Authentication Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles the user login process."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s;", (form.email.data,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data and bcrypt.check_password_hash(user_data['password'], form.password.data):
            user = User(id=user_data['id'], email=user_data['email'], skills=user_data['skills'])
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'error')
            
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles the user registration process."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Initialize with an empty skills array
            cursor.execute(
                "INSERT INTO users (email, password, skills) VALUES (%s, %s, %s);", 
                (form.email.data, hashed_password, [])
            )
            conn.commit()
            flash('Your account has been created! You are now able to log in.', 'success')
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            conn.rollback() 
            flash('Email address already exists. Please use a different one.', 'error')
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {e}', 'error')
        finally:
            cursor.close()
            conn.close()
            
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    """Logs the user out."""
    logout_user()
    return redirect(url_for('login'))

def calculate_job_match_score(job_data, user_skills):
    """
    Calculate how well a job matches the user's skills.
    Returns a match score (0-100) and list of matched skills.
    """
    if not user_skills:
        return 0, []
    
    matched_skills = []
    job_text = f"{job_data.get('title', '')} {job_data.get('company', '')}".lower()
    
    # Check each user skill against job title and company
    for skill in user_skills:
        skill_lower = skill.lower()
        # Check if skill appears in job title or company name
        if skill_lower in job_text:
            matched_skills.append(skill)
    
    # Calculate score: percentage of user skills that matched
    if len(user_skills) > 0:
        score = (len(matched_skills) / len(user_skills)) * 100
    else:
        score = 0
    
    return round(score, 1), matched_skills

@app.route('/search')
@login_required
def search_jobs():
    """API endpoint to search jobs with personalized matching."""
    query = request.args.get('q', '')
    personalized = request.args.get('personalized', 'false').lower() == 'true'
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Get user skills
    user_skills = current_user.skills if current_user.skills else []
    
    if personalized and user_skills:
        # Personalized search: get all jobs and score them
        cursor.execute("SELECT * FROM jobs")
        jobs = cursor.fetchall()
        
        # Calculate match scores
        jobs_with_scores = []
        for job in jobs:
            match_score, matched_skills = calculate_job_match_score(dict(job), user_skills)
            job_dict = dict(job)
            job_dict['match_score'] = match_score
            job_dict['matched_skills'] = matched_skills
            jobs_with_scores.append(job_dict)
        
        # Sort by match score (highest first)
        jobs_with_scores.sort(key=lambda x: x['match_score'], reverse=True)
        
        cursor.close()
        conn.close()
        return jsonify(jobs_with_scores)
    else:
        # Regular search
        if query:
            search_term = f'%{query}%'
            cursor.execute(
                "SELECT * FROM jobs WHERE title ILIKE %s OR company ILIKE %s OR location ILIKE %s",
                (search_term, search_term, search_term)
            )
            jobs = cursor.fetchall()
        else:
            cursor.execute("SELECT * FROM jobs")
            jobs = cursor.fetchall()
        
        # Add match scores for display (even in regular search)
        jobs_list = []
        for job in jobs:
            job_dict = dict(job)
            if user_skills:
                match_score, matched_skills = calculate_job_match_score(job_dict, user_skills)
                job_dict['match_score'] = match_score
                job_dict['matched_skills'] = matched_skills
            else:
                job_dict['match_score'] = 0
                job_dict['matched_skills'] = []
            jobs_list.append(job_dict)
        
        cursor.close()
        conn.close()
        return jsonify(jobs_list)

@app.route('/trigger-scrape')
@login_required
def trigger_scrape():
    """Manually triggers the background scraping task."""
    task = scrape_jobs_task.delay()
    return jsonify({
        "message": "Scraping task has been triggered! It will run in the background.",
        "task_id": task.id
    })

# --- Email Alert Functions ---
def send_job_alert_email(user_email, user_skills, matched_jobs):
    """Send email alert with matching jobs."""
    if not matched_jobs:
        return False
    
    try:
        subject = f"🎯 {len(matched_jobs)} New Job Matches!"
        
        html_body = f"""
        <html><body style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px;">
            <h2 style="color: #007bff;">🎉 New Job Matches Found!</h2>
            <p>Based on your skills: <strong>{', '.join(user_skills[:5])}</strong></p>
            <p><strong>We found {len(matched_jobs)} jobs that match your profile:</strong></p>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            {''.join([f'''
            <div style="background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #007bff;">
                <h3 style="margin-top: 0; color: #333;">{job['title']}</h3>
                <p><strong>Company:</strong> {job['company']}</p>
                <p><strong>Location:</strong> {job['location']}</p>
                <p><strong style="color: #28a745;">Match Score: {job.get('match_score', 0)}%</strong></p>
                {f"<p><strong>Matched Skills:</strong> {', '.join(job.get('matched_skills', [])[:5])}</p>" if job.get('matched_skills') else ''}
                <a href="{job['apply_link']}" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">Apply Now</a>
            </div>
            ''' for job in matched_jobs[:10]])}
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="color: #666; font-size: 0.9rem;"><a href="http://127.0.0.1:5001" style="color: #007bff;">View All Jobs</a> | This is an automated alert from your Job Crawler Bot.</p>
        </body></html>
        """
        
        msg = Message(subject, recipients=[user_email], html=html_body)
        mail.send(msg)
        print(f"✓ Sent email to {user_email}")
        return True
    except Exception as e:
        print(f"✗ Email failed: {e}")
        return False

@app.route('/toggle-email-alerts', methods=['POST'])
@login_required
def toggle_email_alerts():
    """Toggle user's email alert preference."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    new_status = not current_user.email_alerts_enabled
    cursor.execute(
        "UPDATE users SET email_alerts_enabled = %s WHERE id = %s",
        (new_status, current_user.id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    flash(f'Email alerts {"enabled" if new_status else "disabled"}!', 'success')
    return jsonify({'success': True, 'enabled': new_status})

@app.route('/test-email')
@login_required
def test_email():
    """Send a test email."""
    try:
        msg = Message(
            'Test Email from Job Crawler',
            recipients=[current_user.email],
            html=f'<h2>Test Email</h2><p>Hello {current_user.email}!</p><p>Email alerts are working!</p>'
        )
        mail.send(msg)
        flash('Test email sent! Check your inbox.', 'success')
    except Exception as e:
        flash(f'Email error: {str(e)}', 'error')
        print(f"Email error: {e}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)

