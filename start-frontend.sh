#!/bin/bash

echo "Starting Economic Decision Advisor Frontend..."
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  Warning: node_modules not found. Please run ./setup.sh first."
    exit 1
fi

# Run the frontend server
echo "Frontend server starting on http://localhost:3000"
echo "Press Ctrl+C to stop"
echo ""

npm start
