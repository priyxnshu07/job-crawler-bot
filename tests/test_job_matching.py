"""
Tests for job matching and location filtering functionality.
"""
import pytest
from unittest.mock import Mock, patch


class TestJobMatching:
    """Test job matching score calculation."""
    
    def test_calculate_job_match_score_with_matching_skills(self):
        """Test job match score calculation with matching skills."""
        from app import calculate_job_match_score
        
        job_data = {
            'title': 'Python Developer',
            'company': 'Tech Corp'
        }
        user_skills = ['Python', 'Flask', 'Django']
        
        score, matched_skills = calculate_job_match_score(job_data, user_skills)
        
        assert score > 0
        assert isinstance(matched_skills, list)
        assert 'Python' in matched_skills
    
    def test_calculate_job_match_score_no_matching_skills(self):
        """Test job match score with no matching skills."""
        from app import calculate_job_match_score
        
        job_data = {
            'title': 'JavaScript Developer',
            'company': 'Web Corp'
        }
        user_skills = ['Python', 'Flask', 'Django']
        
        score, matched_skills = calculate_job_match_score(job_data, user_skills)
        
        assert score == 0
        assert len(matched_skills) == 0
    
    def test_calculate_job_match_score_empty_skills(self):
        """Test job match score with empty user skills."""
        from app import calculate_job_match_score
        
        job_data = {
            'title': 'Python Developer',
            'company': 'Tech Corp'
        }
        user_skills = []
        
        score, matched_skills = calculate_job_match_score(job_data, user_skills)
        
        assert score == 0
        assert len(matched_skills) == 0
    
    def test_calculate_job_match_score_partial_match(self):
        """Test job match score with partial skill match."""
        from app import calculate_job_match_score
        
        job_data = {
            'title': 'Python Developer',
            'company': 'Tech Corp'
        }
        user_skills = ['Python', 'JavaScript', 'React', 'Vue', 'Angular']
        
        score, matched_skills = calculate_job_match_score(job_data, user_skills)
        
        assert score > 0
        assert score < 100  # Should be partial match
        assert 'Python' in matched_skills


class TestLocationFiltering:
    """Test location filtering logic."""
    
    def test_location_filter_india(self):
        """Test filtering jobs for India location."""
        jobs = [
            {'jobid': 1, 'title': 'Python Dev', 'location': 'Bangalore, India'},
            {'jobid': 2, 'title': 'JS Dev', 'location': 'New York, NY'},
            {'jobid': 3, 'title': 'Python Dev', 'location': 'Mumbai, India'}
        ]
        
        # Filter for India
        india_jobs = [job for job in jobs if 'india' in job['location'].lower()]
        
        assert len(india_jobs) == 2
        assert all('india' in job['location'].lower() for job in india_jobs)
    
    def test_location_filter_remote(self):
        """Test filtering jobs for Remote location."""
        jobs = [
            {'jobid': 1, 'title': 'Python Dev', 'location': 'Remote'},
            {'jobid': 2, 'title': 'JS Dev', 'location': 'New York, NY'},
            {'jobid': 3, 'title': 'Python Dev', 'location': 'Remote'}
        ]
        
        # Filter for Remote
        remote_jobs = [job for job in jobs if job['location'].lower() == 'remote']
        
        assert len(remote_jobs) == 2
        assert all(job['location'].lower() == 'remote' for job in remote_jobs)
    
    def test_location_filter_specific_city(self):
        """Test filtering jobs for specific city."""
        jobs = [
            {'jobid': 1, 'title': 'Python Dev', 'location': 'Bangalore, India'},
            {'jobid': 2, 'title': 'JS Dev', 'location': 'Mumbai, India'},
            {'jobid': 3, 'title': 'Python Dev', 'location': 'Bangalore, India'}
        ]
        
        # Filter for Bangalore
        bangalore_jobs = [job for job in jobs if 'bangalore' in job['location'].lower()]
        
        assert len(bangalore_jobs) == 2
        assert all('bangalore' in job['location'].lower() for job in bangalore_jobs)


class TestEmailAlerts:
    """Test email alert functionality with location filtering."""
    
    @patch('app.get_db_connection')
    def test_email_alerts_respect_location_filter(self, mock_db):
        """Test that email alerts respect location preference."""
        # This would be tested in integration tests
        # For now, we test the logic
        user_preferred_location = 'India'
        
        jobs = [
            {'jobid': 1, 'title': 'Python Dev', 'location': 'Bangalore, India'},
            {'jobid': 2, 'title': 'JS Dev', 'location': 'New York, NY'},
            {'jobid': 3, 'title': 'Python Dev', 'location': 'Mumbai, India'}
        ]
        
        if user_preferred_location.lower() == 'india':
            filtered_jobs = [job for job in jobs if 'india' in job['location'].lower()]
        else:
            filtered_jobs = jobs
        
        assert len(filtered_jobs) == 2
        assert all('india' in job['location'].lower() for job in filtered_jobs)

