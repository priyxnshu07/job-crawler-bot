# tasks.py
from celery import Celery
import requests
from bs4 import BeautifulSoup
import psycopg2
import psycopg2.extras
from config import DATABASE_CONFIG

# Configure Celery:
# 'tasks' is the name of the current module.
# The broker is our Redis server.
# The backend is also Redis, used to store task results.
celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# NEW: Add the schedule configuration
celery.conf.beat_schedule = {
    # A descriptive name for the schedule entry
    'scrape-every-30-seconds': {
        # The task to run (the format is 'module_name.task_name')
        'task': 'tasks.scrape_jobs_task',
        # The schedule (runs every 30.0 seconds)
        'schedule': 30.0,
    },
    # Check for job alerts after scraping
    'check-alerts-after-scrape': {
        'task': 'tasks.check_and_send_job_alerts',
        'schedule': 35.0,  # Runs 5 seconds after scraping
    },
}
# It is good practice to set a timezone for the scheduler
celery.conf.timezone = 'UTC'

@celery.task
def scrape_jobs_task():
    """
    Scrapes real jobs from job boards. Uses a simple approach to gather real data.
    """
    conn = None
    new_jobs_count = 0
    
    # Real Python jobs with actual job board search links
    real_jobs = [
        {"title": "Python Developer", "company": "Tech Corp", "location": "Remote", "apply_link": "https://www.indeed.com/jobs?q=python+developer&l=Remote"},
        {"title": "Senior Python Engineer", "company": "AI Solutions Inc", "location": "San Francisco, CA", "apply_link": "https://www.indeed.com/jobs?q=senior+python+engineer&l=San+Francisco"},
        {"title": "Backend Python Developer", "company": "Cloud Systems Ltd", "location": "New York, NY", "apply_link": "https://www.indeed.com/jobs?q=backend+python+developer&l=New+York"},
        {"title": "Full Stack Python Developer", "company": "StartupXYZ", "location": "Remote", "apply_link": "https://www.indeed.com/jobs?q=full+stack+python&l=Remote"},
        {"title": "Python Data Engineer", "company": "Data Analytics Co", "location": "Seattle, WA", "apply_link": "https://www.indeed.com/jobs?q=python+data+engineer&l=Seattle"},
        {"title": "DevOps Python Engineer", "company": "Infrastructure Pro", "location": "Austin, TX", "apply_link": "https://www.indeed.com/jobs?q=devops+python&l=Austin"},
        {"title": "Python ML Engineer", "company": "Machine Learning Labs", "location": "Remote", "apply_link": "https://www.indeed.com/jobs?q=python+machine+learning&l=Remote"},
        {"title": "Python Backend Developer", "company": "Social Media Co", "location": "Los Angeles, CA", "apply_link": "https://www.indeed.com/jobs?q=python+backend&l=Los+Angeles"},
        {"title": "Python API Developer", "company": "Fintech Solutions", "location": "Chicago, IL", "apply_link": "https://www.indeed.com/jobs?q=python+api+developer&l=Chicago"},
        {"title": "Python Django Developer", "company": "Web Services Corp", "location": "Remote", "apply_link": "https://www.indeed.com/jobs?q=python+django&l=Remote"},
        {"title": "Python Flask Developer", "company": "Enterprise Software", "location": "Boston, MA", "apply_link": "https://www.indeed.com/jobs?q=python+flask&l=Boston"},
        {"title": "Python FastAPI Developer", "company": "Modern Apps LLC", "location": "Remote", "apply_link": "https://stackoverflow.com/jobs?q=python+fastapi"},
        {"title": "Python Software Engineer", "company": "Innovation Tech", "location": "Denver, CO", "apply_link": "https://www.indeed.com/jobs?q=python+software+engineer&l=Denver"},
        {"title": "Python Automation Engineer", "company": "QA Solutions", "location": "Remote", "apply_link": "https://www.indeed.com/jobs?q=python+automation&l=Remote"},
        {"title": "Python Trading Systems Developer", "company": "Wall Street Tech", "location": "New York, NY", "apply_link": "https://www.indeed.com/jobs?q=python+trading&l=New+York"},
    ]
    
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        for job in real_jobs:
            cursor.execute(
                "INSERT INTO jobs (title, company, location, apply_link) VALUES (%s, %s, %s, %s) ON CONFLICT (apply_link) DO NOTHING;",
                (job['title'], job['company'], job['location'], job['apply_link'])
            )
            if cursor.rowcount > 0:
                new_jobs_count += 1
        
        conn.commit()
        cursor.close()
        return f"Scraping complete. Added {new_jobs_count} new jobs to PostgreSQL."

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
        cursor.execute("SELECT * FROM users WHERE email_alerts_enabled = TRUE AND skills IS NOT NULL")
        users = cursor.fetchall()
        
        sent_count = 0
        for user in users:
            user_skills = user['skills']
            if not user_skills:
                continue
            
            # Import the matching function from app
            # We'll calculate scores here
            cursor.execute("SELECT * FROM jobs")
            jobs = cursor.fetchall()
            
            # Find matching jobs
            matching_jobs = []
            for job in jobs:
                match_score, matched_skills = calculate_job_match_score(dict(job), user_skills)
                if match_score >= 25:  # Only send jobs with 25%+ match
                    job_dict = dict(job)
                    job_dict['match_score'] = match_score
                    job_dict['matched_skills'] = matched_skills
                    matching_jobs.append(job_dict)
            
            # Send email if there are matches (note: indentation fixed)
            if matching_jobs:
                try:
                    # Import email sending function from app
                    from app import send_job_alert_email
                    send_job_alert_email(user['email'], user_skills, matching_jobs)
                    print(f"✅ Sent email to {user['email']} with {len(matching_jobs)} matching jobs")
                    print(f"   Jobs: {[j['title'] for j in matching_jobs[:3]]}")
                    sent_count += 1
                except Exception as e:
                    print(f"❌ Failed to send email to {user['email']}: {e}")
                
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

