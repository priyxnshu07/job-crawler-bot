# 🚀 Deploy to Render - 100% FREE (No Redis Needed!)

**Good news!** Your app now uses the **database as Celery broker** - no Redis required! This means:
- ✅ **100% FREE** - Only need PostgreSQL (free tier)
- ✅ **No Redis** - One less service to manage
- ✅ **Simpler setup** - Fewer things that can fail

## 🎯 Quick Deployment (Blueprint - Easiest)

### Step 1: Deploy via Blueprint

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account (if not already connected)
4. Select your repository: `job-crawler-bot` (or your repo name)
5. Click **"Apply"**

**That's it!** Render will automatically:
- ✅ Create PostgreSQL database (FREE)
- ✅ Deploy web service (FREE)
- ✅ Deploy worker service (FREE)
- ✅ Deploy beat service (FREE)
- ✅ **NO REDIS NEEDED!** (Uses database instead)

### Step 2: Initialize Database

1. Wait for all services to deploy (green status - takes 2-3 minutes)
2. Go to **Web Service** → Click **"Shell"** tab
3. Run:
   ```bash
   python database_setup.py
   ```
4. You should see: "Database and tables created/updated successfully"

### Step 3: Access Your App

Your app will be live at:
```
https://job-crawler-web.onrender.com
```
(Your actual URL is shown in the Web Service dashboard)

---

## 🎯 Manual Setup (If Blueprint Fails)

If Blueprint doesn't work, follow these steps (still 100% free):

### Step 1: Create PostgreSQL Database

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `job-crawler-db`
   - **Database**: `job_crawler_db`
   - **User**: `job_crawler_user`
   - **Plan**: **Free**
4. Click **"Create Database"**
5. **IMPORTANT**: Copy the **"Internal Database URL"** (you'll need this)

### Step 2: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. **Connect your GitHub repository**
3. Configure:
   - **Name**: `job-crawler-web`
   - **Environment**: **Python 3**
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**: 
     ```bash
     gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120
     ```
   - **Plan**: **Free**

4. **Environment Variables** (click "Add Environment Variable" for each):
   ```
   FLASK_ENV = production
   SECRET_KEY = dfc072b7405b57e60b7fca3f2f3b28200ef043ae9395a2ab03312cdf557625b0
   DATABASE_URL = <paste Internal Database URL from Step 1>
   ```
   **Note**: NO REDIS_URL needed! The app uses the database as broker.

5. Click **"Create Web Service"**

### Step 3: Create Celery Worker

1. Click **"New +"** → **"Background Worker"**
2. **Connect same GitHub repository**
3. Configure:
   - **Name**: `job-crawler-worker`
   - **Environment**: **Python 3**
   - **Branch**: `main`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**: 
     ```bash
     celery -A tasks worker --loglevel=info --concurrency=2
     ```
   - **Plan**: **Free**

4. **Environment Variables** (same as web service):
   ```
   FLASK_ENV = production
   SECRET_KEY = dfc072b7405b57e60b7fca3f2f3b28200ef043ae9395a2ab03312cdf557625b0
   DATABASE_URL = <same as web service>
   ```

5. Click **"Create Background Worker"**

### Step 4: Create Celery Beat (Scheduler)

1. Click **"New +"** → **"Background Worker"**
2. **Connect same GitHub repository**
3. Configure:
   - **Name**: `job-crawler-beat`
   - **Environment**: **Python 3**
   - **Branch**: `main`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**: 
     ```bash
     celery -A tasks beat --loglevel=info
     ```
   - **Plan**: **Free**

4. **Environment Variables** (same as web service):
   ```
   FLASK_ENV = production
   SECRET_KEY = dfc072b7405b57e60b7fca3f2f3b28200ef043ae9395a2ab03312cdf557625b0
   DATABASE_URL = <same as web service>
   ```

5. Click **"Create Background Worker"**

### Step 5: Initialize Database

1. Wait for Web Service to finish building (green status)
2. Go to **Web Service** → Click **"Shell"** tab
3. Run:
   ```bash
   python database_setup.py
   ```
4. You should see: "Database and tables created/updated successfully"

### Step 6: Access Your Application

Your app will be live at:
```
https://job-crawler-web.onrender.com
```
(Your actual URL is shown in the Web Service dashboard)

---

## ✅ Verification Checklist

- [ ] PostgreSQL database created (green status)
- [ ] Web service deployed (green status)
- [ ] Worker deployed (green status)
- [ ] Beat deployed (green status)
- [ ] Database initialized
- [ ] Application accessible via URL
- [ ] Can register/login
- [ ] Can upload resume
- [ ] Job search works

## 🎯 Quick Reference

**Secret Key** (use for all services):
```
dfc072b7405b57e60b7fca3f2f3b28200ef043ae9395a2ab03312cdf557625b0
```

**Environment Variables** (for all services):
- `FLASK_ENV` = `production`
- `SECRET_KEY` = (above)
- `DATABASE_URL` = (from PostgreSQL)
- **NO REDIS_URL NEEDED!** ✅

## 🐛 Troubleshooting

**Build fails?**
- Check build logs
- Verify requirements.txt is correct
- Check Python version

**App not starting?**
- Check runtime logs
- Verify DATABASE_URL is set
- Check database connection

**Worker not processing?**
- Check worker logs
- Verify DATABASE_URL is correct
- Check Celery configuration

**"No module named 'kombu'" error?**
- Make sure requirements.txt includes `kombu[sqlalchemy]`
- Rebuild the service

## 💡 How It Works

Your app now uses **PostgreSQL as the Celery broker** instead of Redis:
- ✅ **Free** - No extra service needed
- ✅ **Reliable** - Uses your existing database
- ✅ **Simple** - One less thing to configure
- ⚠️ **Slightly slower** - Database is slower than Redis, but fine for job scraping

## 🎉 Success!

Once all services are green and database is initialized, your app is live globally! 🌍

**Total cost: $0.00** (100% free tier)

---

## 📝 Notes

- **Free tier**: Services may spin down after 15 minutes of inactivity
- **First request**: May take 30-60 seconds to wake up
- **Database**: Free tier PostgreSQL is sufficient for development
- **No Redis**: Not needed! Database broker works great for this use case

