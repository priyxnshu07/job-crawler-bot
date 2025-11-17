"""
Pytest configuration and fixtures for testing the Job Crawler application.
"""
import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Set test environment variables before importing app
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'postgresql://test_user@localhost:5432/test_job_crawler_db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/1'

from app import app, get_db_connection, load_user, User
from flask_login import FlaskLoginClient


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['LOGIN_DISABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def test_db_connection():
    """Create a mock database connection for testing."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.rowcount = 0
    
    return mock_conn, mock_cursor


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = User(
        id=1,
        email='test@example.com',
        skills=['Python', 'Flask', 'PostgreSQL'],
        email_alerts_enabled=False,
        preferred_location=None
    )
    return user


@pytest.fixture
def authenticated_client(client, mock_user):
    """Create an authenticated test client."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(mock_user.id)
        sess['_fresh'] = True
    
    # Mock load_user to return our test user
    with patch('app.load_user', return_value=mock_user):
        yield client


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        'jobid': 1,
        'title': 'Python Developer',
        'company': 'Tech Corp',
        'location': 'Remote',
        'description': 'Looking for a Python developer',
        'apply_link': 'https://example.com/job/1'
    }


@pytest.fixture
def sample_jobs_list():
    """Sample list of jobs for testing."""
    return [
        {
            'jobid': 1,
            'title': 'Python Developer',
            'company': 'Tech Corp',
            'location': 'Remote',
            'description': 'Python developer needed',
            'apply_link': 'https://example.com/job/1'
        },
        {
            'jobid': 2,
            'title': 'Senior Python Engineer',
            'company': 'AI Solutions',
            'location': 'Bangalore, India',
            'description': 'Senior Python engineer needed',
            'apply_link': 'https://example.com/job/2'
        },
        {
            'jobid': 3,
            'title': 'JavaScript Developer',
            'company': 'Web Corp',
            'location': 'New York, NY',
            'description': 'JavaScript developer needed',
            'apply_link': 'https://example.com/job/3'
        }
    ]


@pytest.fixture
def temp_upload_dir():
    """Create a temporary directory for file uploads during testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing skill extraction."""
    return """
    John Doe
    Software Engineer
    
    Skills: Python, Flask, Django, PostgreSQL, Redis, Docker, AWS
    Experience: 5 years in software development
    Education: BS in Computer Science
    """


@pytest.fixture(autouse=True)
def reset_config():
    """Reset configuration after each test."""
    yield
    # Any cleanup needed after tests

