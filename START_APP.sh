#!/bin/bash

# Job Crawler Bot - Startup Script
# This script starts all necessary services

echo "🚀 Starting Job Crawler Bot..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Load .env if present
if [ -f .env ]; then
    echo "Loading environment from .env"
    set -a
    source .env
    set +a
fi

# Check if email credentials are set
if [ -z "$EMAIL_USER" ] || [ -z "$EMAIL_PASSWORD" ]; then
    echo ""
    echo "⚠️  Email credentials not found!"
    echo ""
    echo "To get email alerts working, you need to:"
    echo "1. Get a Gmail App Password: https://myaccount.google.com/apppasswords"
    echo "2. Set these environment variables:"
    echo ""
    echo "   export EMAIL_USER='your-email@gmail.com'"
    echo "   export EMAIL_PASSWORD='your-app-password'"
    echo ""
    echo "Or edit the .env file and add:"
    echo "   EMAIL_USER=your-email@gmail.com"
    echo "   EMAIL_PASSWORD=your-app-password"
    echo ""
    read -p "Continue without email alerts? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start Redis if not running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

# Kill any existing processes
echo "Cleaning up old processes..."
pkill -f "python app.py" 2>/dev/null
pkill -f "celery -A tasks worker" 2>/dev/null
pkill -f "celery -A tasks beat" 2>/dev/null
sleep 2

# Start all services
echo ""
echo "Starting services..."
echo ""

# Terminal 1: Flask app
echo "   [1/3] Starting Flask app..."
export EMAIL_USER="${EMAIL_USER}"
export EMAIL_PASSWORD="${EMAIL_PASSWORD}"
python app.py > flask.log 2>&1 &
sleep 3

# Terminal 2: Celery worker
echo "   [2/3] Starting Celery worker..."
export EMAIL_USER="${EMAIL_USER}"
export EMAIL_PASSWORD="${EMAIL_PASSWORD}"
python -m celery -A tasks worker --loglevel INFO > celery-worker.log 2>&1 &
sleep 2

# Terminal 3: Celery beat
echo "   [3/3] Starting Celery scheduler..."
export EMAIL_USER="${EMAIL_USER}"
export EMAIL_PASSWORD="${EMAIL_PASSWORD}"
python -m celery -A tasks beat --loglevel INFO > celery-beat.log 2>&1 &
sleep 2

echo ""
echo "✅ All services started!"
echo ""
echo "📝 Logs:"
echo "   Flask:      tail -f flask.log"
echo "   Celery:     tail -f celery-worker.log"
echo "   Scheduler:  tail -f celery-beat.log"
echo ""
echo "🌐 Your app is running at: http://127.0.0.1:5001"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep script running
wait
