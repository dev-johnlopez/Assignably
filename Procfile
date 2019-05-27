web: flask db upgrade; gunicorn assignably:app
worker: rq worker -u $REDIS_URL assignably-tasks
