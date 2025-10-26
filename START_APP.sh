#!/bin/bash
# Quick start script for the Job Crawler App

echo "🚀 Starting Job Crawler App..."
echo ""

# Navigate to project directory
cd "/Users/priyanshuparashar/Documents/daily work/jobcrawlerprototype"

# Activate virtual environment
source venv/bin/activate

# Check if email credentials are set
if [ -z "$EMAIL_USER" ] || [ -z "$EMAIL_PASSWORD" ]; then
    echo "⚠️  Email credentials not set!"
    echo ""
    echo "Please set them first:"
    echo "export EMAIL_USER=\"your-email@gmail.com\""
    echo "export EMAIL_PASSWORD=\"your-app-password\""
    echo ""
    echo "Without these, you can still use the app but emails won't send."
    echo ""
    read -p "Press Enter to continue anyway..."
fi

# Kill any existing Flask processes
pkill -f "python.*app.py" 2>/dev/null

# Start Flask app
echo "Starting Flask app on port 5001..."
python app.py





