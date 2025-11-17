# 🎯 How to Use Job Crawler Bot

## Step 1: Start the App (Super Easy!)

Open Terminal and run:

```bash
cd "/Users/priyanshuparashar/Documents/daily work/jobcrawlerprototype"
./start.sh
```

You'll see:
```
🚀 Starting Job Crawler Bot...
📱 Starting Flask app...
⚙️  Starting Celery worker...
⏰ Starting Celery beat scheduler...
✅ All services started!
🌐 Open your browser: http://127.0.0.1:5001
```

## Step 2: Open the App

Open your browser and go to: **http://127.0.0.1:5001**

## Step 3: Create an Account

1. Click "Register" if you don't have an account
2. Enter your email and password
3. Click "Register"

## Step 4: Upload Your Resume

1. On the homepage, scroll to "Profile Section"
2. Upload your resume (PDF or DOCX)
3. Your skills will be extracted automatically!
4. You'll see tags with your skills (Python, SQL, etc.)

## Step 5: Enable Email Alerts

1. In your Profile Section, click **"Enable Email Alerts"**
2. You'll receive emails with matching jobs!

## Step 6: Search Jobs

1. Type in the search box (e.g., "Python", "Remote")
2. OR click **"Show Personalized Matches"** to see jobs matched to YOUR skills
3. Click "Apply Now" to go to Indeed.com and apply!

## How It Works

- **Every 30 seconds:** System scrapes new jobs
- **Every 35 seconds:** System checks for jobs matching your skills
- **If matches found:** You get an email with job details!

## Stop the App

Press `Ctrl+C` in the terminal to stop everything.

---

## Troubleshooting

### Can't access http://127.0.0.1:5001?
- Make sure you ran `./start.sh`
- Wait 5 seconds for everything to start

### No emails received?
- Check your spam folder
- Make sure "Enable Email Alerts" is clicked in your profile
- Upload your resume with technical skills mentioned

### Need to restart?
- Press `Ctrl+C` to stop
- Run `./start.sh` again

That's it! 🎉
