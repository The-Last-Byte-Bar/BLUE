#!/bin/bash

# BLUE Project Cleanup Script
echo "Cleaning up BLUE - Blockchain Analysis Tool..."

# Stop and remove containers
echo "Stopping and removing Docker containers..."
docker-compose down

# Remove Docker images
echo "Removing Docker images..."
docker rmi $(docker images -q blue_frontend blue_backend 2>/dev/null) 2>/dev/null || true

# Remove Docker volumes
echo "Removing Docker volumes..."
docker volume prune -f

# Remove node_modules
echo "Removing node_modules..."
rm -rf frontend/node_modules

# Remove Python cache
echo "Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

echo "Cleanup complete!" 