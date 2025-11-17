#!/bin/bash

echo "🛑 Stopping Job Crawler Bot..."

pkill -f "python app.py"
pkill -f "celery -A tasks worker"
pkill -f "celery -A tasks beat"
pkill -f "redis-server"

echo "✅ All services stopped!"

