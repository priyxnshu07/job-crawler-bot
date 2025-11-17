#!/bin/bash
# Build script for Render deployment

set -e

echo "Building Job Crawler application..."

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create necessary directories
mkdir -p uploads
chmod 755 uploads

echo "Build complete!"

