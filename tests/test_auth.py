"""
Tests for authentication functionality (login, register, logout).
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import url_for


class TestAuthentication:
    """Test authentication routes and functionality."""
    
    def test_login_page_loads(self, client):
        """Test that login page loads successfully."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()
    
    def test_register_page_loads(self, client):
        """Test that register page loads successfully."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data or b'register' in response.data.lower()
    
    @patch('app.get_db_connection')
    def test_user_registration_success(self, mock_db, client):
        """Test successful user registration."""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        mock_db.return_value = mock_conn
        
        response = client.post('/register', data={
            'email': 'newuser@example.com',
            'password': 'testpassword123',
            'submit': 'Register'
        }, follow_redirects=True)
        
        # Should redirect to login page
        assert response.status_code == 200
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
    
    @patch('app.get_db_connection')
    def test_user_registration_duplicate_email(self, mock_db, client):
        """Test registration with duplicate email."""
        import psycopg2
        # Mock database connection with integrity error
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.IntegrityError("duplicate key")
        mock_db.return_value = mock_conn
        
        response = client.post('/register', data={
            'email': 'existing@example.com',
            'password': 'testpassword123',
            'submit': 'Register'
        })
        
        # Should show error message
        assert response.status_code == 200
        mock_conn.rollback.assert_called()
    
    @patch('app.get_db_connection')
    @patch('app.bcrypt')
    def test_user_login_success(self, mock_bcrypt, mock_db, client):
        """Test successful user login."""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock user data
        mock_user_data = Mock()
        mock_user_data.__getitem__ = Mock(side_effect=lambda key: {
            'id': 1,
            'email': 'test@example.com',
            'password': 'hashed_password',
            'skills': [],
            'preferred_location': None
        }.get(key))
        mock_user_data.get = Mock(side_effect=lambda key, default=None: {
            'id': 1,
            'email': 'test@example.com',
            'password': 'hashed_password',
            'skills': [],
            'preferred_location': None
        }.get(key, default))
        
        mock_cursor.fetchone.return_value = mock_user_data
        mock_cursor.close = Mock()
        mock_conn.close = Mock()
        mock_db.return_value = mock_conn
        
        # Mock bcrypt password check
        mock_bcrypt.check_password_hash.return_value = True
        
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpassword123',
            'submit': 'Login'
        }, follow_redirects=True)
        
        # Should redirect to index
        assert response.status_code == 200
        mock_bcrypt.check_password_hash.assert_called()
    
    @patch('app.get_db_connection')
    @patch('app.bcrypt')
    def test_user_login_invalid_credentials(self, mock_bcrypt, mock_db, client):
        """Test login with invalid credentials."""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_db.return_value = mock_conn
        
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword',
            'submit': 'Login'
        })
        
        # Should stay on login page with error
        assert response.status_code == 200
        assert b'Unsuccessful' in response.data or b'error' in response.data.lower()
    
    def test_logout_redirects(self, authenticated_client):
        """Test that logout redirects to login page."""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200


class TestUserModel:
    """Test User model functionality."""
    
    def test_user_initialization(self):
        """Test User object initialization."""
        from app import User
        user = User(
            id=1,
            email='test@example.com',
            skills=['Python', 'Flask'],
            email_alerts_enabled=True,
            preferred_location='India'
        )
        
        assert user.id == 1
        assert user.email == 'test@example.com'
        assert user.skills == ['Python', 'Flask']
        assert user.email_alerts_enabled is True
        assert user.preferred_location == 'India'
    
    def test_user_default_values(self):
        """Test User object with default values."""
        from app import User
        user = User(id=1, email='test@example.com')
        
        assert user.skills == []
        assert user.email_alerts_enabled is False
        assert user.preferred_location is None

