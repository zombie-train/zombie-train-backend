#!/bin/sh

# Exit script on any error
set -e

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Start Gunicorn server
gunicorn --workers 2 --bind 0.0.0.0:8000 zombie_train_backend.wsgi:application