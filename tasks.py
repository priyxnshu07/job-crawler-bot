# tasks.py
from celery import Celery
import requests
from bs4 import BeautifulSoup
import psycopg2
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
}
# It is good practice to set a timezone for the scheduler
celery.conf.timezone = 'UTC'

@celery.task
def scrape_jobs_task():
    """
    A Celery task to scrape jobs and save them to the PostgreSQL database.
    This is the same logic from our old scraper.py, but defined as a task.
    """
    url = "https://realpython.github.io/fake-jobs/"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        # It's better to return an error message than just print
        return f"Failed to retrieve page: {e}"

    soup = BeautifulSoup(response.content, "html.parser")
    job_cards = soup.find_all("div", class_="card-content")
    conn = None
    new_jobs_count = 0
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        for card in job_cards:
            title = card.find("h2", class_="title").text.strip()
            company = card.find("h3", class_="company").text.strip()
            location = card.find("p", class_="location").text.strip()
            link_tag = card.find_all("a")[-1]
            apply_link = link_tag['href']

            cursor.execute(
                "INSERT INTO jobs (title, company, location, apply_link) VALUES (%s, %s, %s, %s) ON CONFLICT (apply_link) DO NOTHING;",
                (title, company, location, apply_link)
            )
            # cursor.rowcount will be 1 if a new row was inserted, 0 otherwise.
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

