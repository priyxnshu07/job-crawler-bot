# Easy Deployment Guide for Render

We have simplified your project configuration so it can be deployed **without a credit card** on Render's free tier.

## What Changed?
- **Removed Extra Services**: We deleted the separate "Worker" and "Beat" services.
- **Unified App**: The background job scraper now runs *inside* your main web application.
- **Free Tier Friendly**: You now only need 1 Web Service and 1 Database.

## How to Deploy

### Step 1: Push Changes to GitHub
First, make sure you commit and push the changes we just made:
```bash
git add render.yaml Procfile
git commit -m "Fix deployment: simplified for free tier"
git push origin main
```

### Step 2: Deploy on Render
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository.
4. Render will detect the `render.yaml` file.
5. **IMPORTANT**: You will see two resources to be created:
    - `job-crawler-web` (Web Service)
    - `job-crawler-db` (PostgreSQL)
6. Click **Apply**.

### Troubleshooting Database
If Render asks for a credit card to create the PostgreSQL database:
1. **Uncheck** the database resource in the Blueprint list if possible, OR...
2. Create a free database on [Neon.tech](https://neon.tech) or [Supabase](https://supabase.com).
3. Get the "Connection String" (starts with `postgres://...`).
4. In Render, go to your Web Service -> **Environment**.
5. Add a new Environment Variable:
    - Key: `DATABASE_URL`
    - Value: `postgres://...` (your external connection string)

### Step 3: Verify
Once deployed, wait a few minutes. The logs should show:
> `✅ Background scraper thread started (no worker service needed!)`

This confirms your job scraper is running automatically in the background!
