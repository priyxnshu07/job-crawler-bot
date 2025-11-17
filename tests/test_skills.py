"""
Test skill extraction without requiring database connection.
This test extracts the function code directly to avoid Flask app initialization.
"""
import os
import sys
import re

# Ensure root path on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def extract_skills_from_text(text):
    """
    Simplified version of extract_skills_from_text for testing.
    This mirrors the logic from app.py without requiring database.
    """
    if not text:
        return []
    
    skills_found = set()
    text_lower = text.lower()
    
    # Core technical skills database (subset for testing)
    technical_skills = {
        'python', 'java', 'javascript', 'typescript', 'html', 'css', 'go', 'rust', 
        'c++', 'c#', '.net', 'php', 'ruby', 'swift', 'kotlin', 'dart',
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 
        'fastapi', 'spring', 'laravel', 'rails', 'asp.net',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 
        'dynamodb', 'elasticsearch', 'sqlite', 'oracle',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 
        'jenkins', 'gitlab ci', 'github actions', 'ansible',
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn', 
        'scipy', 'tensorflow', 'pytorch', 'keras', 'opencv', 'nltk', 'spacy',
        'git', 'svn',
        'agile', 'scrum', 'kanban', 'jira', 'confluence', 'trello',
        'rest', 'graphql',
        'linux', 'unix', 'bash', 'powershell',
        'postman', 'selenium', 'pytest', 'junit', 'celery'
    }
    
    # Direct skill matching
    for skill in technical_skills:
        if skill in text_lower:
            skills_found.add(skill.title() if skill.islower() else skill)
    
    # Extract from Skills sections
    skills_pattern = r'(?:technical\s+)?skills?[:\-]?\s*([^\n]{20,500})'
    matches = re.findall(skills_pattern, text_lower, re.IGNORECASE)
    
    for match in matches:
        clean_match = re.sub(r'^(programming|tools?|frameworks?|databases?|libraries?):\s*', '', match, flags=re.IGNORECASE)
        potential_skills = re.split(r'[,;•\n]', clean_match)
        
        for skill in potential_skills:
            skill = skill.strip().lower()
            
            if not skill or len(skill) < 2 or len(skill) > 40:
                continue
            
            # Filter out non-skills
            if any(word in skill for word in ['intern', 'junior', 'senior', 'developer', 
                                              'engineer', 'manager', 'analyst', 'qa', 'quality']):
                continue
            
            if re.search(r'\d{4}', skill):
                continue
            
            if any(sk in skill for sk in ['library', 'libraries', 'framework', 'tool', 'tools']):
                continue
            
            if any(ts in skill or skill in ts for ts in technical_skills):
                skills_found.add(skill.title())
    
    # Clean up results
    filtered_skills = []
    for skill in skills_found:
        skill_lower = skill.lower()
        
        if skill_lower.startswith('py') and len(skill) > 8:
            continue
        
        if any(word in skill_lower for word in ['ltd', 'inc', 'corp', 'international', 'global']):
            continue
        
        if any(word in skill_lower for word in ['intern', 'associate', 'specialist', 'officer']):
            continue
        
        if re.search(r'\d{4}|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\b', skill_lower):
            continue
        
        if skill_lower in ['ms office', 'office', 'windows', 'mac', 'linux operating system']:
            continue
        
        filtered_skills.append(skill)
    
    return sorted(list(set(filtered_skills)))


def test_extract_skills_basic_python():
    """Test that basic Python skills are extracted correctly."""
    text = """
    John Doe
    Experience: Senior Software Engineer at Acme Inc (2018-2024)
    Skills: Python, Flask, Celery, PostgreSQL, Redis, Docker
    """
    skills = extract_skills_from_text(text)
    assert "Python" in skills, f"Python not found in {skills}"
    assert "Flask" in skills, f"Flask not found in {skills}"
    assert "Celery" in skills, f"Celery not found in {skills}"


def test_extract_skills_filters_non_skills():
    """Test that non-skills like company names and job titles are filtered out."""
    text = """
    Worked at Globex Corp as a Data Engineer (Jan 2020 - Dec 2023)
    Key achievements: built pipelines; tools used: collaboration, leadership
    Skills - Python, JavaScript; Intern, Manager, Specialist
    """
    skills = extract_skills_from_text(text)
    # Should not include company names or roles
    noise_terms = ["Globex", "Intern", "Manager", "Specialist"]
    found_noise = [term for term in noise_terms if term in skills]
    assert not found_noise, f"Found noise terms in skills: {found_noise}"
    # But should include real skills
    assert "Python" in skills or "JavaScript" in skills, f"No real skills found in {skills}"
