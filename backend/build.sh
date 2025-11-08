#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Skip migrations during build to avoid SSL issues
# python manage.py migrate

# Collect static files  
python manage.py collectstatic --noinput --clear