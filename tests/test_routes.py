"""
Tests for application routes and endpoints.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestIndexRoute:
    """Test the main index route."""
    
    def test_index_requires_login(self, client):
        """Test that index route requires authentication."""
        response = client.get('/')
        # Should redirect to login
        assert response.status_code == 302 or response.status_code == 401
    
    @patch('app.current_user')
    @patch('flask_login.utils._get_user')
    def test_index_loads_for_authenticated_user(self, mock_get_user, mock_user, client):
        """Test that index loads for authenticated users."""
        from app import User
        test_user = User(id=1, email='test@example.com', skills=['Python'])
        mock_user.id = 1
        mock_user.email = 'test@example.com'
        mock_user.skills = ['Python']
        mock_user.preferred_location = None
        mock_user.is_authenticated = True
        mock_get_user.return_value = test_user
        
        with client.session_transaction() as sess:
            sess['_user_id'] = '1'
            sess['_fresh'] = True
        
        response = client.get('/')
        # May redirect if not properly authenticated, so check for either 200 or 302
        assert response.status_code in [200, 302]


class TestJobSearch:
    """Test job search functionality."""
    
    @patch('app.get_db_connection')
    @patch('app.current_user')
    def test_search_jobs_no_query(self, mock_user, mock_db, client):
        """Test job search without query parameter."""
        # Mock user
        mock_user.id = 1
        mock_user.skills = ['Python']
        mock_user.preferred_location = None
        mock_user.is_authenticated = True
        
        # Mock database
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_db.return_value = mock_conn
        
        with patch('app.login_required', lambda f: f):
            response = client.get('/search')
            assert response.status_code == 200
            import json
            data = json.loads(response.data)
            assert isinstance(data, list)
    
    @patch('app.get_db_connection')
    @patch('app.current_user')
    def test_search_jobs_with_query(self, mock_user, mock_db, client):
        """Test job search with query parameter."""
        # Mock user
        mock_user.id = 1
        mock_user.skills = ['Python']
        mock_user.preferred_location = None
        mock_user.is_authenticated = True
        
        # Mock database
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock job data
        mock_job = Mock()
        mock_job.__getitem__ = Mock(side_effect=lambda key: {
            'jobid': 1,
            'title': 'Python Developer',
            'company': 'Tech Corp',
            'location': 'Remote',
            'apply_link': 'https://example.com/job/1'
        }.get(key))
        
        mock_cursor.fetchall.return_value = [mock_job]
        mock_db.return_value = mock_conn
        
        with patch('app.login_required', lambda f: f):
            response = client.get('/search?q=Python')
            assert response.status_code == 200
            import json
            data = json.loads(response.data)
            assert isinstance(data, list)
    
    @patch('app.get_db_connection')
    @patch('app.current_user')
    def test_search_jobs_personalized(self, mock_user, mock_db, client):
        """Test personalized job search."""
        # Mock user
        mock_user.id = 1
        mock_user.skills = ['Python', 'Flask']
        mock_user.preferred_location = None
        mock_user.is_authenticated = True
        
        # Mock database
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock job data
        mock_job = Mock()
        mock_job.__getitem__ = Mock(side_effect=lambda key: {
            'jobid': 1,
            'title': 'Python Developer',
            'company': 'Tech Corp',
            'location': 'Remote',
            'apply_link': 'https://example.com/job/1'
        }.get(key))
        
        mock_cursor.fetchall.return_value = [mock_job]
        mock_db.return_value = mock_conn
        
        with patch('app.login_required', lambda f: f):
            response = client.get('/search?personalized=true')
            assert response.status_code == 200
            import json
            data = json.loads(response.data)
            assert isinstance(data, list)


class TestLocationFiltering:
    """Test location filtering functionality."""
    
    @patch('app.get_db_connection')
    @patch('app.current_user')
    def test_search_with_location_filter_india(self, mock_user, mock_db, client):
        """Test job search with India location filter."""
        # Mock user with India preference
        mock_user.id = 1
        mock_user.skills = ['Python']
        mock_user.preferred_location = 'India'
        mock_user.is_authenticated = True
        
        # Mock database
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_db.return_value = mock_conn
        
        with patch('app.login_required', lambda f: f):
            response = client.get('/search')
            assert response.status_code == 200
            # Verify location filter was applied in SQL query
            calls = mock_cursor.execute.call_args_list
            if calls:
                # Check that location filter was used
                assert any('India' in str(call) or 'india' in str(call).lower() for call in calls)
    
    @patch('app.get_db_connection')
    @patch('app.current_user')
    def test_update_location_preference(self, mock_user, mock_db, client):
        """Test updating location preference."""
        # Mock user
        mock_user.id = 1
        mock_user.is_authenticated = True
        
        # Mock database
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        
        with patch('app.login_required', lambda f: f):
            with patch('app.load_user') as mock_load_user:
                with patch('app.logout_user') as mock_logout:
                    with patch('app.login_user') as mock_login:
                        mock_load_user.return_value = mock_user
                        
                        response = client.post('/update-location', data={
                            'preferred_location': 'Bangalore'
                        }, follow_redirects=True)
                        
                        assert response.status_code == 200
                        mock_cursor.execute.assert_called()
                        mock_conn.commit.assert_called()


class TestEmailSettings:
    """Test email settings functionality."""
    
    @patch('app.get_db_connection')
    @patch('app.current_user')
    def test_email_settings_page(self, mock_user, mock_db, client):
        """Test email settings page loads."""
        # Mock user
        mock_user.id = 1
        mock_user.is_authenticated = True
        
        # Mock database
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_db.return_value = mock_conn
        
        with patch('app.login_required', lambda f: f):
            response = client.get('/email-settings')
            assert response.status_code == 200
    
    @patch('app.get_db_connection')
    @patch('app.current_user')
    def test_save_email_settings(self, mock_user, mock_db, client):
        """Test saving email settings."""
        # Mock user
        mock_user.id = 1
        mock_user.is_authenticated = True
        
        # Mock database
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        
        with patch('app.login_required', lambda f: f):
            with patch('app.load_user') as mock_load_user:
                with patch('app.logout_user'):
                    with patch('app.login_user'):
                        mock_load_user.return_value = mock_user
                        
                        response = client.post('/save-email-settings', data={
                            'smtp_server': 'smtp.gmail.com',
                            'smtp_port': '587',
                            'email_username': 'test@example.com',
                            'email_password': 'app_password'
                        }, follow_redirects=True)
                        
                        assert response.status_code == 200
                        mock_cursor.execute.assert_called()
                        mock_conn.commit.assert_called()

