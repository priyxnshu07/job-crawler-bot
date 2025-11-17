#!/bin/bash

# Job Crawler Bot - Setup for Mac
# Double-click this file to run

cd "$(dirname "$0")"

echo ""
echo "========================================"
echo "   JOB CRAWLER BOT - SETUP"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python from https://www.python.org/"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo "Setting up database..."
python database_setup.py

echo ""
echo "========================================"
echo "   SETUP COMPLETE!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Double-click RUN.command to start"
echo "2. Or create .env file for email (optional)"
echo ""
read -p "Press Enter to exit..."

