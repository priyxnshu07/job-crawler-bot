#!/bin/bash

# Job Crawler Bot - Simple Launcher for Mac
# Double-click this file to run

cd "$(dirname "$0")"

echo ""
echo "========================================"
echo "   JOB CRAWLER BOT - STARTING"
echo "========================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo ""
    echo "Please run SETUP.command first!"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Load .env if exists
if [ -f .env ]; then
    echo "Loading .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

echo ""
echo "Starting services..."
echo ""

# Start Flask
echo "[1/3] Starting Flask app..."
python app.py > flask.log 2>&1 &
FLASK_PID=$!
sleep 4

# Start Celery Worker
echo "[2/3] Starting Celery worker..."
python -m celery -A tasks worker --loglevel INFO > celery-worker.log 2>&1 &
WORKER_PID=$!
sleep 3

# Start Celery Beat
echo "[3/3] Starting Celery scheduler..."
python -m celery -A tasks beat --loglevel INFO > celery-beat.log 2>&1 &
BEAT_PID=$!
sleep 3

echo ""
echo "========================================"
echo "   APPLICATION IS RUNNING!"
echo "========================================"
echo ""
echo "Opening browser in 5 seconds..."
sleep 5
open http://127.0.0.1:5001

echo ""
echo "========================================"
echo "   HOW TO USE:"
echo "========================================"
echo ""
echo "1. Browser should open automatically"
echo "2. If not, visit: http://127.0.0.1:5001"
echo "3. Register/Login to use the app"
echo ""
echo "TO STOP:"
echo "- Press Ctrl+C in this window"
echo "- OR close this window"
echo ""
echo "Process IDs:"
echo "Flask: $FLASK_PID"
echo "Worker: $WORKER_PID"
echo "Scheduler: $BEAT_PID"
echo ""
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Wait for Ctrl+C
trap "kill $FLASK_PID $WORKER_PID $BEAT_PID 2>/dev/null; exit" INT TERM
wait

