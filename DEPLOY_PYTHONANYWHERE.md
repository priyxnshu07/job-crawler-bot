# 🐍 Deploy to PythonAnywhere NOW (100% FREE)

## ✅ Step 1: Sign Up (1 minute)

1. Go to: https://www.pythonanywhere.com
2. Click **"Beginner: Free account"** (bottom of page)
3. Sign up with email or GitHub
4. Verify email
5. Login

## ✅ Step 2: Clone Your Code (1 minute)

1. Go to **"Files"** tab (top menu)
2. Click **"Bash console"** (opens terminal)
3. Run:
   ```bash
   git clone https://github.com/priyxnshu07/job-crawler-bot.git jobcrawler
   cd jobcrawler
   ```

## ✅ Step 3: Install Dependencies (2 minutes)

In the same Bash console:
```bash
pip3.9 install --user -r requirements.txt
python3.9 -m spacy download en_core_web_sm
```

## ✅ Step 4: Get Railway Database URLs

**Keep your Railway databases!** We'll connect to them:

1. Go back to Railway dashboard
2. Click **PostgreSQL** service
3. Go to **"Connect"** tab
4. Copy the **"Public Network"** connection string
   - Format: `postgresql://postgres:password@host:port/dbname`
5. Do the same for **Redis** → Copy connection URL

## ✅ Step 5: Configure Web App (3 minutes)

1. In PythonAnywhere, go to **"Web"** tab
2. Click **"Add a new web app"**
3. Choose **"Flask"**
4. Choose **"Python 3.9"**
5. **Source code**: `/home/yourusername/jobcrawler`
6. **Working directory**: `/home/yourusername/jobcrawler`
7. Click **"Next"**

8. **WSGI file**: Click the link to edit
9. Replace content with:
   ```python
   import sys
   path = '/home/yourusername/jobcrawler'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```
10. Click **"Save"**

10. Go to **"Web"** tab → Your web app → **"Environment variables"**
11. Add:
    ```
    DATABASE_URL=<paste-from-railway-postgres>
    REDIS_URL=<paste-from-railway-redis>
    FLASK_ENV=production
    SECRET_KEY=dfc072b7405b57e60b7fca3f2f3b28200ef043ae9395a2ab03312cdf557625b0
    ```

## ✅ Step 6: Initialize Database (1 minute)

1. Go to **"Bash console"**
2. Run:
   ```bash
   cd jobcrawler
   python3.9 database_setup.py
   ```

## ✅ Step 7: Reload Web App

1. Go to **"Web"** tab
2. Click **"Reload"** button (green button)
3. Your app is live!

## ✅ Step 8: Get Your URL

Your app URL is: `https://yourusername.pythonanywhere.com`

(Replace `yourusername` with your PythonAnywhere username)

## 🎉 DONE!

Your app is now:
- ✅ Globally accessible
- ✅ 100% FREE
- ✅ Using Railway databases
- ✅ No credit card needed

---

**If you get stuck, tell me which step!**

