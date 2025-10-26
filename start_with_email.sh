#!/bin/bash
# Start Flask app with email credentials

export EMAIL_USER="parasharpriyanshu08@gmail.com"
export EMAIL_PASSWORD="ocigzfqkmecxtcyy"

cd "/Users/priyanshuparashar/Documents/daily work/jobcrawlerprototype"
source venv/bin/activate

echo "✅ Email credentials set!"
echo "Starting Flask app on http://127.0.0.1:5001"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python app.py



