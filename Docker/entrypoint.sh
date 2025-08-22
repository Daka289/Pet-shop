#!/bin/bash

# entrypoint.sh - Entry point script for Render deployment

# Don't exit on errors initially - we'll handle them gracefully
set +e

echo "Starting Pet Shop Application..."
echo "DEBUG: $(python -c 'import os; print(os.environ.get("DEBUG", "Not set"))')"
echo "DATABASE_URL: $(python -c 'import os; url=os.environ.get("DATABASE_URL", "Not set"); print(url[:30] + "..." if len(url) > 30 else url)')"

# Wait for database to be ready (with better error handling)
echo "Checking database connection..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petshop.settings')
django.setup()
from django.db import connections
try:
    connections['default'].ensure_connection()
    print('Database connection successful!')
except Exception as e:
    print(f'Database connection failed: {e}')
    print('Continuing anyway - migrations will handle this...')
" || echo "Database check failed, but continuing..."

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput || echo "Migrations failed, but continuing..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || echo "Static files collection failed, but continuing..."

# Create superuser if it doesn't exist (simplified)
echo "Creating superuser if needed..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petshop.settings')
django.setup()
from django.contrib.auth import get_user_model
try:
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@petshop.com', 'admin123')
        print('Admin user created successfully!')
    else:
        print('Admin user already exists')
except Exception as e:
    print(f'Could not create admin user: {e}')
" || echo "Superuser creation skipped"

# Skip data population for now to avoid issues
echo "Skipping data population for faster startup..."

echo "Setup complete! Starting application..."

# Start the application
exec "$@"