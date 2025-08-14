#!/bin/bash

# Pet Shop Application Setup Script
echo " Setting up Pet Shop Application..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo " Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo " Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo " Docker and Docker Compose are available"

# Build and start services
echo " Building Docker images..."
docker-compose build

echo " Starting services..."
docker-compose up -d

# Wait for services to be ready
echo " Waiting for services to start..."
sleep 30

# Run database migrations
echo " Setting up database..."
docker-compose exec -T web python manage.py migrate

# Create sample data
echo " Creating sample data..."
docker-compose exec -T web python manage.py populate_data

# Create static files directory
echo " Setting up static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

echo " Setup complete!"
echo ""
echo " Application is running at:"
echo "   Frontend: http://localhost"
echo "   Admin: http://localhost/admin"
echo "   Health Check: http://localhost/health/"
echo ""
echo " Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo ""
echo " Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart" 