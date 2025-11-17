# 🔧 Fixing Render.yaml Error

## Issue
Render is having trouble parsing the `render.yaml` file, likely due to:
1. Redis property reference format
2. Service dependencies
3. YAML syntax

## ✅ Solution Options

### Option 1: Use Simplified Version (Recommended)

I've created a simplified `render-simple.yaml` that you can use:

1. **Rename the file:**
   ```bash
   mv render.yaml render.yaml.backup
   mv render-simple.yaml render.yaml
   ```

2. **Push to GitHub:**
   ```bash
   git add render.yaml
   git commit -m "Fix render.yaml format"
   git push origin main
   ```

3. **In Render Dashboard:**
   - After services are created, manually add environment variables:
     - `DATABASE_URL` - Copy from PostgreSQL service
     - `REDIS_URL` - Copy from Redis service

### Option 2: Manual Service Creation (Easier)

Instead of using Blueprint, create services manually:

#### Step 1: Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Name: `job-crawler-db`
3. Plan: Free
4. Click "Create"
5. **Copy the Internal Database URL**

#### Step 2: Create Redis
1. Click "New +" → "Redis"
2. Name: `job-crawler-redis`
3. Plan: Free
4. Click "Create"
5. **Copy the Internal Redis URL**

#### Step 3: Create Web Service
1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Configure:
   - **Name**: `job-crawler-web`
   - **Environment**: Python 3
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**: 
     ```bash
     gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120
     ```
   - **Plan**: Free

4. **Environment Variables**:
   ```
   FLASK_ENV=production
   SECRET_KEY=dfc072b7405b57e60b7fca3f2f3b28200ef043ae9395a2ab03312cdf557625b0
   DATABASE_URL=<paste-from-postgres-service>
   REDIS_URL=<paste-from-redis-service>
   PORT=10000
   ```

5. Click "Create Web Service"

#### Step 4: Create Worker
1. Click "New +" → "Background Worker"
2. Same repository
3. Configure:
   - **Name**: `job-crawler-worker`
   - **Build Command**: Same as web
   - **Start Command**: 
     ```bash
     celery -A tasks worker --loglevel=info --concurrency=2
     ```
   - **Environment Variables**: Same as web service

#### Step 5: Create Beat
1. Click "New +" → "Background Worker"
2. Same repository
3. Configure:
   - **Name**: `job-crawler-beat`
   - **Build Command**: Same as web
   - **Start Command**: 
     ```bash
     celery -A tasks beat --loglevel=info
     ```
   - **Environment Variables**: Same as web service

### Option 3: Fix Current render.yaml

The issue might be with Redis property reference. Try this corrected version:

**Key Changes:**
- Changed `plan: starter` to `plan: free` (for free tier)
- Removed `PORT` environment variable (Render sets this automatically)
- Simplified Redis connection

## 🔍 Common Issues

1. **"property: connectionString" error**
   - Solution: Use manual environment variable setup (Option 2)

2. **"plan: starter" not found**
   - Solution: Use `plan: free` for free tier

3. **Redis connectionString not found**
   - Solution: Manually copy Redis URL from service dashboard

## ✅ Recommended Approach

**Use Option 2 (Manual Creation)** - It's more reliable and gives you better control:

1. Create services one by one
2. Copy environment variables manually
3. More control over configuration
4. Easier to troubleshoot

## 📝 After Manual Setup

1. **Initialize Database:**
   - Go to Web Service → Shell
   - Run: `python database_setup.py`

2. **Verify Services:**
   - All services should show green status
   - Check logs for any errors

3. **Test Application:**
   - Visit your Render URL
   - Register and test features

## 🎯 Quick Fix

If you want to try the fixed render.yaml:

1. The file has been updated with `plan: free`
2. Push to GitHub
3. Try Blueprint again
4. If it still fails, use Option 2 (Manual)

---

**Status**: Fixed render.yaml with free tier plans
**Next Step**: Try Blueprint again OR use manual setup (recommended)

