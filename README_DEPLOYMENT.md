# Quick Deployment Guide

## Prerequisites

- Docker and Docker Compose
- PostgreSQL and Redis (or use Docker)
- Python 3.9+ (for local development)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd jobcrawlerprototype
```

### 2. Environment Setup

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Run Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Or use the test script
./scripts/run_tests.sh
```

### 4. Validate Environment

```bash
# Validate environment variables
python scripts/validate_env.py
```

### 5. Deploy with Docker

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d

# Initialize database
docker-compose exec web python database_setup.py
```

### 6. Access Application

- Web: http://localhost:5001
- Check logs: `docker-compose logs -f`

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Tests
```bash
pytest tests/test_auth.py
pytest tests/test_routes.py
```

## CI/CD

The project includes GitHub Actions workflow that:
- Runs tests on push/PR
- Checks code quality
- Builds Docker images
- Deploys to production (configured)

## Documentation

- [TESTING.md](TESTING.md) - Testing guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
- [README.md](README.md) - Main project documentation

## Troubleshooting

### Tests Failing
1. Check database connection
2. Verify environment variables
3. Check test dependencies installed

### Docker Issues
1. Check Docker is running
2. Verify ports are available
3. Check Docker logs: `docker-compose logs`

### Database Issues
1. Verify PostgreSQL is running
2. Check database credentials
3. Run database setup: `python database_setup.py`

## Support

For issues:
1. Check logs
2. Review documentation
3. Check GitHub issues
4. Contact support

