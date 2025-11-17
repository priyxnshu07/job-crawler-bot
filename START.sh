#!/bin/bash

cd "/Users/priyanshuparashar/Documents/daily work/jobcrawlerprototype"
source venv/bin/activate

export EMAIL_USER="parasharpriyanshu08@gmail.com"
export EMAIL_PASSWORD="ocigzfqkmecxtcyy"

echo "🚀 Starting Job Crawler..."
echo "Email: $EMAIL_USER"
echo ""
echo "App will be at: http://127.0.0.1:5001"
echo "Press Ctrl+C to stop"
echo ""

python app.py



