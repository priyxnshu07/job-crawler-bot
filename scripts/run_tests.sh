#!/bin/bash
# Test runner script for the Job Crawler application

set -e

echo "=========================================="
echo "Running Job Crawler Test Suite"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install/update test dependencies
echo -e "\n${GREEN}Installing test dependencies...${NC}"
pip install -q -r requirements.txt

# Run flake8 linting
echo -e "\n${GREEN}Running flake8 linting...${NC}"
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics || true

# Run pytest with coverage
echo -e "\n${GREEN}Running pytest with coverage...${NC}"
pytest tests/ -v --cov=app --cov=tasks --cov-report=html --cov-report=term --cov-report=xml

# Check coverage threshold (optional)
COVERAGE_THRESHOLD=70
COVERAGE=$(coverage report | tail -1 | awk '{print $NF}' | sed 's/%//')

echo -e "\n${GREEN}Coverage: ${COVERAGE}%${NC}"

if (( $(echo "$COVERAGE < $COVERAGE_THRESHOLD" | bc -l) )); then
    echo -e "${RED}Warning: Coverage is below ${COVERAGE_THRESHOLD}%${NC}"
else
    echo -e "${GREEN}✅ Coverage is above ${COVERAGE_THRESHOLD}%${NC}"
fi

echo -e "\n${GREEN}=========================================="
echo "Test suite completed!"
echo "==========================================${NC}"

# Open coverage report in browser (optional)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open htmlcov/index.html 2>/dev/null || true
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open htmlcov/index.html 2>/dev/null || true
fi

