# Testing Guide

This document describes how to run tests for the Job Crawler application.

## Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=tasks --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::TestAuthentication::test_login_page_loads
```

### Using the Test Script

```bash
# Run the test script
./scripts/run_tests.sh
```

This script will:
1. Check virtual environment
2. Install dependencies
3. Run flake8 linting
4. Run pytest with coverage
5. Display coverage report
6. Open HTML coverage report in browser

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest configuration and fixtures
├── test_auth.py         # Authentication tests
├── test_routes.py       # Route tests
├── test_resume_upload.py # Resume upload tests
├── test_job_matching.py # Job matching tests
└── test_skills.py       # Skill extraction tests
```

## Test Categories

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Fast execution
- High coverage

### Integration Tests
- Test component interactions
- Use test database
- Test API endpoints
- Test database operations

## Fixtures

### Available Fixtures

- `client`: Flask test client
- `mock_user`: Mock user object
- `authenticated_client`: Authenticated test client
- `test_db_connection`: Mock database connection
- `sample_job_data`: Sample job data
- `sample_jobs_list`: List of sample jobs
- `temp_upload_dir`: Temporary directory for uploads
- `sample_resume_text`: Sample resume text

## Coverage

### Coverage Goals

- Overall coverage: > 70%
- Critical paths: > 90%
- New code: > 80%

### Viewing Coverage

```bash
# Generate HTML report
pytest --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html
```

## Mocking

### Database Mocking

```python
@patch('app.get_db_connection')
def test_example(mock_db):
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn
    # Test code
```

### User Authentication Mocking

```python
@patch('app.current_user')
def test_example(mock_user):
    mock_user.id = 1
    mock_user.is_authenticated = True
    # Test code
```

## Continuous Integration

Tests are automatically run on:
- Push to main branch
- Pull requests
- Scheduled runs

See `.github/workflows/ci.yml` for CI configuration.

## Writing Tests

### Test Naming

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test

```python
def test_example_function():
    """Test that example function works correctly."""
    result = example_function("input")
    assert result == "expected_output"
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Clear test names** that describe what is being tested
3. **Arrange-Act-Assert** pattern
4. **Mock external dependencies**
5. **Test edge cases**
6. **Test error conditions**

## Debugging Tests

### Verbose Output

```bash
pytest -v
```

### Print Statements

```bash
pytest -s
```

### Debugger

```bash
pytest --pdb
```

### Specific Test

```bash
pytest tests/test_auth.py::TestAuthentication::test_login_page_loads -v
```

## Common Issues

### Import Errors

Make sure the project root is in Python path:
```python
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
```

### Database Connection Errors

Use mocks for database connections in unit tests:
```python
@patch('app.get_db_connection')
def test_example(mock_db):
    # Mock database
```

### Authentication Errors

Mock the current_user:
```python
@patch('app.current_user')
def test_example(mock_user):
    mock_user.is_authenticated = True
```

## Test Data

### Sample Data

Use fixtures for consistent test data:
- `sample_job_data`: Single job
- `sample_jobs_list`: List of jobs
- `sample_resume_text`: Resume text

### Test Database

For integration tests, use a test database:
```python
@pytest.fixture
def test_db():
    # Create test database
    # Run migrations
    # Yield database
    # Cleanup
```

## Performance Testing

### Load Testing

Use tools like:
- Apache Bench
- Locust
- Artillery

### Example

```bash
# Install Locust
pip install locust

# Run load test
locust -f tests/load_test.py
```

## Security Testing

### Security Checks

1. **SQL Injection**: Test all database queries
2. **XSS**: Test all user inputs
3. **CSRF**: Test form submissions
4. **Authentication**: Test access controls
5. **Authorization**: Test permission checks

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Flask testing](https://flask.palletsprojects.com/en/2.3.x/testing/)
- [Mock documentation](https://docs.python.org/3/library/unittest.mock.html)

