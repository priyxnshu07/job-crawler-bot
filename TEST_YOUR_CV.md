# Testing Your CV Upload

## ✅ Status

Your Flask app is now running at: **http://127.0.0.1:5000**

## 🎯 Testing Steps

### Step 1: Access the App
Open your browser and go to:
```
http://127.0.0.1:5000
```

### Step 2: Login or Register
- If you don't have an account, register first
- If you have an account, login

### Step 3: Upload Your Resume
1. Once logged in, you'll see the main dashboard
2. Scroll to the "Your Profile" section
3. Click "Choose File" and select your CV (PDF or DOCX)
4. Click "Upload Resume"
5. Wait for the processing to complete

### Step 4: Check Results
- You should see a success message
- Your extracted skills will appear in the "Your Extracted Skills" section

## 🔍 What Skills Will Be Detected?

Based on your CV (`PRIYANSHU_PARASHARCV.pdf`), we tested it and found these 25 skills:

1. Python
2. C++
3. Go
4. SQL
5. MySQL
6. PostgreSQL
7. NumPy
8. Pandas
9. Matplotlib
10. Scikit-Learn
11. Machine Learning
12. AI
13. NLTK
14. Jira
15. MS Office
16. Arduino IDE
17. Keil µVision
18. Google Colab
19. PostgreSQL (Basics)
20. And more...

## ❌ If It Doesn't Work

### Check the Console Output
Look at the terminal where Flask is running (or check `app.log` file). You'll see detailed debugging information like:

```
Extracted 2313 characters from resume
First 500 chars: Priyanshu Parashar...
Extracted 25 skills: ['Python', 'C++', 'Go', ...]
```

### Common Issues

#### Issue: "No file part"
**Solution:** Make sure you're actually selecting a file before clicking upload

#### Issue: "Could not extract any skills"
**Solution:** Your CV might not use standard technology names. Try updating your resume with more specific keywords.

#### Issue: "Error reading PDF"
**Possible causes:**
- PDF is password protected
- PDF is image-only (scanned document)
- PDF is corrupted

**Solution:** Try creating a new PDF from your source document (Word, Google Docs, etc.)

#### Issue: Connection refused
**Solution:** Make sure Flask is running:
```bash
source venv/bin/activate
python app.py
```

## 🐛 Debug Mode

I've added detailed debugging to the code. When you upload a file, you'll see in the console:
- How many characters were extracted
- The first 500 characters of text
- How many skills were found
- The list of extracted skills

This will help us identify exactly where the problem is.

## 📝 Manual Testing

You can also test the parsing logic directly:

```bash
# Copy your CV to test_cv.pdf
cp "/Users/priyanshuparashar/Documents/PRIYANSHU_PARASHARCV.pdf" test_cv.pdf

# Run the test script
python test_cv_parsing.py
```

This will show you:
- Whether the PDF can be read
- What text is extracted
- What skills are detected

## 🎬 Next Steps

1. **Visit the app** at http://127.0.0.1:5000
2. **Try uploading your resume**
3. **Check the console** for debugging output
4. **Share any error messages** you see

## 💡 Tips for Best Results

- Use **text-based PDFs** (not scanned images)
- Include specific technology names in your skills section
- Use standard names (Python not Python3, JavaScript not JS)
- Keep your resume updated with current skills

## 🆘 Still Having Issues?

If you're still facing problems:
1. Check the Flask console output (or `app.log` file)
2. Copy any error messages you see
3. Check `test_cv_parsing.py` output to see if basic parsing works

The app is now more robust and will give you detailed error messages to help debug any issues.


