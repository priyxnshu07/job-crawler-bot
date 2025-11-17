# 🪟 Windows Instructions - Job Crawler Bot

## 🚀 Quick Start (3 Steps)

### Step 1: First Time Setup (Do This Once)
1. **Double-click** `SETUP.bat`
2. Wait 5-10 minutes for setup to complete
3. Done!

### Step 2: Run the Application
1. **Double-click** `RUN.bat`
2. Wait 10 seconds
3. Browser opens automatically!

### Step 3: Stop the Application
- Close all 3 windows that opened (Flask, Worker, Scheduler)
- OR close the main window

---

## 📋 Detailed Instructions

### First Time Setup

1. **Make sure Python is installed:**
   - Download from: https://www.python.org/downloads/
   - During installation, check ✅ "Add Python to PATH"
   - Install Python 3.9 or higher

2. **Run Setup:**
   - Find `SETUP.bat` in the project folder
   - **Double-click** it
   - A black window will open showing:
     - "Creating virtual environment..."
     - "Installing dependencies..."
     - "Downloading spaCy model..."
     - "Setting up database..."
   - Wait for "Setup Complete!" message
   - Press any key to close

3. **Setup is done!** ✅

---

### Running the Application

1. **Double-click `RUN.bat`**
   - A window will open showing progress
   - Three new windows will open:
     - **Job Crawler - Flask** (web server)
     - **Job Crawler - Worker** (background jobs)
     - **Job Crawler - Scheduler** (job scraping)
   - Your browser will open automatically to: http://127.0.0.1:5001

2. **Use the Application:**
   - Register a new account OR Login
   - Upload your resume
   - Search for jobs
   - Enable email alerts (optional)

3. **Stop the Application:**
   - Close all 3 windows (Flask, Worker, Scheduler)
   - OR close the main window

---

## 📧 Setting Up Email (Optional)

**You can now configure email through the web interface!**

1. **Login to the app**
2. **Click "⚙️ Configure Email"** button on the dashboard
3. **Follow the on-screen instructions** to get a Gmail app password
4. **Enter your email and app password** in the form
5. **Click "Save Email Settings"**
6. **Enable email alerts** from the dashboard

**No terminal commands needed!** Everything is done through the web interface.

---

## 🎯 What Each File Does

| File | Purpose |
|------|---------|
| `SETUP.bat` | Run ONCE for first-time setup |
| `RUN.bat` | Run EVERY TIME to start the app |
| `START.bat` | Alternative way to start (same as RUN.bat) |
| `launcher.py` | GUI launcher (double-click to use) |

---

## ❓ Troubleshooting

### "Python is not recognized"
**Solution:**
1. Install Python from https://www.python.org/
2. During installation, check ✅ "Add Python to PATH"
3. Restart your computer
4. Try again

### "Virtual environment not found"
**Solution:**
1. Run `SETUP.bat` first
2. Wait for it to complete
3. Then run `RUN.bat`

### "Port 5001 is already in use"
**Solution:**
1. Close all the windows from previous run
2. Wait a few seconds
3. Try `RUN.bat` again

### "Browser didn't open automatically"
**Solution:**
1. Manually open your browser
2. Go to: http://127.0.0.1:5001

### "Windows protected your PC" (when double-clicking .bat files)
**Solution:**
1. Click "More info"
2. Click "Run anyway"
3. This is normal - Windows is just being cautious

### Files open in Notepad instead of running
**Solution:**
1. Right-click on the `.bat` file
2. Select "Run as administrator"
3. OR use Command Prompt:
   - Press `Win + R`
   - Type `cmd` and press Enter
   - Type: `cd "C:\path\to\your\project"`
   - Type: `SETUP.bat` or `RUN.bat`

---

## 🎉 That's It!

**Windows users: Just double-click `SETUP.bat` (once), then `RUN.bat` (every time)!**

No terminal commands needed! Everything is point-and-click! 🖱️

---

## 📝 What Happens When You Run

1. **Flask App** starts (web server on port 5001)
2. **Celery Worker** starts (processes background jobs)
3. **Celery Scheduler** starts (scrapes jobs every 30 seconds)
4. **Browser** opens to http://127.0.0.1:5001

You'll see 3 windows open - that's normal! They're all needed for the app to work.

---

**Need help? Check the main README.md or HOW_TO_RUN.md files!**

