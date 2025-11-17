#!/bin/bash
# Deployment script for Job Crawler application

set -e

echo "=========================================="
echo "Job Crawler Deployment Script"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model if not present
echo -e "${GREEN}Checking spaCy model...${NC}"
python -m spacy download en_core_web_sm 2>/dev/null || echo "spaCy model already installed or download failed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your configuration${NC}"
    echo -e "${YELLOW}   Required: SECRET_KEY, DATABASE_URL, REDIS_URL${NC}"
    read -p "Press Enter to continue after editing .env file..."
fi

# Validate environment
echo -e "${GREEN}Validating environment...${NC}"
python scripts/validate_env.py || {
    echo -e "${RED}Environment validation failed. Please fix .env file.${NC}"
    exit 1
}

# Run database setup
echo -e "${GREEN}Setting up database...${NC}"
python database_setup.py

# Create uploads directory
echo -e "${GREEN}Creating uploads directory...${NC}"
mkdir -p uploads
chmod 755 uploads

# Run tests (optional)
read -p "Run tests before deployment? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Running tests...${NC}"
    pytest tests/ -v --tb=short || {
        echo -e "${YELLOW}⚠️  Some tests failed, but continuing deployment...${NC}"
    }
fi

# Check if services are running
echo -e "${GREEN}Checking services...${NC}"

# Check PostgreSQL
if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not running${NC}"
    echo -e "${YELLOW}   Please start PostgreSQL: brew services start postgresql${NC}"
    exit 1
fi

# Check Redis
if redis-cli ping >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis is not running${NC}"
    echo -e "${YELLOW}   Please start Redis: brew services start redis${NC}"
    exit 1
fi

# Start Celery worker in background
echo -e "${GREEN}Starting Celery worker...${NC}"
if pgrep -f "celery.*worker" > /dev/null; then
    echo -e "${YELLOW}⚠️  Celery worker already running${NC}"
else
    celery -A tasks worker --loglevel=INFO > celery-worker.log 2>&1 &
    echo $! > celery-worker.pid
    echo -e "${GREEN}✅ Celery worker started (PID: $(cat celery-worker.pid))${NC}"
fi

# Start Celery beat in background
echo -e "${GREEN}Starting Celery beat...${NC}"
if pgrep -f "celery.*beat" > /dev/null; then
    echo -e "${YELLOW}⚠️  Celery beat already running${NC}"
else
    celery -A tasks beat --loglevel=INFO > celery-beat.log 2>&1 &
    echo $! > celery-beat.pid
    echo -e "${GREEN}✅ Celery beat started (PID: $(cat celery-beat.pid))${NC}"
fi

# Start Flask application
echo -e "${GREEN}Starting Flask application...${NC}"
echo -e "${GREEN}=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "🌐 Application will be available at:"
echo "   http://127.0.0.1:5001"
echo ""
echo "📝 Logs:"
echo "   Flask:      tail -f app.log"
echo "   Worker:     tail -f celery-worker.log"
echo "   Beat:       tail -f celery-beat.log"
echo ""
echo "⏹️  To stop services:"
echo "   ./scripts/stop_deployment.sh"
echo ""
echo "🚀 Starting Flask application..."
echo "   Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Run Flask app
python app.py

