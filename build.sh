#!/bin/bash

# BLUE Project Build Script
echo "Building BLUE - Blockchain Analysis Tool..."

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

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit the .env file with your API keys and configuration."
fi

# Build Docker images
echo "Building Docker images..."
docker-compose build

echo "Build complete! To start the application, run: docker-compose up -d" 