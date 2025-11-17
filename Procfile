web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120
worker: celery -A tasks worker --loglevel=info --concurrency=2
beat: celery -A tasks beat --loglevel=info

