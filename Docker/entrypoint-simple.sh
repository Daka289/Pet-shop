#!/bin/bash

# Simple entrypoint script for testing
echo "=== Pet Shop Simple Startup ==="

# Basic environment check
echo "DEBUG: ${DEBUG:-not-set}"
echo "DATABASE_URL: ${DATABASE_URL:0:30}..."

# Try migrations (don't fail if it doesn't work)
echo "Attempting migrations..."
python manage.py migrate --noinput 2>/dev/null || echo "Migrations skipped"

# Try static files (don't fail if it doesn't work)
echo "Attempting static files collection..."
python manage.py collectstatic --noinput 2>/dev/null || echo "Static files skipped"

echo "Starting application..."
exec "$@"
