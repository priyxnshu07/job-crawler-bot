# ✅ Your Credentials Are Configured!

## 🚀 Start Your App

I've created a startup script with your credentials. Run this:

```bash
./start_with_email.sh
```

Or manually:

```bash
# In your project directory:
cd "/Users/priyanshuparashar/Documents/daily work/jobcrawlerprototype"
source venv/bin/activate

# Set credentials
export EMAIL_USER="parasharpriyanshu08@gmail.com"
export EMAIL_PASSWORD="ocigzfqkmecxtcyy"

# Start app
python app.py
```

## 🌐 Access Your App

Once the app starts, open your browser:

**http://127.0.0.1:5001**

## 🧪 Test Email

1. **Login** to your account
2. In **Your Profile** section, find **"Send Test Email"**
3. **Click it**
4. Check your inbox at **parasharpriyanshu08@gmail.com**!

## 📧 Enable Automated Alerts

1. After testing email works
2. Click **"Enable Email Alerts"** button
3. Your app will now email you when new matching jobs appear!

## 🎉 What You Can Do

✅ **Login/Register** - Create account or login  
✅ **Upload Resume** - Extract your 14 skills  
✅ **Search Jobs** - Find opportunities  
✅ **Personalized Matches** - See jobs sorted by your skills  
✅ **Test Email** - Send yourself a test email  
✅ **Enable Alerts** - Get automated job alerts  

## 📝 Next Steps

If you want to start the other services (Celery worker and beat), open new terminals:

**Terminal 2:**
```bash
cd "/Users/priyanshuparashar/Documents/daily work/jobcrawlerprototype"
source venv/bin/activate
celery -A tasks worker --loglevel=info
```

**Terminal 3:**
```bash
cd "/Users/priyanshuparashar/Documents/daily work/jobcrawlerprototype"
source venv/bin/activate
celery -A tasks beat --loglevel=info
```

This enables automatic job scraping and alert checking.

## 🎯 Your Complete Setup

Everything is ready! Just run `./start_with_email.sh` and visit http://127.0.0.1:5001!



