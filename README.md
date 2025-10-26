# Job Crawler Bot 🤖

Automated job search system with personalized matching and email alerts.

## Features

✅ **Resume Upload** - Upload your CV and extract skills automatically  
✅ **Personalized Matching** - Find jobs that match your skills  
✅ **Email Alerts** - Get notified when new matching jobs are found  
✅ **Real-Time Scraping** - Jobs are updated every 30 seconds  
✅ **Match Scores** - See how well jobs match your profile  

## Quick Start

### 1. Setup (First Time Only)

```bash
# Make scripts executable
chmod +x setup.sh start_app.sh stop_app.sh

# Run setup
./setup.sh
```

### 2. Configure Email Alerts (Optional but Recommended)

Create a `.env` file in the project root:

```bash
# .env
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

**To get a Gmail App Password:**
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Enter "Job Crawler Bot"
4. Click "Generate"
5. Copy the 16-digit password and paste it in `.env`

### 3. Start the Application

```bash
./start_app.sh
```

Your app will be available at: **http://127.0.0.1:5001**

### 4. Stop the Application

```bash
./stop_app.sh
```

## Manual Setup (Alternative)

If you prefer to run commands manually:

### Terminal 1: Flask App
```bash
source venv/bin/activate
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
python app.py
```

### Terminal 2: Celery Worker
```bash
source venv/bin/activate
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
python -m celery -A tasks worker --loglevel INFO
```

### Terminal 3: Celery Scheduler
```bash
source venv/bin/activate
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
python -m celery -A tasks beat --loglevel INFO
```

### Terminal 4: Redis (if not installed)
```bash
redis-server
```

## Usage

1. **Register/Login** - Create an account or login
2. **Upload Resume** - Upload your CV to extract your skills
3. **Enable Email Alerts** - Toggle email alerts in your profile
4. **Browse Jobs** - Search for jobs or click "Show Personalized Matches"
5. **Apply** - Click "Apply Now" to visit the job posting on Indeed.com

## Project Structure

```
jobcrawlerprototype/
├── app.py              # Flask application
├── tasks.py            # Celery tasks (scraping & alerts)
├── config.py           # Configuration
├── database_setup.py  # Database setup
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
├── uploads/            # Resume uploads
└── *.sh                # Startup scripts
```

## Technologies

- **Flask** - Web framework
- **PostgreSQL** - Database
- **Redis** - Task queue
- **Celery** - Background jobs
- **Flask-Mail** - Email sending
- **spaCy** - NLP for skill extraction
- **PyPDF2** - PDF parsing
- **python-docx** - DOCX parsing

## System Requirements

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- 2GB RAM minimum

## Troubleshooting

### Port 5001 already in use
```bash
# Kill the process using port 5001
lsof -ti:5001 | xargs kill
```

### Email not working
- Verify your Gmail App Password is correct
- Check that environment variables are set
- See logs: `tail -f celery-worker.log`

### Database connection error
- Ensure PostgreSQL is running: `pgrep -l postgres`
- Check database credentials in `config.py`

## License

MIT License
