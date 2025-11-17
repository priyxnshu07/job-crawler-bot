# 🚀 Start Here - Job Crawler Bot

## Easiest Way to Run (No Terminal Required!)

### Option 1: GUI Launcher (Recommended) 🖥️

**For Windows/Mac/Linux users who want a simple interface:**

1. **Double-click** `launcher.py` 
   - OR right-click → "Open With" → Python
   - OR run: `python launcher.py`

2. Click **"▶ Start Application"** button

3. Wait for "✅ All services started" message

4. Click **"🌐 Open in Browser"** or it will open automatically

5. When done, click **"■ Stop Application"**

That's it! No terminal commands needed! 🎉

---

### Option 2: Simple Python Script 🐍

**If the GUI doesn't work, use this:**

1. **Double-click** `run_app.py`
   - OR run: `python run_app.py`

2. The app will start and open your browser automatically

3. Press **Ctrl+C** to stop when done

---

### Option 3: One-Click Script (Mac/Linux) 📱

1. **Double-click** `start_app.sh`
   - OR right-click → "Open" → Terminal

2. The app starts automatically

---

## First Time Setup

If this is your first time, you need to run setup once:

1. **Double-click** `setup.sh` (Mac/Linux)
   - OR run: `python setup.sh` (Windows)
   - OR run: `./setup.sh` in terminal

This will install everything you need.

---

## Email Alerts Setup (Optional)

To receive job alerts via email:

1. Get a Gmail App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Create a new app password
   - Copy the 16-digit password

2. Create a `.env` file in the project folder:
   ```
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-16-digit-app-password
   ```

3. Restart the app

---

## Troubleshooting

**"Virtual environment not found"**
- Run `setup.sh` first

**"Port already in use"**
- Another app is using port 5001
- Close other apps or change the port in `app.py`

**"Database connection error"**
- Make sure PostgreSQL is running
- Check `config.py` for correct database settings

**Can't open GUI launcher?**
- Install tkinter: `pip install tk` (if not already installed)
- Or use `run_app.py` instead

---

## Need Help?

- Check `README.md` for detailed documentation
- Check logs in the GUI launcher or terminal
- All logs are saved to: `flask.log`, `celery-worker.log`, `celery-beat.log`

---

**Enjoy your automated job search! 🎯**
