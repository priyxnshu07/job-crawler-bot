# config.py
# This file contains the configuration for the database connection.
# Supports both local development and cloud deployment (Render, Heroku, etc.)

import os
from urllib.parse import urlparse

# Get database URL from environment (for cloud deployment) or use local config
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Parse DATABASE_URL (format: postgresql://user:password@host:port/dbname)
    # Render and other cloud providers use this format
    parsed = urlparse(DATABASE_URL)
    DATABASE_CONFIG = {
        'dbname': parsed.path[1:],  # Remove leading '/'
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname,
        'port': parsed.port or '5432'
    }
else:
    # Local development configuration
    DATABASE_CONFIG = {
        'dbname': os.environ.get('POSTGRES_DB', 'job_crawler_db'),
        'user': os.environ.get('POSTGRES_USER', 'priyanshuparashar'),
        'password': os.environ.get('POSTGRES_PASSWORD', ''),
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': os.environ.get('POSTGRES_PORT', '5432')
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

