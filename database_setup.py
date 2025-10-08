# database_setup.py
import sqlite3

conn = sqlite3.connect('jobs.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    jobId INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    description TEXT,
    apply_link TEXT UNIQUE
);
''')

print("Database and table created successfully.")

conn.commit()
conn.close()