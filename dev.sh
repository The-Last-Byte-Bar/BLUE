#!/bin/bash

# BLUE Project Development Script
echo "Starting BLUE in development mode..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit the .env file with your API keys and configuration."
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Start backend in background
echo "Starting backend server..."
cd api
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8008 &
BACKEND_PID=$!
cd ..

# Start frontend in background
echo "Starting frontend server..."
cd frontend
PORT=3030 npm start &
FRONTEND_PID=$!
cd ..

# Function to handle script termination
function cleanup {
    echo "Stopping servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

echo "Development servers started!"
echo "- Frontend: http://localhost:3030"
echo "- Backend API: http://localhost:8008"
echo "Press Ctrl+C to stop the servers."

# Wait for user to press Ctrl+C
wait 