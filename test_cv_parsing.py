#!/usr/bin/env python3
"""
Test script to parse the user's CV and see what happens.
"""
import sys
import os

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyPDF2 import PdfReader
import docx

def extract_text_from_pdf(filepath):
    """Extract text from PDF file."""
    try:
        text = ""
        reader = PdfReader(filepath)
        print(f"✓ PDF opened successfully")
        print(f"  Pages: {len(reader.pages)}")
        for page in reader.pages:
            page_text = page.extract_text()
            text += page_text
            print(f"  Page text length: {len(page_text)} chars")
        return text
    except Exception as e:
        print(f"✗ Error reading PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return ""

def extract_skills_from_text(text):
    """Extract technical skills from resume text with better filtering."""
    if not text:
        return []
    
    import re
    skills_found = set()
    text_lower = text.lower()
    
    # Comprehensive technical skills database
    technical_skills = {
        'python', 'java', 'javascript', 'typescript', 'html', 'css', 'go', 'rust', 
        'c++', 'c#', '.net', 'php', 'ruby', 'swift', 'kotlin',
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 
        'spring', 'laravel', 'fastapi',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 
        'elasticsearch', 'oracle',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 
        'jenkins', 'gitlab ci', 'github actions', 'ansible',
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn', 
        'scipy', 'tensorflow', 'pytorch', 'keras', 'opencv', 'nltk', 'spaCy',
        'machine learning', 'deep learning', 'neural networks',
        'computer vision', 'nlp',
        'git', 'svn',
        'agile', 'scrum', 'kanban', 'jira', 'confluence', 'trello',
        'rest', 'graphql', 'rest api',
        'linux', 'unix', 'bash', 'powershell', 'shell scripting',
        'postman', 'selenium', 'pytest', 'junit'
    }
    
    for skill in technical_skills:
        if skill in text_lower:
            skills_found.add(skill.title() if skill.islower() else skill)
    
    # Extract from Skills section
    skills_pattern = r'(?:technical\s+)?skills?[:\-]?\s*([^\n]{20,500})'
    matches = re.findall(skills_pattern, text_lower, re.IGNORECASE)
    
    for match in matches:
        clean_match = re.sub(r'^(programming|tools?|frameworks?|databases?|libraries?):\s*', '', match, flags=re.IGNORECASE)
        potential_skills = re.split(r'[,;•\n]', clean_match)
        
        for skill in potential_skills:
            skill = skill.strip().lower()
            
            if not skill or len(skill) < 2 or len(skill) > 40:
                continue
            
            if any(word in skill for word in ['intern', 'junior', 'senior', 'developer', 
                                                'engineer', 'manager', 'analyst']):
                continue
            
            if re.search(r'\d{4}', skill):
                continue
            
            if any(ts in skill or skill in ts for ts in technical_skills):
                skills_found.add(skill.title())
    
    # Clean up results
    filtered_skills = []
    for skill in skills_found:
        skill_lower = skill.lower()
        
        if skill_lower.startswith('py') and len(skill) > 8:
            continue
        
        if any(word in skill_lower for word in ['ltd', 'inc', 'corp']):
            continue
        
        if any(word in skill_lower for word in ['intern', 'associate', 'specialist']):
            continue
        
        if re.search(r'\d{4}', skill_lower):
            continue
        
        filtered_skills.append(skill)
    
    return sorted(list(set(filtered_skills)))

def main():
    cv_path = "test_cv.pdf"
    
    if not os.path.exists(cv_path):
        print(f"✗ CV file not found: {cv_path}")
        return 1
    
    print("=" * 60)
    print("Testing CV Parsing")
    print("=" * 60)
    print(f"\nFile: {cv_path}")
    
    # Extract text
    text = extract_text_from_pdf(cv_path)
    print(f"\n✓ Extracted {len(text)} characters of text")
    
    if not text:
        print("\n✗ No text extracted from PDF!")
        print("  This might be an image-based PDF. Try converting to text-based PDF.")
        return 1
    
    # Show first 200 chars of extracted text
    print(f"\nFirst 200 characters of extracted text:")
    print("-" * 60)
    print(text[:200] + "...")
    print("-" * 60)
    
    # Extract skills
    skills = extract_skills_from_text(text)
    
    print(f"\n✓ Found {len(skills)} skills:")
    if skills:
        for i, skill in enumerate(skills, 1):
            print(f"  {i}. {skill}")
    else:
        print("  No skills detected. This might mean:")
        print("  - Your CV doesn't use common technology keywords")
        print("  - The skills section is formatted differently")
        print("  - Add skills manually or update your resume with standard tech names")
    
    return 0 if skills else 1

if __name__ == '__main__':
    sys.exit(main())


