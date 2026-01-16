#!/bin/bash

echo "Starting Economic Decision Advisor Backend..."
echo ""

cd backend

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ../.env ]; then
    echo "⚠️  Warning: .env file not found. Please run ./setup.sh first."
    exit 1
fi

# Run the backend server
echo "Backend server starting on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

python main.py
