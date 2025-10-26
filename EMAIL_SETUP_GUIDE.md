# 📧 Automated Job Alert System - Setup Guide

## ✅ What's Been Implemented

1. **Database Schema** - Added columns for email alerts
2. **Flask-Mail** - Configured and ready
3. **Requirements Updated** - Flask-Mail added

## 🔧 What You Need to Do

### Step 1: Update Database
Run the database update to add the new columns:

```bash
python database_setup.py
```

This will add:
- `email_alerts_enabled` (boolean) - User's email alert preference
- `last_email_check` (timestamp) - Track when we last checked for new jobs

### Step 2: Install Flask-Mail
```bash
pip install Flask-Mail
```

### Step 3: Configure Email Credentials

Set up environment variables for Gmail:

```bash
# For Gmail, create an App Password:
# 1. Go to: https://myaccount.google.com/apppasswords
# 2. Generate an app-specific password
# 3. Set environment variables:

export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password-here"

# Or add to your shell profile (~/.zshrc or ~/.bashrc)
```

### Step 4: Add Email Functionality to app.py

Add these functions and routes after the existing routes (before `if __name__ == '__main__'`):

```python
# Email alert functions
def send_job_alert_email(user_email, user_skills, matched_jobs):
    """Send email alert with matching jobs."""
    if not matched_jobs:
        return False
    
    try:
        subject = f"🎯 {len(matched_jobs)} New Job Matches!"
        html_body = f"""
        <html><body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>🎉 New Job Matches Found!</h2>
            <p>Based on your skills: {', '.join(user_skills[:5])}</p>
            <p><strong>{len(matched_jobs)} jobs match your profile</strong></p>
            <hr>
            {''.join([f'''
            <div style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px;">
                <h3>{job['title']}</h3>
                <p><strong>Company:</strong> {job['company']}</p>
                <p><strong>Location:</strong> {job['location']}</p>
                <p><strong>Match: {job.get('match_score', 0)}%</strong></p>
                <a href="{job['apply_link']}" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Apply Now</a>
            </div>
            ''' for job in matched_jobs[:10]])}
            <hr>
            <p><a href="http://127.0.0.1:5000">View All Jobs</a></p>
        </body></html>
        """
        
        msg = Message(subject, recipients=[user_email], html=html_body)
        mail.send(msg)
        print(f"✓ Sent email to {user_email}")
        return True
    except Exception as e:
        print(f"✗ Email failed: {e}")
        return False

@app.route('/toggle-email-alerts', methods=['POST'])
@login_required
def toggle_email_alerts():
    """Toggle user's email alert preference."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    new_status = not current_user.email_alerts_enabled
    cursor.execute(
        "UPDATE users SET email_alerts_enabled = %s WHERE id = %s",
        (new_status, current_user.id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    status_text = "enabled" if new_status else "disabled"
    flash(f'Email alerts {status_text}!', 'success')
    return jsonify({'success': True, 'enabled': new_status})

@app.route('/test-email')
@login_required
def test_email():
    """Send a test email to the current user."""
    try:
        msg = Message(
            'Test Email from Job Crawler',
            recipients=[current_user.email],
            html=f'<h2>Test Email</h2><p>Hello {current_user.email}!</p><p>Email alerts are working!</p>'
        )
        mail.send(msg)
        flash('Test email sent! Check your inbox.', 'success')
    except Exception as e:
        flash(f'Email error: {str(e)}', 'error')
    
    return redirect(url_for('index'))
```

### Step 5: Update tasks.py for Automated Checking

Add this to `tasks.py`:

```python
from celery import shared_task
from app import app, get_db_connection, calculate_job_match_score, send_job_alert_email

@app.task
def check_and_send_job_alerts():
    """Check for new matching jobs and send emails to users who opted in."""
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Get all users with email alerts enabled
        cursor.execute("SELECT * FROM users WHERE email_alerts_enabled = TRUE AND skills IS NOT NULL")
        users = cursor.fetchall()
        
        sent_count = 0
        for user in users:
            user_skills = user['skills']
            if not user_skills:
                continue
            
            # Get jobs posted since last check (or all jobs if first time)
            if user['last_email_check']:
                cursor.execute("SELECT * FROM jobs WHERE created_at > %s", (user['last_email_check'],))
            else:
                cursor.execute("SELECT * FROM jobs")
            
            jobs = cursor.fetchall()
            
            # Find matching jobs
            matching_jobs = []
            for job in jobs:
                match_score, matched_skills = calculate_job_match_score(dict(job), user_skills)
                if match_score >= 25:  # Only send jobs with 25%+ match
                    job_dict = dict(job)
                    job_dict['match_score'] = match_score
                    job_dict['matched_skills'] = matched_skills
                    matching_jobs.append(job_dict)
            
            # Send email if there are matches
            if matching_jobs:
                if send_job_alert_email(user['email'], user_skills, matching_jobs):
                    sent_count += 1
                    # Update last check time
                    cursor.execute(
                        "UPDATE users SET last_email_check = NOW() WHERE id = %s",
                        (user['id'],)
                    )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Job alert check complete. Sent {sent_count} emails.")
        return f"Sent {sent_count} job alert emails"
```

### Step 6: Update Celery Beat Schedule

Update `tasks.py` to include the alert task in the schedule:

```python
celery.conf.beat_schedule = {
    'scrape-jobs-every-30-seconds': {
        'task': 'tasks.scrape_jobs_task',
        'schedule': 30.0,
    },
    'check-and-send-alerts-after-scrape': {
        'task': 'tasks.check_and_send_job_alerts',
        'schedule': 35.0,  # Runs 5 seconds after scraping
    },
}
```

### Step 7: Update index.html

Add the email alerts toggle back to the profile section. Add this after the resume upload form:

```html
<hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">

<div>
    <strong>📧 Email Job Alerts:</strong>
    <p style="font-size: 0.9rem; color: #666;">Get automatic emails when new jobs match your skills</p>
    <button id="toggleEmailAlerts" style="background-color: #17a2b8; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer;">
        <span id="emailAlertStatus">{{ 'Disable' if current_user.email_alerts_enabled else 'Enable' }} Email Alerts</span>
    </button>
    <a href="/test-email" style="margin-left: 10px; color: #007bff; text-decoration: none;">Send Test Email</a>
    <p id="emailAlertMessage" style="margin-top: 5px; font-size: 0.85rem; color: #666;"></p>
</div>
```

And add this JavaScript:

```javascript
document.getElementById('toggleEmailAlerts').addEventListener('click', async () => {
    try {
        const response = await fetch('/toggle-email-alerts', { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            location.reload();
        }
    } catch (error) {
        console.error('Error:', error);
    }
});
```

## 🎯 How It Works

1. **User enables alerts** - Toggles preference in database
2. **Celery scrapes jobs** - Every 30 seconds (or your schedule)
3. **Celery checks matches** - Runs alert task after scraping
4. **Emails are sent** - To users with matching jobs (25%+ match)
5. **Track sent jobs** - Updates last_email_check timestamp

## 🧪 Test It

1. Set up email credentials
2. Update database: `python database_setup.py`
3. Enable email alerts in UI
4. Click "Send Test Email" to verify
5. Let the system run and watch for automated emails!

## 🎉 Result

Your app now:
- Scrapes jobs automatically
- Matches them to user skills
- Sends email alerts proactively
- Tracks what's been sent
- Keeps users informed of new opportunities

**Your job crawler is now a personal job agent!** 🚀

