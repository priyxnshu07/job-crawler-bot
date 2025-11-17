# 🚀 Automated Email Alerts - Complete Setup Guide

## ✅ What's Ready

✅ Database schema updated  
✅ Flask-Mail installed and configured  
✅ Email infrastructure ready  
✅ Database columns added (email_alerts_enabled, last_email_check)  

## 🔧 What You Need to Do

### 1. Configure Gmail App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in with your Gmail account
3. Select "Mail" and "Other"
4. Name it "Job Crawler"
5. Click "Generate"
6. Copy the 16-character password (no spaces)

### 2. Set Environment Variables

```bash
# Set these in your terminal:
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-16-char-app-password"

# Add to your ~/.zshrc or ~/.bashrc to make permanent:
echo 'export EMAIL_USER="your-email@gmail.com"' >> ~/.zshrc
echo 'export EMAIL_PASSWORD="your-app-password"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Restart Your Flask App

```bash
# Kill existing process
pkill -f "python.*app.py"

# Start fresh
cd /Users/priyanshuparashar/Documents/daily\ work/jobcrawlerprototype
source venv/bin/activate
python app.py
```

### 4. Test Email Functionality

Visit: http://127.0.0.1:5000

1. Login to your account
2. Upload your resume if you haven't
3. Click "Send Test Email" button
4. Check your Gmail inbox!

## 🎯 Next Steps to Complete

The infrastructure is ready. You now need to add the email functions to `app.py`. 

Refer to `EMAIL_SETUP_GUIDE.md` for the complete code to add:
- Email sending function
- Toggle alerts route
- Test email route
- Celery task for automated checking
- UI components

## 📧 How It Will Work

Once fully configured:

1. **User enables alerts** in UI
2. **Celery scrapes** jobs every 30 seconds
3. **Celery checks** for new matches
4. **Email is sent** if new matching jobs found
5. **System tracks** what was already sent

## 🎉 Result

Instead of manually checking, users get:
- **Proactive notifications** when perfect jobs appear
- **Only relevant jobs** that match their skills
- **Match scores** showing why it's relevant
- **Direct apply links** in email

## 💡 Benefits

### For Users:
✅ Never miss a perfect opportunity  
✅ Get notified as soon as jobs appear  
✅ Only relevant jobs sent  
✅ Match scores explain why  

### For You:
✅ Differentiates your app  
✅ Increases user engagement  
✅ Builds stickiness  
✅ Automated, runs 24/7  

Your job crawler becomes a **personal job agent** that works for the user even when they're not logged in!

