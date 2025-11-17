# 📧 Quick Email Setup - Step by Step

## ✅ You Have Your Gmail App Password - Now What?

### Step 1: Set Environment Variables

Open a terminal and run these commands (replace with YOUR values):

```bash
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-16-char-app-password"
```

**Example:**
```bash
export EMAIL_USER="priyanshu@gmail.com"
export EMAIL_PASSWORD="abcd efgh ijkl mnop"
```

⚠️ **Important:** Remove the spaces from the app password!

### Step 2: Start/Restart Your Flask App

```bash
cd "/Users/priyanshuparashar/Documents/daily work/jobcrawlerprototype"
source venv/bin/activate

# Kill old process if running
pkill -f "python.*app.py"

# Start fresh with environment variables
python app.py
```

### Step 3: Access the App

Open your browser and go to:

**http://127.0.0.1:5001**

Or run:
```bash
open http://127.0.0.1:5001
```

## 🧪 Test Email Sending

1. **Login** to your account
2. In your **profile section**, find **"Send Test Email"**
3. **Click it**
4. Check your **Gmail inbox** for the test email!

## ✅ Test Email Alerts

1. Upload your resume if you haven't
2. Click **"Enable Email Alerts"** button
3. It should change to "Disable Email Alerts"
4. The system will now check for matching jobs and send emails!

## 📝 Quick Commands

```bash
# Check if email credentials are set
echo $EMAIL_USER
echo $EMAIL_PASSWORD

# If they're not showing, set them again:
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-password-without-spaces"
```

## 🔧 Troubleshooting

### Email not sending?
- Check you set the environment variables before starting Flask
- Check that password has NO spaces
- Check browser console (F12) for errors

### Can't access app?
- Make sure Flask is running
- Check: http://127.0.0.1:5001
- If port 5001 doesn't work, check app.log for errors

### Want to make credentials permanent?
Add to your ~/.zshrc:

```bash
echo 'export EMAIL_USER="your-email@gmail.com"' >> ~/.zshrc
echo 'export EMAIL_PASSWORD="your-app-password"' >> ~/.zshrc
source ~/.zshrc
```

Now restart Flask!





