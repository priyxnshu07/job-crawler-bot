#!/bin/bash
# Stop deployment script for Job Crawler application

echo "=========================================="
echo "Stopping Job Crawler Services"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Stop Celery worker
if [ -f "celery-worker.pid" ]; then
    PID=$(cat celery-worker.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}Stopping Celery worker (PID: $PID)...${NC}"
        kill $PID
        rm celery-worker.pid
        echo -e "${GREEN}✅ Celery worker stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  Celery worker not running${NC}"
        rm celery-worker.pid
    fi
else
    # Try to find and kill by process name
    pkill -f "celery.*worker" && echo -e "${GREEN}✅ Celery worker stopped${NC}" || echo -e "${YELLOW}⚠️  Celery worker not found${NC}"
fi

# Stop Celery beat
if [ -f "celery-beat.pid" ]; then
    PID=$(cat celery-beat.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}Stopping Celery beat (PID: $PID)...${NC}"
        kill $PID
        rm celery-beat.pid
        echo -e "${GREEN}✅ Celery beat stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  Celery beat not running${NC}"
        rm celery-beat.pid
    fi
else
    # Try to find and kill by process name
    pkill -f "celery.*beat" && echo -e "${GREEN}✅ Celery beat stopped${NC}" || echo -e "${YELLOW}⚠️  Celery beat not found${NC}"
fi

# Stop Flask app (if running in background)
pkill -f "python.*app.py" && echo -e "${GREEN}✅ Flask application stopped${NC}" || echo -e "${YELLOW}⚠️  Flask application not found${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "✅ All services stopped"
echo "==========================================${NC}"

