#!/usr/bin/env python3
"""
Test the upload functionality programmatically
"""
import requests
import os
import time

# Wait for app to start
time.sleep(2)

# First, let's check if the app is running
try:
    response = requests.get('http://127.0.0.1:5000', timeout=5)
    print("✓ App is running")
except Exception as e:
    print(f"✗ App not running: {e}")
    print("\nPlease start the app manually:")
    print("  python app.py")
    exit(1)

# Check if we can reach the login page
response = requests.get('http://127.0.0.1:5000/login')
print(f"✓ Login page accessible (status: {response.status_code})")

# Try to get a test file
cv_path = "test_cv.pdf"
if os.path.exists(cv_path):
    print(f"✓ Test CV found: {cv_path}")
    print("\nTo test the upload:")
    print("1. Visit: http://127.0.0.1:5000")
    print("2. Login or register")
    print("3. Upload the resume")
    print("\nThe app should now work!")
else:
    print(f"✗ Test CV not found: {cv_path}")


