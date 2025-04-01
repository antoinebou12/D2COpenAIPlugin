#!/bin/bash

# Docker run script for D2COpenAIPlugin
# This script starts the application using Docker Compose

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Check if we need to build
if [ "$1" = "build" ]; then
  echo "Building Docker images..."
  docker-compose build
  shift
fi

# Start the services
echo "Starting services..."
docker-compose up -d

# Show status
echo "Services:"
docker-compose ps

# Show logs if requested
if [ "$1" = "logs" ]; then
  echo "Showing logs..."
  docker-compose logs -f
fi

echo "Services started successfully!"
echo "API server is available at: http://localhost:5003"
echo "PlantUML server is available at: http://localhost:8080"
echo "Kroki server is available at: http://localhost:8000"
echo ""
echo "To stop the services, run: docker-compose down"
echo "To view logs, run: docker-compose logs -f"
