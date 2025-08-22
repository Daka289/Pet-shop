# Use official Python runtime as base image
FROM python:3.11-slim

# Set metadata labels   
LABEL maintainer="Pet Shop Team"
LABEL version="1.0"
LABEL description="Django Pet Shop Application"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=petshop.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (security best practice)
RUN groupadd -r django && useradd -r -g django django

# Copy requirements first (Docker layer caching optimization)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy entrypoint scripts and make them executable (do this as root)
COPY entrypoint.sh /app/entrypoint.sh
COPY entrypoint-simple.sh /app/entrypoint-simple.sh
RUN chmod +x /app/entrypoint.sh /app/entrypoint-simple.sh

# Copy project files
COPY . /app/

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

# Change ownership to django user (including entrypoint script)
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Health check (additional option)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Set entrypoint (using simple version for testing)
ENTRYPOINT ["/app/entrypoint-simple.sh"]

# Default command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "petshop.wsgi:application"] 