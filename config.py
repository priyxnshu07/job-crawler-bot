# config.py
# This file contains the configuration for the database connection.
# By default, Postgres creates a user with the same name as your computer's username.

import os

DATABASE_CONFIG = {
    'dbname': 'job_crawler_db',
    'user': 'priyanshuparashar',  # Replace with your PostgreSQL username
    'password': '',              # Leave empty if you haven't set a password
    'host': 'localhost',
    'port': '5432'
}

# Email Configuration for Job Alerts
# For Gmail, you need to:
# 1. Enable "Less secure app access" or create an "App Password"
# 2. Go to: https://myaccount.google.com/apppasswords
# 3. Generate an app-specific password for "Mail" and "Other"
# 4. Use that password below (NOT your regular Gmail password)

EMAIL_CONFIG = {
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': os.environ.get('EMAIL_USER'),      # Your Gmail address
    'MAIL_PASSWORD': os.environ.get('EMAIL_PASSWORD'), # Your Gmail app password
    'MAIL_DEFAULT_SENDER': ('Job Crawler', os.environ.get('EMAIL_USER', 'noreply@jobcrawler.com'))
}

