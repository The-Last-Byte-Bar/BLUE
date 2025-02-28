#!/bin/bash

# BLUE Project Test Script
echo "Running tests for BLUE - Blockchain Analysis Tool..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit the .env file with your API keys and configuration."
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Run backend tests
echo "Running backend tests..."
python -m pytest tests/

# Run frontend tests
echo "Running frontend tests..."
cd frontend
npm test
cd ..

echo "Tests completed!" 