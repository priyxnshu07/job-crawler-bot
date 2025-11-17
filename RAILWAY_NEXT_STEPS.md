# 🚀 Railway Deployment - Complete These Steps

Your GitHub repo is connected! Now complete the deployment:

## ✅ Step 1: Add PostgreSQL (30 seconds)

1. In Railway dashboard, click **"+ New"** (top right)
2. Click **"Database"**
3. Click **"Add PostgreSQL"**
4. ✅ DONE! Railway auto-sets `DATABASE_URL`

## ✅ Step 2: Add Redis (30 seconds)

1. Click **"+ New"** again
2. Click **"Database"**
3. Click **"Add Redis"**
4. ✅ DONE! Railway auto-sets `REDIS_URL`

## ✅ Step 3: Configure Web Service (2 minutes)

1. Click on your **web service** (the one that's building)
2. Click **"Settings"** tab
3. Scroll to **"Build Command"** - change to:
   ```bash
   pip install -r requirements.txt && python -m spacy download en_core_web_sm
   ```
4. Scroll to **"Start Command"** - change to:
   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```
5. Click **"Variables"** tab
6. Click **"+ New Variable"**
7. Add:
   - **Key**: `FLASK_ENV`
   - **Value**: `production`
8. Click **"+ New Variable"** again
9. Add:
   - **Key**: `SECRET_KEY`
   - **Value**: `dfc072b7405b57e60b7fca3f2f3b28200ef043ae9395a2ab03312cdf557625b0`

   *(Note: `DATABASE_URL` and `REDIS_URL` are already there automatically)*

## ✅ Step 4: Add Worker (1 minute)

1. Click **"+ New"** → **"GitHub Repo"**
2. Select **same repository** (jobcrawlerprototype)
3. Click on the new service
4. Go to **"Settings"** tab
5. **Start Command**:
   ```bash
   celery -A tasks worker --loglevel=info --concurrency=2
   ```
6. Go to **"Variables"** tab
7. Add same variables as web service:
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = `dfc072b7405b57e60b7fca3f2f3b28200ef043ae9395a2ab03312cdf557625b0`
   - *(DATABASE_URL and REDIS_URL are auto-inherited)*

## ✅ Step 5: Add Beat (1 minute)

1. Click **"+ New"** → **"GitHub Repo"**
2. Select **same repository**
3. Click on the new service
4. Go to **"Settings"** tab
5. **Start Command**:
   ```bash
   celery -A tasks beat --loglevel=info
   ```
6. Go to **"Variables"** tab
7. Add same variables as web service

## ✅ Step 6: Initialize Database (1 minute)

1. **Wait** for web service to finish building (green checkmark ✅)
2. Click on **web service**
3. Click **"Deployments"** tab
4. Click on **latest deployment**
5. Click **"View Logs"**
6. Click **"Shell"** button (top right)
7. Type:
   ```bash
   python database_setup.py
   ```
8. Press **Enter**
9. Wait for: "Database and tables created/updated successfully"

## ✅ Step 7: Get Your URL (30 seconds)

1. Click on **web service**
2. Click **"Settings"** tab
3. Scroll to **"Domains"** section
4. You'll see a URL like: `job-crawler-web-production.up.railway.app`
5. Click the URL → **YOUR APP IS LIVE!** 🎉

## 🎉 Success!

Your app is now:
- ✅ Globally accessible
- ✅ HTTPS enabled
- ✅ All services running
- ✅ Database initialized
- ✅ 100% FREE!

## 🆘 If You Get Stuck

Tell me which step number and I'll help immediately!

---

**Total Time**: ~10 minutes
**Status**: Almost there! 🚀

