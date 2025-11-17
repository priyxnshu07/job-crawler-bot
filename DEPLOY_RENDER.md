# 🚀 Deploy to Render - Complete Guide

## Option 1: Blueprint Deployment (Easiest - Try This First)

### Step 1: Connect GitHub Repository

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account (if not already connected)
4. Select your repository: `jobcrawlerprototype` (or your repo name)
5. Click **"Apply"**

### Step 2: Review Configuration

Render will automatically detect `render.yaml` and create:
- ✅ PostgreSQL database
- ✅ Redis instance
- ✅ Web service
- ✅ Worker service
- ✅ Beat service

### Step 3: Manual Redis URL Setup (If Needed)

**If Blueprint shows an error about Redis**, you'll need to add `REDIS_URL` manually:

1. After Blueprint creates services, go to each service (web, worker, beat)
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add:
   - **Key**: `REDIS_URL`
   - **Value**: Go to Redis service → **"Info"** tab → Copy **"Internal Redis URL"**
5. Save and redeploy

### Step 4: Initialize Database

1. Wait for all services to deploy (green status)
2. Go to **Web Service** → Click **"Shell"** tab
3. Run:
   ```bash
   python database_setup.py
   ```
4. You should see: "Database and tables created/updated successfully"

### Step 5: Access Your App

Your app will be live at:
```
https://job-crawler-web.onrender.com
```
(Your actual URL is shown in the Web Service dashboard)

---

## Option 2: Manual Setup (More Reliable)

If Blueprint doesn't work, follow these steps:

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

### Step 2: Create Redis Instance

1. Click **"New +"** → **"Redis"**
2. Configure:
   - **Name**: `job-crawler-redis`
   - **Plan**: **Free**
3. Click **"Create Redis"**
4. **IMPORTANT**: Copy the **"Internal Redis URL"** (you'll need this)

### Step 3: Create Web Service

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
   REDIS_URL = <paste Internal Redis URL from Step 2>
   ```

5. Click **"Create Web Service"**

### Step 4: Create Celery Worker

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
   REDIS_URL = <same as web service>
   ```

5. Click **"Create Background Worker"**

### Step 5: Create Celery Beat (Scheduler)

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
   REDIS_URL = <same as web service>
   ```

5. Click **"Create Background Worker"**

### Step 6: Initialize Database

1. Wait for Web Service to finish building (green status)
2. Go to **Web Service** → Click **"Shell"** tab
3. Run:
   ```bash
   python database_setup.py
   ```
4. You should see: "Database and tables created/updated successfully"

### Step 7: Access Your Application

Your app will be live at:
```
https://job-crawler-web.onrender.com
```
(Your actual URL is shown in the Web Service dashboard)

---

## ✅ Verification Checklist

- [ ] PostgreSQL database created (green status)
- [ ] Redis created (green status)
- [ ] Web service deployed (green status)
- [ ] Worker deployed (green status)
- [ ] Beat deployed (green status)
- [ ] Database initialized
- [ ] Application accessible via URL
- [ ] Can register/login
- [ ] Can upload resume
- [ ] Job search works

## 🔑 Important URLs to Copy

When creating services, you'll need these URLs:

1. **PostgreSQL Internal Database URL**:
   - Format: `postgresql://user:password@host:port/dbname`
   - Found in: Database service → "Info" tab → "Internal Database URL"

2. **Redis Internal URL**:
   - Format: `redis://:password@host:port`
   - Found in: Redis service → "Info" tab → "Internal Redis URL"

## 🎯 Quick Reference

**Secret Key** (use for all services):
```
dfc072b7405b57e60b7fca3f2f3b28200ef043ae9395a2ab03312cdf557625b0
```

**Environment Variables** (for all services):
- `FLASK_ENV` = `production`
- `SECRET_KEY` = (above)
- `DATABASE_URL` = (from PostgreSQL)
- `REDIS_URL` = (from Redis)

## 🐛 Troubleshooting

**Build fails?**
- Check build logs
- Verify requirements.txt is correct
- Check Python version

**App not starting?**
- Check runtime logs
- Verify all environment variables are set
- Check database connection

**Worker not processing?**
- Check worker logs
- Verify REDIS_URL is correct
- Check Celery configuration

**Redis connection error?**
- Make sure you're using **Internal Redis URL** (not external)
- Verify REDIS_URL is set in all services (web, worker, beat)

## 🎉 Success!

Once all services are green and database is initialized, your app is live globally! 🌍

---

## 📝 Notes

- **Free tier**: Services may spin down after 15 minutes of inactivity
- **First request**: May take 30-60 seconds to wake up
- **Database**: Free tier PostgreSQL is sufficient for development
- **Redis**: Free tier Redis is sufficient for Celery

