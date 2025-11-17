# tasks.py
from celery import Celery
import requests
from bs4 import BeautifulSoup
import psycopg2
import psycopg2.extras
from config import DATABASE_CONFIG
import time
import random
from urllib.parse import urlencode

# Configure Celery:
# Use database as broker if REDIS_URL is not available (100% free, no Redis needed!)
# Falls back to Redis if REDIS_URL is provided
import os
REDIS_URL = os.environ.get('REDIS_URL')
DATABASE_URL = os.environ.get('DATABASE_URL')

# Use database broker if no Redis (free tier friendly!)
if REDIS_URL:
    # Use Redis if available (faster)
    broker_url = REDIS_URL
    backend_url = REDIS_URL
else:
    # Use database as broker (free, no extra service needed!)
    # Convert postgresql:// to db+postgresql:// for Celery
    if DATABASE_URL:
        if DATABASE_URL.startswith('postgresql://'):
            broker_url = DATABASE_URL.replace('postgresql://', 'db+postgresql://', 1)
        else:
            broker_url = f"db+{DATABASE_URL}"
        backend_url = broker_url
    else:
        # Fallback to local Redis for development
        broker_url = 'redis://localhost:6379/0'
        backend_url = 'redis://localhost:6379/0'

celery = Celery('tasks', broker=broker_url, backend=backend_url)

# NEW: Add the schedule configuration
from celery.schedules import crontab
celery.conf.beat_schedule = {
    # Scrape jobs every hour (more reasonable for web scraping)
    'scrape-jobs-hourly': {
        'task': 'tasks.scrape_jobs_task',
        'schedule': 3600.0,  # Every hour (3600 seconds)
    },
    # Check for job alerts every 2 hours
    'check-alerts-periodic': {
        'task': 'tasks.check_and_send_job_alerts',
        'schedule': 7200.0,  # Every 2 hours (7200 seconds)
    },
}
# It is good practice to set a timezone for the scheduler
celery.conf.timezone = 'UTC'

def scrape_indeed_jobs(query="python developer", location="India", max_jobs=20):
    """
    Scrapes real jobs from Indeed.com for a given query and location.
    Returns a list of job dictionaries with title, company, location, and apply_link.
    NO ERRORS - All exceptions are caught and handled gracefully.
    """
    jobs = []
    
    # Validate inputs
    if not query or not query.strip():
        return jobs
    if not location or not location.strip():
        location = "India"  # Default location
    
    # Better headers to avoid 403 errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.indeed.com/',
    }
    
    try:
        # Clean and encode query
        query_clean = query.strip()
        location_clean = location.strip()
        
        # Skip if query is invalid
        if len(query_clean) < 2:
            return jobs
        
        # Build URL with proper encoding
        try:
            params = {
                'q': query_clean,
                'l': location_clean
            }
            url = f"https://www.indeed.com/jobs?{urlencode(params)}"
        except Exception as e:
            print(f"⚠️  Error encoding URL for {query} in {location}: {e}", flush=True)
            return jobs
        
        # Add random delay to avoid rate limiting (before request)
        try:
            time.sleep(random.uniform(4, 7))  # 4-7 second delay
        except:
            time.sleep(5)  # Fallback delay
        
        # Make request with error handling
        try:
            response = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        except requests.exceptions.Timeout:
            print(f"⚠️  Timeout for {query} in {location}. Skipping...", flush=True)
            return jobs
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Request error for {query} in {location}: {str(e)[:50]}. Skipping...", flush=True)
            return jobs
        
        # Check for 403 or other errors
        if response.status_code == 403:
            # Silently skip - don't log to avoid spam
            return jobs
        
        if response.status_code != 200:
            # Skip non-200 responses
            return jobs
        
        # Parse HTML
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"⚠️  Error parsing HTML for {query}: {str(e)[:50]}", flush=True)
            return jobs
        
        # Find job cards on Indeed - try multiple selectors
        job_cards = []
        try:
            job_cards = soup.find_all('div', class_='job_seen_beacon')
        except:
            pass
        
        if not job_cards:
            try:
                job_cards = soup.find_all('div', {'data-jk': True})
            except:
                pass
        
        if not job_cards:
            # No jobs found - this is OK, not an error
            return jobs
        
        # Extract jobs
        for card in job_cards[:max_jobs]:
            try:
                # Extract job title
                title = None
                try:
                    title_elem = card.find('h2', class_='jobTitle')
                    if not title_elem:
                        title_elem = card.find('h2')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                except:
                    pass
                
                if not title or len(title) < 2:
                    continue
                
                # Extract company name
                company = "Company not specified"
                try:
                    company_elem = card.find('span', class_='companyName')
                    if not company_elem:
                        company_elem = card.find('span', {'data-testid': 'company-name'})
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                except:
                    pass
                
                # Extract location
                job_location = location_clean
                try:
                    location_elem = card.find('div', class_='companyLocation')
                    if not location_elem:
                        location_elem = card.find('div', {'data-testid': 'job-location'})
                    if location_elem:
                        job_location = location_elem.get_text(strip=True)
                except:
                    pass
                
                # Extract job link
                apply_link = f"https://www.indeed.com/jobs?{urlencode({'q': query_clean, 'l': location_clean})}"
                try:
                    if title_elem:
                        link_elem = title_elem.find('a')
                        if link_elem and link_elem.get('href'):
                            job_path = link_elem['href']
                            if job_path.startswith('/'):
                                apply_link = f"https://www.indeed.com{job_path}"
                            elif job_path.startswith('http'):
                                apply_link = job_path
                            elif job_path.startswith('viewjob'):
                                apply_link = f"https://www.indeed.com/{job_path}"
                except:
                    pass
                
                # Validate job data
                if title and len(title) > 1:
                    jobs.append({
                        'title': title[:200],  # Limit length
                        'company': company[:200] if company else "Company not specified",
                        'location': job_location[:200] if job_location else location_clean,
                        'apply_link': apply_link[:500]  # Limit length
                    })
            except Exception as e:
                # Silently skip invalid job cards
                continue
                
    except Exception as e:
        # Catch all other errors - don't fail, just return empty list
        pass
    
    return jobs

def build_search_queries_from_skills(skills):
    """
    Build Indeed search queries based on user skills extracted from resumes.
    Filters out invalid skills and fixes special characters.
    Returns a list of search query strings.
    NO ERRORS - All edge cases handled.
    """
    if not skills:
        return []
    
    try:
        # Skills that shouldn't be used for job searches (tools, not job titles)
        invalid_skills = {
            'git', 'jira', 'agile', 'scrum', 'kanban', 'confluence', 'trello',
            'postman', 'insomnia', 'swagger', 'docker compose', 'kubectl',
            'helm', 'terraform', 'vagrant', 'consul', 'vault', 'ansible',
            'puppet', 'chef', 'jenkins', 'gitlab ci', 'github actions',
            'sass', 'scss', 'less', 'webpack', 'babel', 'gulp', 'grunt',
            'jest', 'mocha', 'jasmine', 'cypress', 'selenium', 'pytest',
            'unittest', 'junit', 'testng', 'svn', 'mercurial', 'perforce',
            'asana', 'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'cassandra', 'dynamodb', 'elasticsearch', 'neo4j', 'sqlite',
            'oracle', 'html', 'css', 'tailwind css', 'bootstrap', 'material-ui', 'chakra ui'
        }
        
        # Programming languages and frameworks (valid for job searches)
        valid_skills = {
            'python', 'java', 'javascript', 'typescript', 'go', 'rust',
            'cpp', 'csharp', 'c#', 'c++', 'dotnet', '.net', 'php', 'ruby', 'swift', 'kotlin', 'dart',
            'react', 'angular', 'vue', 'next.js', 'nuxt.js', 'svelte',
            'node.js', 'nodejs', 'express', 'django', 'flask', 'fastapi', 'spring',
            'laravel', 'symfony', 'rails', 'asp.net', 'ember', 'backbone',
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
            'scikit-learn', 'scikit learn', 'scipy', 'tensorflow', 'pytorch', 'keras',
            'xgboost', 'lightgbm', 'opencv', 'nltk', 'spacy',
            'machine learning', 'deep learning', 'neural networks',
            'computer vision', 'nlp', 'natural language processing'
        }
        
        queries = []
        
        # Primary skills (most important) - use top skills from resume
        try:
            primary_skills = [str(skill).lower().strip() for skill in skills[:10] if skill]
        except:
            return []
        
        # Filter and clean skills
        cleaned_skills = []
        for skill in primary_skills:
            try:
                if not skill or len(skill) < 2:
                    continue
                
                # Skip invalid skills
                if skill.lower() in invalid_skills:
                    continue
                
                # Fix special characters
                skill_clean = skill.replace('c++', 'cpp').replace('c#', 'csharp').replace('.net', 'dotnet')
                skill_clean = skill_clean.replace('/', ' ').replace(':', ' ').replace('+', ' ')
                skill_clean = skill_clean.replace('(', '').replace(')', '').replace('[', '').replace(']', '')
                skill_clean = ' '.join(skill_clean.split())  # Remove extra spaces
                
                if len(skill_clean) < 2:
                    continue
                
                # Check if it's a valid programming skill
                skill_lower = skill_clean.lower()
                is_valid = (
                    skill_lower in valid_skills or 
                    any(vs in skill_lower for vs in valid_skills) or
                    skill_lower in ['python', 'java', 'javascript', 'react', 'django', 'flask', 'node.js']
                )
                
                if is_valid or (len(skill_clean) > 2 and skill_lower not in invalid_skills):
                    cleaned_skills.append(skill_clean)
            except:
                continue
        
        # Build queries based on cleaned skills
        for skill in cleaned_skills[:5]:  # Limit to top 5 cleaned skills
            try:
                if len(skill) < 2:
                    continue
                
                skill_lower = skill.lower()
                
                # Direct skill queries (only for programming languages/frameworks)
                if skill_lower in ['python', 'java', 'javascript', 'typescript', 'go', 'rust', 'cpp', 'csharp', 'php', 'ruby']:
                    queries.append(f"{skill} developer")
                    queries.append(f"{skill} engineer")
                
                # Framework-specific queries
                if skill_lower in ['python', 'java', 'javascript', 'react', 'node.js', 'nodejs']:
                    queries.append(f"{skill} backend developer")
                    queries.append(f"{skill} full stack developer")
                
                if skill_lower in ['python', 'django', 'flask', 'fastapi']:
                    queries.append(f"{skill} web developer")
                
                if skill_lower in ['python', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'scikit learn']:
                    queries.append(f"{skill} data engineer")
                    queries.append(f"{skill} machine learning engineer")
                
                # For ML/AI skills
                if 'machine learning' in skill_lower or 'deep learning' in skill_lower or 'nlp' in skill_lower:
                    queries.append(f"{skill} engineer")
                    queries.append(f"{skill} developer")
            except:
                continue
        
        # Remove duplicates and invalid queries
        valid_queries = []
        seen = set()
        for q in queries:
            try:
                q_lower = q.lower()
                # Skip invalid patterns
                if any(inv in q_lower for inv in ['git developer', 'jira developer', 'sql developer', 'html developer', 'css developer']):
                    continue
                if len(q) > 3 and q not in seen:  # Minimum length and no duplicates
                    valid_queries.append(q)
                    seen.add(q)
            except:
                continue
        
        return valid_queries[:8]  # Limit to 8 queries per user
    except Exception as e:
        # Return empty list on any error
        return []

@celery.task
def scrape_jobs_task():
    """
    Scrapes real jobs from Indeed.com based on user skills extracted from resumes.
    Personalizes scraping for each user.
    """
    conn = None
    new_jobs_count = 0
    total_scraped = 0
    
    # Default locations in India (fallback if user has no location preference)
    default_locations = [
        "Bangalore, Karnataka",
        "Chandigarh",
        "Delhi",
        "Gurgaon, Haryana",
        "Noida, Uttar Pradesh",
        "Pune, Maharashtra",
        "Hyderabad, Telangana",
        "Mumbai, Maharashtra",
        "Chennai, Tamil Nadu",
        "Remote"
    ]
    
    try:
        # Get all users with skills
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, email, skills, preferred_location
            FROM users 
            WHERE skills IS NOT NULL AND array_length(skills, 1) > 0
        """)
        users = cursor.fetchall()
        
        if not users:
            print("No users with skills found. Using default Python queries.")
            # Fallback: scrape for common Python jobs
            queries = ["python developer", "python engineer", "python backend developer"]
            for location in default_locations[:5]:  # Limit to 5 locations
                for query in queries:
                    print(f"Scraping Indeed: {query} in {location}")
                    jobs = scrape_indeed_jobs(query=query, location=location, max_jobs=3)
                    total_scraped += len(jobs)
                    # Save jobs
                    for job in jobs:
                        try:
                            cursor.execute(
                                "INSERT INTO jobs (title, company, location, apply_link) VALUES (%s, %s, %s, %s) ON CONFLICT (apply_link) DO NOTHING;",
                                (job['title'], job['company'], job['location'], job['apply_link'])
                            )
                            if cursor.rowcount > 0:
                                new_jobs_count += 1
                        except Exception as e:
                            print(f"Error inserting job: {e}")
                            continue
                    import time
                    time.sleep(2)
        else:
            print(f"Found {len(users)} users with skills. Scraping personalized jobs...")
            
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
                    # Use user's preferred location
                    if preferred_location.lower() == "india":
                        locations = default_locations
                    elif preferred_location.lower() == "remote":
                        locations = ["Remote"]
                    else:
                        # Specific city
                        locations = [preferred_location] + default_locations[:2]  # User location + 2 defaults
                else:
                    # No preference, use default locations
                    locations = default_locations[:5]  # Limit to 5 locations
                
                print(f"Scraping for user {user['email']} with skills: {user_skills[:3]}")
                print(f"  Queries: {queries[:3]}")
                print(f"  Locations: {locations[:3]}")
                
                # Scrape jobs for this user's skills and locations
                for location in locations:
                    for query in queries[:5]:  # Limit to 5 queries per location
                        try:
                            print(f"  Scraping Indeed: {query} in {location}")
                            jobs = scrape_indeed_jobs(query=query, location=location, max_jobs=3)
                            all_jobs.extend(jobs)
                            total_scraped += len(jobs)
                            
                            # Small delay to avoid rate limiting
                            import time
                            time.sleep(2)
                        except Exception as e:
                            print(f"  Error scraping {query} in {location}: {e}")
                            continue
            
            # Remove duplicates based on apply_link
            seen_links = set()
            unique_jobs = []
            for job in all_jobs:
                if job['apply_link'] not in seen_links:
                    seen_links.add(job['apply_link'])
                    unique_jobs.append(job)
            
            print(f"Found {len(unique_jobs)} unique jobs from Indeed (scraped {total_scraped} total)")
            
            # Save unique jobs to database
            for job in unique_jobs:
                try:
                    cursor.execute(
                        "INSERT INTO jobs (title, company, location, apply_link) VALUES (%s, %s, %s, %s) ON CONFLICT (apply_link) DO NOTHING;",
                        (job['title'], job['company'], job['location'], job['apply_link'])
                    )
                    if cursor.rowcount > 0:
                        new_jobs_count += 1
                except Exception as e:
                    print(f"Error inserting job: {e}")
                    continue
        
        conn.commit()
        cursor.close()
        return f"Scraping complete. Added {new_jobs_count} new jobs from Indeed based on user skills. Total scraped: {total_scraped}."

    except Exception as e:
        return f"Database error: {e}"
    finally:
        if conn is not None:
            conn.close()

@celery.task
def check_and_send_job_alerts():
    """
    Check for new matching jobs and send email alerts to users who opted in.
    """
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Get all users with email alerts enabled and skills
        cursor.execute("""
            SELECT id, email, skills, email_alerts_enabled, preferred_location,
                   email_smtp_server, email_smtp_port, email_username, email_password
            FROM users 
            WHERE email_alerts_enabled = TRUE AND skills IS NOT NULL
        """)
        users = cursor.fetchall()
        
        sent_count = 0
        for user in users:
            user_skills = user['skills']
            if not user_skills:
                continue
            
            # Get user's preferred location
            preferred_location = user.get('preferred_location')
            
            # Build location filter if user has a preferred location
            location_filter = ""
            location_params = []
            if preferred_location:
                # Support filtering by "India", "Remote", or specific cities
                if preferred_location.lower() == "india":
                    location_filter = " AND (location ILIKE %s OR location ILIKE %s)"
                    location_params = ['%India%', '%india%']
                elif preferred_location.lower() == "remote":
                    location_filter = " AND location ILIKE %s"
                    location_params = ['%Remote%']
                else:
                    # Specific location
                    location_filter = " AND location ILIKE %s"
                    location_params = [f'%{preferred_location}%']
            
            # Import the matching function from app
            # We'll calculate scores here
            # Filter jobs by location if user has a preference
            if location_filter:
                cursor.execute(f"SELECT * FROM jobs WHERE 1=1 {location_filter}", location_params)
            else:
                cursor.execute("SELECT * FROM jobs")
            jobs = cursor.fetchall()
            
            # Find matching jobs
            matching_jobs = []
            for job in jobs:
                match_score, matched_skills = calculate_job_match_score(dict(job), user_skills)
                if match_score >= 1:  # Lowered threshold to 1% for testing
                    job_dict = dict(job)
                    job_dict['match_score'] = match_score
                    job_dict['matched_skills'] = matched_skills
                    matching_jobs.append(job_dict)
            
            # Send email if there are matches (note: indentation fixed)
            if matching_jobs:
                try:
                    # Get user's email config from database
                    user_email_config = None
                    if user.get('email_username') and user.get('email_password'):
                        user_email_config = {
                            'smtp_server': user.get('email_smtp_server', 'smtp.gmail.com'),
                            'smtp_port': user.get('email_smtp_port', 587),
                            'username': user.get('email_username'),
                            'password': user.get('email_password')  # Already stored as-is (app password)
                        }
                    
                    # Import email sending function from app with app context
                    from app import app, send_job_alert_email
                    with app.app_context():
                        if send_job_alert_email(user['email'], user_skills, matching_jobs, user_email_config):
                            print(f"✅ Sent email to {user['email']} with {len(matching_jobs)} matching jobs")
                            print(f"   Jobs: {[j['title'] for j in matching_jobs[:3]]}")
                            sent_count += 1
                        else:
                            print(f"⚠ Could not send email to {user['email']} - email not configured or auth failed")
                except Exception as e:
                    print(f"❌ Failed to send email to {user['email']}: {str(e)[:100]}")
                
                # Update the timestamp
                cursor.execute(
                    "UPDATE users SET last_email_check = NOW() WHERE id = %s",
                    (user['id'],)
                )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Job alert check complete. Would send {sent_count} emails.")
        return f"Checked {len(users)} users, would send {sent_count} emails"
        
    except Exception as e:
        print(f"Error in job alerts: {e}")
        return f"Error: {e}"

def calculate_job_match_score(job_data, user_skills):
    """Calculate job match score (same as in app.py)."""
    if not user_skills:
        return 0, []
    
    matched_skills = []
    job_text = f"{job_data.get('title', '')} {job_data.get('company', '')}".lower()
    
    for skill in user_skills:
        skill_lower = skill.lower()
        if skill_lower in job_text:
            matched_skills.append(skill)
    
    score = (len(matched_skills) / len(user_skills)) * 100 if len(user_skills) > 0 else 0
    return round(score, 1), matched_skills

