# 📖 How to Run Job Crawler Bot

## 🎯 Step-by-Step Instructions

### Method 1: GUI Launcher (Easiest - Recommended)

#### Step 1: Open the Launcher
- **Windows**: Double-click `launcher.py` OR right-click → "Open With" → Python
- **Mac**: Double-click `launcher.py` OR right-click → "Open With" → Python Launcher
- **Linux**: Double-click `launcher.py` OR right-click → "Open With" → Python

#### Step 2: Start the Application
1. You'll see a window with buttons
2. Click the **"▶ Start Application"** button (green button)
3. Wait for the log messages to show:
   - "✓ Flask app started"
   - "✓ Celery worker started"  
   - "✓ Celery scheduler started"
   - "✅ All services started successfully!"

#### Step 3: Open Browser
- Click the **"🌐 Open in Browser"** button (blue button)
- OR your browser will open automatically
- The app will be at: http://127.0.0.1:5001

#### Step 4: Stop When Done
- Click the **"■ Stop Application"** button (red button)
- OR close the launcher window (it will ask to stop first)

---

### Method 2: Simple Python Launcher

#### Step 1: Run the Script
- **Windows**: Double-click `run_app.py` OR right-click → "Open With" → Python
- **Mac/Linux**: Double-click `run_app.py` OR open terminal and type: `python run_app.py`

#### Step 2: Wait for Start
- You'll see messages in the console:
  - "Starting Flask app..."
  - "Starting Celery worker..."
  - "Starting Celery scheduler..."
  - "✅ Application is running!"

#### Step 3: Browser Opens
- Your browser will open automatically
- If not, visit: http://127.0.0.1:5001

#### Step 4: Stop When Done
- Press **Ctrl+C** in the terminal/console window
- OR close the window

---

### Method 3: Windows Batch File (Windows Only)

#### Step 1: Double-Click
- Double-click `START.bat`
- Three new windows will open (Flask, Worker, Scheduler)

#### Step 2: Browser Opens
- Your browser will open automatically
- App is at: http://127.0.0.1:5001

#### Step 3: Stop When Done
- Close all three windows (Flask, Worker, Scheduler)
- OR close the main window

---

### Method 4: Shell Script (Mac/Linux)

#### Step 1: Double-Click
- Double-click `start_app.sh`
- OR open terminal in the project folder and type: `./start_app.sh`

#### Step 2: Wait for Start
- See messages in terminal
- Wait for "✅ All services started!"

#### Step 3: Browser Opens
- Browser opens automatically
- OR visit: http://127.0.0.1:5001

#### Step 4: Stop When Done
- Press **Ctrl+C**
- OR close the terminal

---

## 🚀 First Time Setup (Do This Once)

If you haven't set up the project yet:

### Windows:
1. Double-click `SETUP.bat`
2. Wait for it to finish
3. Then use any method above to start

### Mac/Linux:
1. Double-click `setup.sh`
2. OR open terminal and type: `./setup.sh`
3. Wait for it to finish
4. Then use any method above to start

---

## 📧 Setting Up Email (Optional)

1. Get Gmail App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Create app password for "Mail"
   - Copy the 16-digit password

2. Create `.env` file:
   - Create a new file named `.env` (no extension)
   - Add these lines:
     ```
     EMAIL_USER=your-email@gmail.com
     EMAIL_PASSWORD=your-16-digit-password
     ```
   - Save the file

3. Restart the app

---

## ❓ Troubleshooting

**"Python not found"**
- Install Python from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

**"Virtual environment not found"**
- Run setup first (see First Time Setup above)

**"Can't open launcher.py"**
- Make sure Python is installed
- Try right-click → "Open With" → Python
- OR use terminal: `python launcher.py`

**"Port 5001 already in use"**
- Close other applications
- OR restart your computer

**"Browser didn't open"**
- Manually visit: http://127.0.0.1:5001

---

## ✅ Quick Summary

**Easiest way:**
1. Double-click `launcher.py`
2. Click "Start Application"
3. Click "Open in Browser"
4. Done!

**All methods do the same thing - just pick the one you like!**

---

## 📝 What Happens When You Start

1. **Flask App** - The web server (port 5001)
2. **Celery Worker** - Processes background jobs
3. **Celery Scheduler** - Schedules job scraping every 30 seconds
4. **Browser** - Opens automatically to http://127.0.0.1:5001

You can now:
- Register/Login
- Upload your resume
- Search for jobs
- Get personalized matches
- Receive email alerts (if configured)

---

**That's it! You're ready to go! 🎉**

