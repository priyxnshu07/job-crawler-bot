#!/bin/bash

# Setup script for Job Crawler Bot
# This script installs all dependencies and sets up the environment

echo "🔧 Setting up Job Crawler Bot..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found!"
    echo "Please install PostgreSQL: https://www.postgresql.org/download/"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install spaCy model
echo "📦 Downloading spaCy language model..."
python -m spacy download en_core_web_sm

# Setup database
echo "📦 Setting up database..."
python database_setup.py

# Setup email credentials
echo ""
echo "📧 Email Setup"
echo "=============="
echo "To receive job alerts via email, you need to:"
echo ""
echo "1. Create a Gmail App Password:"
echo "   https://myaccount.google.com/apppasswords"
echo ""
echo "2. Create a .env file in the project root with:"
echo "   EMAIL_USER=your-email@gmail.com"
echo "   EMAIL_PASSWORD=your-16-digit-app-password"
echo ""
echo "Or set environment variables:"
echo "   export EMAIL_USER='your-email@gmail.com'"
echo "   export EMAIL_PASSWORD='your-16-digit-app-password'"
echo ""

echo "✅ Setup complete!"
echo ""
echo "To start the app, run:"
echo "   ./start_app.sh"
echo ""

