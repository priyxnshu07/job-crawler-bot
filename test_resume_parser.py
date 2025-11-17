#!/usr/bin/env python3
"""
Test script to verify resume parsing functionality.
Run this to check if the environment is set up correctly.
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import spacy
        print("✓ spaCy imported successfully")
    except ImportError as e:
        print(f"✗ spaCy import failed: {e}")
        return False
    
    try:
        import PyPDF2
        print("✓ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"✗ PyPDF2 import failed: {e}")
        return False
    
    try:
        import docx
        print("✓ python-docx imported successfully")
    except ImportError as e:
        print(f"✗ python-docx import failed: {e}")
        return False
    
    try:
        nlp = spacy.load('en_core_web_sm')
        print("✓ spaCy model 'en_core_web_sm' loaded successfully")
    except OSError:
        print("⚠ spaCy model 'en_core_web_sm' not found")
        print("  Run: python -m spacy download en_core_web_sm")
    
    return True

def test_pdf_reading():
    """Test PDF reading capability."""
    print("\nTesting PDF reading...")
    
    try:
        from PyPDF2 import PdfReader
        print("✓ PDF reading module available")
        return True
    except Exception as e:
        print(f"✗ PDF reading failed: {e}")
        return False

def test_docx_reading():
    """Test DOCX reading capability."""
    print("\nTesting DOCX reading...")
    
    try:
        import docx
        print("✓ DOCX reading module available")
        return True
    except Exception as e:
        print(f"✗ DOCX reading failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Resume Parser Environment Test")
    print("=" * 50)
    print()
    
    all_passed = True
    
    if not test_imports():
        all_passed = False
    
    if not test_pdf_reading():
        all_passed = False
    
    if not test_docx_reading():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed! Your environment is ready.")
    else:
        print("✗ Some tests failed. Please install missing dependencies.")
        print("\nTo fix issues, run:")
        print("  pip install -r requirements.txt")
        print("  python -m spacy download en_core_web_sm")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())

