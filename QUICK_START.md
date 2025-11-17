# ⚡ Quick Start Guide

## 🎯 For Complete Beginners (No Coding Experience)

### Step 1: First Time Setup (One Time Only)

**Windows:**
- Double-click `SETUP.bat`
- Wait for it to finish
- Done! ✅

**Mac/Linux:**
- Double-click `setup.sh`
- OR right-click → "Open With" → Terminal
- Wait for it to finish
- Done! ✅

---

### Step 2: Start the Application

**Windows:**
- Double-click `START.bat`
- OR double-click `launcher.py` for GUI

**Mac/Linux:**
- Double-click `launcher.py` (GUI - Recommended)
- OR double-click `run_app.py` (Simple)
- OR double-click `start_app.sh`

**The app will open in your browser automatically!** 🌐

---

### Step 3: Stop the Application

**If using GUI launcher:**
- Click "■ Stop Application" button

**If using START.bat or scripts:**
- Close the terminal windows
- OR press Ctrl+C

---

## 📧 Email Setup (Optional)

Want to receive job alerts? Follow these steps:

1. Go to: https://myaccount.google.com/apppasswords
2. Click "Select app" → Choose "Mail"
3. Click "Select device" → Choose "Other" → Type "Job Crawler"
4. Click "Generate"
5. Copy the 16-digit password (e.g., `abcd efgh ijkl mnop`)

6. Create a file named `.env` in the project folder
   - Right-click → New → Text Document
   - Rename it to `.env` (remove .txt extension)
   - Open it and paste:
   ```
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=abcdefghijklmnop
   ```
   (Replace with your actual email and the 16-digit password)

7. Save and restart the app

---

## 🆘 Troubleshooting

**"Python not found"**
- Install Python from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

**"Virtual environment not found"**
- Run SETUP.bat (Windows) or setup.sh (Mac/Linux) first

**"Port already in use"**
- Close other applications using port 5001
- Restart your computer if needed

**"Can't open launcher.py"**
- Install Python first
- On Windows: Right-click → "Open With" → Python
- On Mac: Right-click → "Open With" → Python Launcher

**"Database error"**
- Make sure PostgreSQL is installed and running
- Check PostgreSQL is running in Services (Windows) or Activity Monitor (Mac)

---

## 💡 Tips

- **GUI Launcher** (`launcher.py`) is the easiest - just click buttons!
- **Logs** are shown in the GUI launcher window
- **Browser** opens automatically when app starts
- **Email alerts** only work if you set up `.env` file

---

## 📞 Need More Help?

- Check `README.md` for detailed documentation
- Check `START_HERE.md` for step-by-step instructions
- All logs are saved to `.log` files in the project folder

**Happy job hunting! 🎯**
