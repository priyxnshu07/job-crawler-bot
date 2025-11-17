# 🚀 Deploy to Render - Global Access

This guide will help you deploy your Job Crawler application to Render for global access.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com) (free tier available)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Environment Variables**: Know your email configuration (optional)

## 🚀 Quick Deployment Steps

### Step 1: Push Code to GitHub

```bash
# Make sure all changes are committed
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create Render Account & Services

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Blueprint"** (for automatic setup)
   - OR manually create services (see Step 3)

### Step 3: Manual Service Setup (Alternative)

#### 3.1 Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. Name: `job-crawler-db`
3. Database: `job_crawler_db`
4. User: `job_crawler_user`
5. Plan: **Free** (or Starter for production)
6. Click **"Create Database"**
7. **Copy the Internal Database URL** (you'll need this)

#### 3.2 Create Redis Instance

1. Click **"New +"** → **"Redis"**
2. Name: `job-crawler-redis`
3. Plan: **Free** (or Starter for production)
4. Click **"Create Redis"**
5. **Copy the Internal Redis URL**

#### 3.3 Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `job-crawler-web`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**: 
     ```bash
     gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120
     ```
   - **Plan**: Free (or Starter for production)

4. **Environment Variables**:
   ```
   FLASK_ENV=production
   SECRET_KEY=<generate-a-random-secret-key>
   DATABASE_URL=<from-postgres-service>
   REDIS_URL=<from-redis-service>
   PORT=10000
   ```

5. Click **"Create Web Service"**

#### 3.4 Create Celery Worker

1. Click **"New +"** → **"Background Worker"**
2. Connect same GitHub repository
3. Configure:
   - **Name**: `job-crawler-worker`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**: 
     ```bash
     celery -A tasks worker --loglevel=info --concurrency=2
     ```
   - **Plan**: Free

4. **Environment Variables** (same as web service):
   ```
   FLASK_ENV=production
   SECRET_KEY=<same-as-web-service>
   DATABASE_URL=<from-postgres-service>
   REDIS_URL=<from-redis-service>
   ```

5. Click **"Create Background Worker"**

#### 3.5 Create Celery Beat (Scheduler)

1. Click **"New +"** → **"Background Worker"**
2. Connect same GitHub repository
3. Configure:
   - **Name**: `job-crawler-beat`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**: 
     ```bash
     celery -A tasks beat --loglevel=info
     ```
   - **Plan**: Free

4. **Environment Variables** (same as web service)

5. Click **"Create Background Worker"**

### Step 4: Initialize Database

After services are deployed:

1. Go to your **Web Service** → **"Shell"** tab
2. Run:
   ```bash
   python database_setup.py
   ```
3. This will create all necessary tables

### Step 5: Access Your Application

Your application will be available at:
```
https://job-crawler-web.onrender.com
```
(URL will be shown in your Render dashboard)

## 🔧 Using Render Blueprint (Easier Method)

### Option A: Using render.yaml

1. **Push render.yaml to GitHub** (already created)
2. In Render Dashboard, click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Click **"Apply"** - Render will create all services automatically!

### Option B: Manual Setup (More Control)

Follow Step 3 above for manual service creation.

## 🔐 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `production` |
| `SECRET_KEY` | Flask secret key | Generate random string |
| `DATABASE_URL` | PostgreSQL connection | Auto-provided by Render |
| `REDIS_URL` | Redis connection | Auto-provided by Render |
| `PORT` | Server port | `10000` (Render default) |

### Optional Variables

| Variable | Description |
|----------|-------------|
| `EMAIL_USER` | Gmail address for alerts |
| `EMAIL_PASSWORD` | Gmail app password |

### Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 📝 Post-Deployment Steps

### 1. Verify Services

Check that all services are running:
- ✅ Web Service (green status)
- ✅ Worker (green status)
- ✅ Beat (green status)
- ✅ PostgreSQL (green status)
- ✅ Redis (green status)

### 2. Test Application

1. Visit your Render URL
2. Register a new account
3. Upload a resume
4. Test job search
5. Set location preference

### 3. Monitor Logs

- Go to each service → **"Logs"** tab
- Check for any errors
- Monitor background job processing

## 🎯 Custom Domain (Optional)

1. Go to your Web Service
2. Click **"Settings"** → **"Custom Domain"**
3. Add your domain
4. Follow DNS configuration instructions

## 💰 Pricing

### Free Tier (Good for Testing)

- **Web Service**: Free (spins down after 15 min inactivity)
- **Worker**: Free
- **PostgreSQL**: Free (90 days, then $7/month)
- **Redis**: Free (25MB limit)

### Starter Plan (Recommended for Production)

- **Web Service**: $7/month (always on)
- **Worker**: $7/month
- **PostgreSQL**: $7/month
- **Redis**: $10/month

**Total**: ~$31/month for always-on production

## 🐛 Troubleshooting

### Build Fails

1. Check **Build Logs** in Render dashboard
2. Common issues:
   - Missing dependencies in requirements.txt
   - spaCy model download fails
   - Python version mismatch

### Application Not Starting

1. Check **Runtime Logs**
2. Verify environment variables are set
3. Check database connection
4. Verify Redis connection

### Database Connection Error

1. Verify `DATABASE_URL` is set correctly
2. Check PostgreSQL service is running
3. Verify database name matches

### Worker Not Processing Jobs

1. Check worker logs
2. Verify `REDIS_URL` is set
3. Check Celery configuration

## 📊 Monitoring

### Render Dashboard

- View service status
- Check logs in real-time
- Monitor resource usage
- View metrics

### Application Health

- Health check endpoint: `/login`
- Monitor via Render dashboard
- Set up alerts for downtime

## 🔄 Updates

To update your application:

1. Push changes to GitHub
2. Render automatically detects changes
3. Rebuilds and redeploys services
4. Zero-downtime deployment (on paid plans)

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Render Python Guide](https://render.com/docs/deploy-flask)
- [Render PostgreSQL](https://render.com/docs/databases)
- [Render Redis](https://render.com/docs/redis)

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] PostgreSQL database created
- [ ] Redis instance created
- [ ] Web service deployed
- [ ] Worker service deployed
- [ ] Beat service deployed
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] Application accessible
- [ ] All services running

## 🎉 Success!

Once deployed, your application will be:
- ✅ Globally accessible
- ✅ Always available (on paid plans)
- ✅ Auto-scaling
- ✅ Secure (HTTPS by default)
- ✅ Monitored

**Your Job Crawler is now live on the internet!** 🌐

