# Quick Start: Testing & Deployment

## 🧪 Running Tests

### Option 1: Simple Test Run
```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest
```

### Option 2: With Coverage Report
```bash
# Run tests with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Option 3: Using Test Script
```bash
# Make script executable (first time only)
chmod +x scripts/run_tests.sh

# Run tests
./scripts/run_tests.sh
```

## 🐳 Docker Deployment

### Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production
```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Initialize database
docker-compose exec web python database_setup.py
```

## ✅ Environment Validation

```bash
# Validate environment variables
python scripts/validate_env.py
```

## 📊 Test Results

After running tests, you should see:
- ✅ All tests passing
- 📊 Coverage report
- 📝 Test summary

## 🚀 Next Steps

1. **Review Test Results**: Check coverage and fix any failing tests
2. **Set Up CI/CD**: Configure GitHub Actions secrets
3. **Deploy**: Follow DEPLOYMENT.md for production deployment
4. **Monitor**: Set up monitoring and logging

## 📚 Documentation

- **TESTING.md**: Detailed testing guide
- **DEPLOYMENT.md**: Production deployment guide
- **DEPLOYMENT_SUMMARY.md**: Complete summary

## 🐛 Troubleshooting

### Tests Not Running
```bash
# Install test dependencies
pip install -r requirements.txt

# Verify pytest is installed
pytest --version
```

### Docker Issues
```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs
```

### Database Connection
```bash
# Verify PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Check database setup
python database_setup.py
```

