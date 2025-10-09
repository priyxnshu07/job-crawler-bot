# app.py
from flask import Flask, render_template, jsonify, request
import psycopg2
import psycopg2.extras
from config import DATABASE_CONFIG
from tasks import scrape_jobs_task  # Import our new task

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search_jobs():
    query = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    search_term = f'%{query}%'
    cursor.execute(
        "SELECT * FROM jobs WHERE title ILIKE %s OR company ILIKE %s OR location ILIKE %s",
        (search_term, search_term, search_term)
    )
    jobs = cursor.fetchall()
    cursor.close()
    conn.close()
    jobs_list = [dict(job) for job in jobs]
    return jsonify(jobs_list)

# NEW ROUTE FOR TESTING OUR BACKGROUND TASK
@app.route('/trigger-scrape')
def trigger_scrape():
    """
    This endpoint triggers the background scraping task.
    `.delay()` sends the task to the Celery queue.
    """
    task = scrape_jobs_task.delay()
    # Return a response immediately, the task runs in the background
    return jsonify({
        "message": "Scraping task has been triggered! It will run in the background.",
        "task_id": task.id
    })

if __name__ == '__main__':
    app.run(debug=True)

