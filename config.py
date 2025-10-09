# config.py
# This file contains the configuration for the database connection.
# By default, Postgres creates a user with the same name as your computer's username.

DATABASE_CONFIG = {
    'dbname': 'job_crawler_db',
    'user': 'priyanshuparashar',  # Replace with your PostgreSQL username
    'password': '',              # Leave empty if you haven't set a password
    'host': 'localhost',
    'port': '5432'
}

