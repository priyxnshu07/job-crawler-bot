# Resume Parser Troubleshooting Guide

## The Problem
You've been facing issues with `pyresparser` - this is a common problem because `pyresparser` has many complex dependencies that often conflict or break.

## The Solution
I've replaced `pyresparser` with a more reliable approach using:
- **PyPDF2** for PDF reading
- **python-docx** for DOCX files
- **spaCy** for named entity recognition (optional but recommended)

## Quick Fix Steps

### 1. Clean and Rebuild Your Environment

```bash
# Deactivate if currently active
deactivate

# Remove old virtual environment
rm -rf venv

# Create fresh virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 2. Test Your Environment

```bash
python test_resume_parser.py
```

This will check if all dependencies are properly installed.

### 3. Start Your Application

```bash
# In terminal 1: Start Redis
redis-server

# In terminal 2: Start Celery worker
celery -A tasks worker --loglevel=info

# In terminal 3: Start Flask app
python app.py
```

## What Changed

### In `app.py`:
- Removed `pyresparser` dependency
- Added custom PDF reading with `PyPDF2`
- Added custom DOCX reading with `python-docx`
- Added robust skill extraction using:
  - Keyword matching (80+ common technical skills)
  - Pattern matching for "Skills:" sections
  - spaCy NER (if available)

### In `requirements.txt`:
- Removed: `pyresparser`, `nltk`, `pdfminer.six`, `docx2txt`, `Wand`
- Kept: `spacy`, `PyPDF2`, `python-docx`
- Added version constraints for stability

## Common Issues and Solutions

### Issue: "spaCy model not found"
**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: "No module named 'PyPDF2'"
**Solution:**
```bash
pip install PyPDF2
```

### Issue: "No module named 'docx'"
**Solution:**
```bash
pip install python-docx
```

### Issue: "Cannot read PDF file"
**Possible reasons:**
1. PDF is corrupted or encrypted
2. PDF contains only images (OCR needed)
3. File extension is wrong

**Solution:** Make sure your PDF is a text-based PDF, not scanned images.

### Issue: "Could not extract any skills"
**Possible reasons:**
1. Resume doesn't mention technical skills
2. Skills are written in uncommon ways

**Solution:** 
- Make sure your resume mentions specific technologies (Python, Java, React, etc.)
- The parser looks for these keywords and patterns

## Testing with Your Own Resume

1. Save your resume as PDF or DOCX
2. Upload via the web interface
3. Check the extracted skills in your profile
4. If no skills found, review what was extracted and improve your resume's keyword usage

## The New Parsing Approach

The new parser:
1. **Extracts text** from PDF/DOCX files using reliable libraries
2. **Searches for keywords** - 80+ common technical skills
3. **Uses pattern matching** to find skills sections
4. **Optionally uses spaCy** for named entity recognition
5. **Returns a clean list** of skills

## Benefits of New Approach

✅ **More reliable** - fewer dependencies to break  
✅ **Better error messages** - you'll know exactly what went wrong  
✅ **More maintainable** - code is easier to understand and debug  
✅ **Faster** - no complex parsing pipelines  
✅ **More flexible** - easy to add new skills or patterns

## Still Having Issues?

Run the test script and share the output:
```bash
python test_resume_parser.py
```

Also check the Flask console output when you try to upload a resume - it will show detailed error messages.

