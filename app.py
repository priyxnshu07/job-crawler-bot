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
# from tasks import scrape_jobs_task
from database_setup import setup_database
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

# --- FORCE IPv4 GLOBALLY ---
# Fixes [Errno 101] Network is unreachable on Render/Docker
import socket
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return socket.getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4
# ---------------------------

# Configure Flask-Mail
app.config.update(EMAIL_CONFIG)
mail = Mail(app)

# --- NEW: Upload Folder Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Auto-initialize database on startup (FREE - no shell needed!) ---
try:
    setup_database()
    print("✅ Database initialized automatically on startup")
except Exception as e:
    print(f"⚠️  Database initialization warning: {e}")
    print("   (This is OK if tables already exist)")

# --- Background Scraper (No Worker Service Needed - 100% FREE!) ---
import threading
import time
from datetime import datetime, timedelta
import sys

# Import scraping functions from tasks.py
# Import scraping functions from tasks.py
from tasks import scrape_jobs, build_search_queries_from_skills

def run_background_scraper():
    """
    Background scraper that runs in the web service (no separate worker needed!).
    Scrapes jobs every hour based on user skills.
    """
    # Force flush to ensure logs appear
    sys.stdout.flush()
    print("🔄 Background scraper started (runs every hour)", flush=True)
    sys.stdout.flush()
    
    last_scrape_time = None
    
    while True:
        try:
            # Wait 1 hour between scrapes (or scrape immediately on first run)
            if last_scrape_time is None:
                # First run: wait 2 minutes after startup (reduced from 5)
                print("⏳ Waiting 2 minutes before first scrape...", flush=True)
                sys.stdout.flush()
                time.sleep(120)  # 2 minutes
            else:
                # Subsequent runs: wait 1 hour
                print(f"⏳ Next scrape in 1 hour (last: {last_scrape_time})", flush=True)
                sys.stdout.flush()
                time.sleep(3600)  # 1 hour
            
            print(f"🔄 Starting background scrape at {datetime.now()}", flush=True)
            sys.stdout.flush()
            
            # Get all users with skills
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            cursor.execute("""
                SELECT id, email, skills, preferred_location
                FROM users 
                WHERE skills IS NOT NULL AND array_length(skills, 1) > 0
            """)
            users = cursor.fetchall()
            
            if not users:
                print("⚠️  No users with skills found. Using default Python queries.", flush=True)
                sys.stdout.flush()
                # Fallback: scrape for common Python jobs
                default_locations = ["Bangalore, Karnataka", "Delhi", "Mumbai, Maharashtra", "Remote"]
                queries = ["python developer", "python engineer", "python backend developer"]
                
                all_jobs = []
                for location in default_locations[:3]:
                    for query in queries:
                        try:
                            print(f"  Scraping: {query} in {location}", flush=True)
                            sys.stdout.flush()
                            # scrape_jobs handles all errors internally
                            jobs = scrape_jobs(query=query, location=location, max_jobs=5)
                            if jobs:
                                all_jobs.extend(jobs)
                                print(f"    Found {len(jobs)} jobs", flush=True)
                                sys.stdout.flush()
                            # Delay is already in scrape_jobs
                            time.sleep(1)  # Small additional delay
                        except Exception as e:
                            # scrape_jobs should never raise, but just in case
                            print(f"  Unexpected error scraping {query} in {location}: {str(e)[:50]}", flush=True)
                            sys.stdout.flush()
                            continue
            else:
                print(f"✅ Found {len(users)} users with skills. Scraping personalized jobs...", flush=True)
                sys.stdout.flush()
                
                default_locations = [
                    "Bangalore, Karnataka", "Chandigarh", "Delhi", "Gurgaon, Haryana",
                    "Noida, Uttar Pradesh", "Pune, Maharashtra", "Hyderabad, Telangana",
                    "Mumbai, Maharashtra", "Chennai, Tamil Nadu", "Remote"
                ]
                
                all_jobs = []
                
                # Scrape jobs for each user based on their skills
                for user in users:
                    user_skills = user['skills']
                    preferred_location = user.get('preferred_location')
                    
                    if not user_skills:
                        continue
                    
                    # Build search queries from user skills
                    queries = build_search_queries_from_skills(user_skills)
                    
                    if not queries:
                        continue
                    
                    # Determine locations to scrape
                    if preferred_location:
                        if preferred_location.lower() == "india":
                            locations = default_locations
                        elif preferred_location.lower() == "remote":
                            locations = ["Remote"]
                        else:
                            locations = [preferred_location] + default_locations[:2]
                    else:
                        locations = default_locations[:5]
                    
                    print(f"  Scraping for user {user['email']} with skills: {user_skills[:3]}", flush=True)
                    sys.stdout.flush()
                    
                    # Scrape jobs for this user's skills and locations
                    for location in locations[:3]:  # Limit to 3 locations per user
                        for query in queries[:3]:  # Limit to 3 queries per location
                            try:
                                print(f"    Scraping: {query} in {location}", flush=True)
                                sys.stdout.flush()
                                # scrape_jobs handles all errors internally
                                jobs = scrape_jobs(query=query, location=location, max_jobs=5)
                                if jobs:
                                    all_jobs.extend(jobs)
                                    print(f"      Found {len(jobs)} jobs", flush=True)
                                    sys.stdout.flush()
                                # Delay is already in scrape_jobs, but add small extra delay
                                time.sleep(1)  # Small additional delay
                            except Exception as e:
                                # scrape_jobs should never raise, but just in case
                                print(f"    Unexpected error scraping {query} in {location}: {str(e)[:50]}", flush=True)
                                sys.stdout.flush()
                                continue
            
            # Remove duplicates based on apply_link
            seen_links = set()
            unique_jobs = []
            for job in all_jobs:
                if job['apply_link'] not in seen_links:
                    seen_links.add(job['apply_link'])
                    unique_jobs.append(job)
            
            print(f"✅ Found {len(unique_jobs)} unique jobs from Indeed (from {len(all_jobs)} total)", flush=True)
            sys.stdout.flush()
            
            # Save unique jobs to database
            new_jobs_count = 0
            for job in unique_jobs:
                try:
                    cursor.execute(
                        "INSERT INTO jobs (title, company, location, apply_link) VALUES (%s, %s, %s, %s) ON CONFLICT (apply_link) DO NOTHING;",
                        (job['title'], job['company'], job['location'], job['apply_link'])
                    )
                    if cursor.rowcount > 0:
                        new_jobs_count += 1
                except Exception as e:
                    print(f"    Error inserting job: {e}", flush=True)
                    sys.stdout.flush()
                    continue
            
            conn.commit()
            cursor.close()
            conn.close()
            
            last_scrape_time = datetime.now()
            print(f"✅ Scraping complete. Added {new_jobs_count} new jobs. Next scrape in 1 hour.", flush=True)
            sys.stdout.flush()
            
        except Exception as e:
            print(f"❌ Error in background scraper: {e}", flush=True)
            sys.stdout.flush()
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            time.sleep(60)  # Wait 1 minute before retrying

# Start background scraper in a separate thread
try:
    scraper_thread = threading.Thread(target=run_background_scraper, daemon=True)
    scraper_thread.start()
    print("✅ Background scraper thread started (no worker service needed!)", flush=True)
    sys.stdout.flush()
except Exception as e:
    print(f"❌ ERROR: Failed to start background scraper: {e}", flush=True)
    sys.stdout.flush()
    import traceback
    traceback.print_exc()

# --- Login, Bcrypt, and Form Setup ---
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info' 

# --- User Model ---
class User(UserMixin):
    def __init__(self, id, email, skills=None, email_alerts_enabled=None, email_config=None, preferred_location=None):
        self.id = id
        self.email = email
        self.skills = skills if skills is not None else []
        self.email_alerts_enabled = email_alerts_enabled if email_alerts_enabled is not None else False
        self.email_config = email_config  # Dict with smtp_server, smtp_port, username, password
        self.preferred_location = preferred_location

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
        # Build email config dict if user has email settings
        email_config = None
        if user_data.get('email_username') and user_data.get('email_password'):
            email_config = {
                'smtp_server': user_data.get('email_smtp_server', 'smtp.gmail.com'),
                'smtp_port': user_data.get('email_smtp_port', 587),
                'username': user_data.get('email_username'),
                'password': user_data.get('email_password')  # Stored as-is (app password)
            }
        
        return User(
            id=user_data['id'], 
            email=user_data['email'], 
            skills=user_data['skills'],
            email_alerts_enabled=user_data.get('email_alerts_enabled', False),
            email_config=email_config,
            preferred_location=user_data.get('preferred_location')
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
    preferred_location = current_user.preferred_location
    return render_template('index.html', skills=user_skills, preferred_location=preferred_location)

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
    
    login_form = LoginForm()
    register_form = RegistrationForm()

    if login_form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s;", (login_form.email.data,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data and bcrypt.check_password_hash(user_data['password'], login_form.password.data):
            user = User(
                id=user_data['id'], 
                email=user_data['email'], 
                skills=user_data['skills'],
                preferred_location=user_data.get('preferred_location')
            )
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'error')
    
    return render_template('auth.html', login_form=login_form, register_form=register_form, mode='login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles the user registration process."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    login_form = LoginForm()
    register_form = RegistrationForm()

    if register_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Initialize with an empty skills array
            cursor.execute(
                "INSERT INTO users (email, password, skills) VALUES (%s, %s, %s);", 
                (register_form.email.data, hashed_password, [])
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
    
    return render_template('auth.html', login_form=login_form, register_form=register_form, mode='register')

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
    """API endpoint to search jobs with personalized matching and location filtering."""
    query = request.args.get('q', '')
    personalized = request.args.get('personalized', 'false').lower() == 'true'
    location_param = request.args.get('location', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Get user skills and preferred location
    user_skills = current_user.skills if current_user.skills else []
    preferred_location = current_user.preferred_location
    
    # Build location filter, preferring explicit location parameter over stored preference.
    # Also treat simple city queries (e.g., "Chandigarh") as location-only filters
    # so they don't get AND-ed with an existing preferred_location.
    location_filter = ""
    location_params = []
    effective_location = None
    
    # Known city/location keywords we support explicitly
    known_locations = {
        "bangalore", "bangalore, karnataka",
        "chandigarh",
        "delhi",
        "gurgaon", "gurgaon, haryana",
        "noida", "noida, uttar pradesh",
        "pune", "pune, maharashtra",
        "hyderabad", "hyderabad, telangana",
        "mumbai", "mumbai, maharashtra",
        "chennai", "chennai, tamil nadu",
        "remote",
        "india"
    }

    query_lower = query.strip().lower()

    if location_param:
        # Explicit location parameter from UI overrides everything
        effective_location = location_param
    elif query_lower and query_lower in known_locations and not personalized:
        # User typed a city like "Chandigarh" as the query: treat it purely as location
        effective_location = query
        query = ""  # Clear text query so we only filter by location
    elif preferred_location:
        effective_location = preferred_location

    if effective_location:
        # Support filtering by "India", "Remote", or specific cities
        if effective_location.lower() == "india":
            location_filter = " AND (location ILIKE %s OR location ILIKE %s)"
            location_params = ['%India%', '%india%']
        elif effective_location.lower() == "remote":
            location_filter = " AND location ILIKE %s"
            location_params = ['%Remote%']
        else:
            # Specific location (e.g., "Chandigarh")
            location_filter = " AND location ILIKE %s"
            location_params = [f'%{effective_location}%']
    
    if personalized and user_skills:
        # Personalized search: get jobs (filtered by location if set) and score them
        if location_filter:
            cursor.execute(f"SELECT * FROM jobs WHERE 1=1 {location_filter}", location_params)
        else:
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
            if location_filter:
                cursor.execute(
                    f"SELECT * FROM jobs WHERE (title ILIKE %s OR company ILIKE %s OR location ILIKE %s) {location_filter}",
                    (search_term, search_term, search_term) + tuple(location_params)
                )
            else:
                cursor.execute(
                    "SELECT * FROM jobs WHERE title ILIKE %s OR company ILIKE %s OR location ILIKE %s",
                    (search_term, search_term, search_term)
                )
            jobs = cursor.fetchall()
        else:
            if location_filter:
                cursor.execute(f"SELECT * FROM jobs WHERE 1=1 {location_filter}", location_params)
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
    """Manually triggers scraping (runs in background thread)."""
    # ... existing code ...
    return "Scraping started in background"

@app.route('/test-scrape')
@login_required
def test_scrape():
    """
    Runs a synchronous scrape for the current user and returns the results immediately.
    Useful for debugging "No jobs found".
    """
    try:
        user_skills = current_user.skills
        if not user_skills:
            return jsonify({"status": "error", "message": "No skills found. Please upload a resume first."})
            
        # Build queries
        queries = build_search_queries_from_skills(user_skills)
        if not queries:
            return jsonify({"status": "error", "message": "Could not generate queries from skills."})
            
        # Use preferred location or default
        location = current_user.preferred_location or "India"
        
        results = []
        # Try just the first query to save time
        query = queries[0]
        
        print(f"Testing scrape for: {query} in {location}")
        jobs = scrape_jobs(query=query, location=location, max_jobs=10)
        
        return jsonify({
            "status": "success", 
            "query": query,
            "location": location,
            "jobs_found": len(jobs),
            "jobs": jobs
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})







# --- Email Alert Functions ---
def send_job_alert_email(user_email, user_skills, matched_jobs, user_email_config=None):
    """Send email alert with matching jobs using user's email configuration."""
    if not matched_jobs:
        return False
    
    # Determine which email config to use
    if user_email_config:
        # User has their own email config
        smtp_server = user_email_config.get('smtp_server', 'smtp.gmail.com')
        smtp_port = user_email_config.get('smtp_port', 587)
        smtp_username = user_email_config.get('username')
        smtp_password = user_email_config.get('password')
    else:
        # Try global config
        smtp_server = EMAIL_CONFIG.get('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = EMAIL_CONFIG.get('MAIL_PORT', 587)
        smtp_username = EMAIL_CONFIG.get('MAIL_USERNAME')
        smtp_password = EMAIL_CONFIG.get('MAIL_PASSWORD')
    
    # Check if email is configured
    if not smtp_username or not smtp_password:
        print(f"⚠ Email not configured for {user_email}. Skipping email send.")
        return False
    
    try:
        # Use smtplib directly for per-user email sending
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
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
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"Job Crawler <{smtp_username}>"
        msg['To'] = user_email
        
        # Send email using smtplib
        print(f"   Connecting to {smtp_server}:{smtp_port}...")
        
        # Set a timeout for the connection
        import socket
        socket.setdefaulttimeout(10)  # 10 seconds timeout
        
        server = None # Initialize server to None
        try:
            if int(smtp_port) == 465:
                # SSL Connection
                server = smtplib.SMTP_SSL(smtp_server, int(smtp_port))
            else:
                # TLS Connection
                server = smtplib.SMTP(smtp_server, int(smtp_port))
                server.starttls()
                
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            
            print(f"✅ Email sent successfully to {user_email}")
            return True
        finally:
            if server:
                server.quit()
        
    except Exception as e:
        # Silent error - don't show scary messages to users
        error_msg = str(e)
        if "Authentication" in error_msg or "530" in error_msg:
            print(f"⚠ Email authentication failed for {user_email}. Please check email settings.")
        else:
            print(f"⚠ Email send failed for {user_email}: {error_msg[:50]}")
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

@app.route('/email-settings')
@login_required
def email_settings():
    """Show email configuration page."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT email_smtp_server, email_smtp_port, email_username FROM users WHERE id = %s", (current_user.id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    has_config = user_data and user_data.get('email_username')
    
    return render_template('email_settings.html', 
                         has_config=has_config,
                         smtp_server=user_data.get('email_smtp_server', 'smtp.gmail.com') if user_data else 'smtp.gmail.com',
                         smtp_port=user_data.get('email_smtp_port', 587) if user_data else 587,
                         email_username=user_data.get('email_username', '') if user_data else '')

@app.route('/save-email-settings', methods=['POST'])
@login_required
def save_email_settings():
    """Save user's email configuration."""
    try:
        smtp_server = request.form.get('smtp_server', 'smtp.gmail.com')
        smtp_port = int(request.form.get('smtp_port', 587))
        email_username = request.form.get('email_username', '').strip()
        email_password = request.form.get('email_password', '').strip()
        
        if not email_username:
            return jsonify({"status": "error", "message": "Email address is required"})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Store password as-is (it's already an app-specific password, not the main account password)
        # App passwords are designed to be used directly
        if email_password:
            cursor.execute("""
                UPDATE users 
                SET email_smtp_server = %s, email_smtp_port = %s, 
                    email_username = %s, email_password = %s
                WHERE id = %s
            """, (smtp_server, smtp_port, email_username, email_password, current_user.id))
        else:
            # Don't update password if not provided
            cursor.execute("""
                UPDATE users 
                SET email_smtp_server = %s, email_smtp_port = %s, email_username = %s
                WHERE id = %s
            """, (smtp_server, smtp_port, email_username, current_user.id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Reload user to get updated config
        user_id = current_user.id
        from flask_login import logout_user, login_user
        logout_user()
        user = load_user(user_id)
        login_user(user)
        
        return jsonify({"status": "success", "message": "Email settings saved successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/test-email')
@login_required
def test_email():
    """Send a test email using user's configuration."""
    # Get user's email config
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT email_smtp_server, email_smtp_port, email_username, email_password FROM users WHERE id = %s", (current_user.id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not user_data or not user_data.get('email_username'):
        return jsonify({"status": "error", "message": "Please configure your email settings first!"})
    
    email_config = {
        'smtp_server': user_data.get('email_smtp_server', 'smtp.gmail.com'),
        'smtp_port': user_data.get('email_smtp_port', 587),
        'username': user_data.get('email_username'),
        'password': user_data.get('email_password')
    }
    
    try:
        # Create a simple test email
        test_jobs = [{'title': 'Test Job', 'company': 'Test Company', 'location': 'Test Location', 
                     'apply_link': 'http://127.0.0.1:5001', 'match_score': 100, 'matched_skills': ['Test']}]
        
        if send_job_alert_email(current_user.email, ['Test'], test_jobs, email_config):
            return jsonify({"status": "success", "message": "Test email sent! Check your inbox."})
        else:
            return jsonify({"status": "error", "message": "Failed to send test email. Please check your email settings and app password."})
    except Exception as e:
        print(f"Email test error: {e}")
        return jsonify({"status": "error", "message": "Email configuration error. Please check your settings."})

@app.route('/update-location', methods=['POST'])
@login_required
def update_location():
    """Update user's preferred location."""
    preferred_location = request.form.get('preferred_location', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update preferred location (empty string means no filter)
    cursor.execute(
        "UPDATE users SET preferred_location = %s WHERE id = %s",
        (preferred_location if preferred_location else None, current_user.id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    # Reload user to get updated location
    user_id = current_user.id
    from flask_login import logout_user, login_user
    logout_user()
    user = load_user(user_id)
    login_user(user)
    
    if preferred_location:
        flash(f'Location filter set to: {preferred_location}', 'success')
    else:
        flash('Location filter removed. Showing all jobs.', 'success')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Allow access from all network interfaces for public deployment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host=host, port=port, debug=debug)

