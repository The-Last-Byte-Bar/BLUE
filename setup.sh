#!/bin/bash

# BLUE Project Setup Script
echo "Setting up BLUE - Blockchain Analysis Tool..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit https://docs.docker.com/compose/install/ for installation instructions."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit the .env file with your API keys and configuration."
fi

# Build and start the containers
echo "Building and starting Docker containers..."
docker-compose up -d --build

echo "Setup complete! The application should be running at:"
echo "- Frontend: http://localhost:3030"
echo "- Backend API: http://localhost:8008"
echo ""
echo "To stop the application, run: docker-compose down" 