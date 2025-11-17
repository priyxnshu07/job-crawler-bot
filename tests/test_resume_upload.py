"""
Tests for resume upload and skill extraction functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import io


class TestResumeUpload:
    """Test resume upload functionality."""
    
    @patch('app.get_db_connection')
    @patch('app.current_user')
    @patch('app.allowed_file')
    @patch('app.extract_text_from_pdf')
    @patch('app.extract_skills_from_text')
    def test_upload_resume_pdf_success(self, mock_extract_skills, mock_extract_text, 
                                       mock_allowed, mock_user, mock_db, client):
        """Test successful PDF resume upload."""
        # Mock user
        mock_user.id = 1
        mock_user.is_authenticated = True
        
        # Mock database
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        
        # Mock file operations
        mock_allowed.return_value = True
        mock_extract_text.return_value = "Python Flask Django PostgreSQL"
        mock_extract_skills.return_value = ['Python', 'Flask', 'Django', 'PostgreSQL']
        
        # Create a mock file
        data = {'resume': (io.BytesIO(b'fake pdf content'), 'resume.pdf')}
        
        with patch('app.os.path.exists', return_value=True):
            with patch('app.os.remove'):
                with patch('app.os.path.join', return_value='/tmp/resume.pdf'):
                    with patch('app.secure_filename', return_value='resume.pdf'):
                        with patch('builtins.open', mock_open()):
                            with patch('app.login_required', lambda f: f):
                                response = client.post('/upload_resume', 
                                                     data=data, 
                                                     content_type='multipart/form-data',
                                                     follow_redirects=True)
                                
                                assert response.status_code == 200
                                mock_extract_skills.assert_called()
                                mock_cursor.execute.assert_called()
                                mock_conn.commit.assert_called()
    
    @patch('app.current_user')
    def test_upload_resume_no_file(self, mock_user, client):
        """Test upload resume without file."""
        mock_user.is_authenticated = True
        
        with patch('app.login_required', lambda f: f):
            response = client.post('/upload_resume', follow_redirects=True)
            assert response.status_code == 200
    
    @patch('app.current_user')
    @patch('app.allowed_file')
    def test_upload_resume_invalid_file_type(self, mock_allowed, mock_user, client):
        """Test upload resume with invalid file type."""
        mock_user.is_authenticated = True
        mock_allowed.return_value = False
        
        data = {'resume': (io.BytesIO(b'fake content'), 'resume.txt')}
        
        with patch('app.login_required', lambda f: f):
            response = client.post('/upload_resume', 
                                 data=data, 
                                 content_type='multipart/form-data',
                                 follow_redirects=True)
            assert response.status_code == 200


class TestSkillExtraction:
    """Test skill extraction from resume text."""
    
    def test_extract_skills_basic(self):
        """Test basic skill extraction."""
        from app import extract_skills_from_text
        
        text = """
        Skills: Python, Flask, Django, PostgreSQL, Redis, Docker
        Experience: Software Developer
        """
        skills = extract_skills_from_text(text)
        
        assert 'Python' in skills or 'python' in [s.lower() for s in skills]
        assert len(skills) > 0
    
    def test_extract_skills_filters_noise(self):
        """Test that skill extraction filters out noise."""
        from app import extract_skills_from_text
        
        text = """
        Worked at Globex Corp as Intern (2020-2021)
        Skills: Python, Manager, Specialist, 2024
        """
        skills = extract_skills_from_text(text)
        
        # Should not include job titles or years
        noise_terms = ['Intern', 'Manager', 'Specialist', '2024']
        for term in noise_terms:
            assert term not in skills, f"Found noise term: {term}"
    
    def test_extract_skills_empty_text(self):
        """Test skill extraction with empty text."""
        from app import extract_skills_from_text
        
        skills = extract_skills_from_text("")
        assert skills == []
    
    def test_extract_skills_no_skills(self):
        """Test skill extraction with no skills in text."""
        from app import extract_skills_from_text
        
        text = "This is a resume without any technical skills mentioned."
        skills = extract_skills_from_text(text)
        # May return empty or very few skills
        assert isinstance(skills, list)


class TestFileHandling:
    """Test file handling utilities."""
    
    def test_allowed_file_pdf(self):
        """Test that PDF files are allowed."""
        from app import allowed_file
        assert allowed_file('resume.pdf') is True
    
    def test_allowed_file_docx(self):
        """Test that DOCX files are allowed."""
        from app import allowed_file
        assert allowed_file('resume.docx') is True
    
    def test_allowed_file_txt(self):
        """Test that TXT files are not allowed."""
        from app import allowed_file
        assert allowed_file('resume.txt') is False
    
    def test_allowed_file_case_insensitive(self):
        """Test that file extension check is case insensitive."""
        from app import allowed_file
        assert allowed_file('resume.PDF') is True
        assert allowed_file('resume.DOCX') is True

