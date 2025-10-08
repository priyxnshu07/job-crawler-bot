# app.py
from flask import Flask, render_template, jsonify, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search_jobs():
    query = request.args.get('q', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM jobs WHERE title LIKE ? OR company LIKE ? OR location LIKE ?",
        (f'%{query}%', f'%{query}%', f'%{query}%')
    )
    jobs = cursor.fetchall()
    conn.close()
    
    jobs_list = [dict(job) for job in jobs]
    return jsonify(jobs_list)

if __name__ == '__main__':
    app.run(debug=True)