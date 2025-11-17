#!/bin/bash
# Setup script for the job crawler prototype

echo "Setting up job crawler prototype environment..."

# Activate virtual environment
source venv/bin/activate

# Install/upgrade all requirements
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy English model..."
python -m spacy download en_core_web_sm

echo "Setup complete!"
echo ""
echo "To start the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start Redis: redis-server (if not running)"
echo "3. Start Celery worker: celery -A tasks worker --loglevel=info"
echo "4. Start Flask app: python app.py"

