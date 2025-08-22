#!/bin/bash

# entrypoint.sh - Entry point script for Render deployment

set -e  # Exit on any error

echo "Starting Pet Shop Application..."
echo "DEBUG: $(python -c 'import os; print(os.environ.get("DEBUG", "Not set"))')"
echo "DATABASE_URL: $(python -c 'import os; url=os.environ.get("DATABASE_URL", "Not set"); print(url[:30] + "..." if len(url) > 30 else url)')"

# Wait for database to be ready (optional, but good practice)
echo "Waiting for database to be ready..."
python << END
import time
import sys
import os
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.db import connections
from django.db.utils import OperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petshop.settings')
django.setup()

def wait_for_db():
    """Wait for database to be available"""
    max_tries = 30
    for i in range(max_tries):
        try:
            connections['default'].ensure_connection()
            print(" Database connection successful!")
            return True
        except OperationalError as e:
            print(f" Database not ready (attempt {i+1}/{max_tries}): {e}")
            if i < max_tries - 1:
                time.sleep(2)
            else:
                print(" Database connection failed after maximum attempts")
                sys.exit(1)

wait_for_db()
END

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist (optional)
echo "Creating superuser if needed..."
python manage.py shell << END || echo "Warning: Could not create superuser"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    print("Creating admin user...")
    User.objects.create_superuser(
        username='admin',
        email='admin@petshop.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print(" Admin user created!")
else:
    print("Info: Admin user already exists")
END

# Populate initial data if database is empty (optional)
echo "Checking for initial data..."
python manage.py shell << END || echo "Warning: Could not populate initial data"
from shop.models import Category, Product
if not Category.objects.exists():
    print("Database seems empty, running data population...")
    try:
        from django.core.management import call_command
        call_command('populate_data')
        print(" Initial data populated!")
    except Exception as e:
        print(f" Could not populate data: {e}")
else:
    print("Info: Database already has data")
END

echo "Setup complete! Starting application..."

# Start the application
exec "$@"