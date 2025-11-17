# Deployment Guide

This guide covers deploying the Job Crawler application to production.

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (or use Docker)
- Redis server (or use Docker)
- Domain name (optional, for production)
- SSL certificate (for HTTPS in production)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@host:5432/job_crawler_db
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=job_crawler_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Flask Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
FLASK_ENV=production
PORT=5001

# Email Configuration (Optional)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

## Docker Deployment

### 1. Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Initialize Database

```bash
# Run database setup
docker-compose exec web python database_setup.py
```

### 3. Access the Application

- Web interface: http://localhost:5001
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Production Deployment

### Option 1: Docker Compose on Server

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd jobcrawlerprototype
   ```

2. **Set up environment:**
   ```bash
   cp env.example .env
   # Edit .env with production values
   ```

3. **Build and deploy:**
   ```bash
   docker-compose -f docker-compose.yml up -d --build
   ```

4. **Initialize database:**
   ```bash
   docker-compose exec web python database_setup.py
   ```

5. **Set up reverse proxy (Nginx):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:5001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

### Option 2: Cloud Platform (AWS, GCP, Azure)

#### AWS (ECS/EKS)
1. Push Docker image to ECR
2. Create ECS task definition
3. Create ECS service with load balancer
4. Configure RDS for PostgreSQL
5. Configure ElastiCache for Redis

#### Google Cloud Platform
1. Push Docker image to Container Registry
2. Deploy to Cloud Run or GKE
3. Use Cloud SQL for PostgreSQL
4. Use Memorystore for Redis

#### Azure
1. Push Docker image to Container Registry
2. Deploy to Container Instances or AKS
3. Use Azure Database for PostgreSQL
4. Use Azure Cache for Redis

## Database Setup

### Initial Setup

```bash
# Run database setup script
python database_setup.py
```

### Migrations

For production, consider using Alembic for database migrations:

```bash
pip install alembic
alembic init alembic
# Configure Alembic and create migrations
```

## Security Considerations

1. **Change SECRET_KEY:** Use a strong, random secret key in production
2. **Use HTTPS:** Always use HTTPS in production (use Let's Encrypt)
3. **Database Security:** Use strong passwords and restrict access
4. **Environment Variables:** Never commit `.env` file to version control
5. **Firewall:** Restrict database and Redis access to application servers only
6. **Regular Updates:** Keep dependencies updated for security patches

## Monitoring

### Health Checks

The application includes a health check endpoint. Monitor:
- Application health: `GET /`
- Database connectivity
- Redis connectivity
- Celery worker status

### Logging

Logs are available via:
```bash
# Docker logs
docker-compose logs -f web
docker-compose logs -f worker
docker-compose logs -f beat

# Application logs
tail -f app.log
tail -f celery-worker.log
tail -f celery-beat.log
```

### Metrics

Consider integrating:
- Prometheus for metrics
- Grafana for visualization
- Sentry for error tracking

## Scaling

### Horizontal Scaling

1. **Web Servers:** Run multiple web containers behind a load balancer
2. **Workers:** Scale Celery workers based on job queue size
3. **Database:** Use read replicas for read-heavy workloads

### Vertical Scaling

1. Increase container resources (CPU, memory)
2. Optimize database queries
3. Use connection pooling

## Backup and Recovery

### Database Backups

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U username job_crawler_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U username job_crawler_db < backup.sql
```

### Automated Backups

Set up cron job or scheduled task for regular backups:
```bash
0 2 * * * docker-compose exec postgres pg_dump -U username job_crawler_db > /backups/backup-$(date +\%Y\%m\%d).sql
```

## Troubleshooting

### Common Issues

1. **Database connection errors:**
   - Check database credentials
   - Verify database is running
   - Check network connectivity

2. **Redis connection errors:**
   - Check Redis is running
   - Verify Redis URL

3. **Celery worker not processing jobs:**
   - Check worker logs
   - Verify Redis connection
   - Check task registration

4. **File upload issues:**
   - Check uploads directory permissions
   - Verify disk space
   - Check file size limits

## Testing in Production

Before deploying to production:

1. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

2. **Check code coverage:**
   ```bash
   pytest --cov=app --cov-report=html
   ```

3. **Load testing:**
   - Use tools like Apache Bench or Locust
   - Test with realistic load

4. **Security scanning:**
   - Run security audits
   - Check for vulnerabilities in dependencies

## CI/CD Pipeline

The project includes GitHub Actions workflow for:
- Automated testing
- Code quality checks
- Docker image building
- Deployment automation

Configure secrets in GitHub repository settings:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_KEY`

## Support

For issues or questions:
1. Check logs for errors
2. Review this documentation
3. Check GitHub issues
4. Contact support team

