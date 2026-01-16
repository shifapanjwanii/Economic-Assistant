#!/bin/bash

# Economic Decision Advisor - Setup Script

echo "=========================================="
echo "Economic Decision Advisor Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "✓ Node.js found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit the .env file and add your API keys:"
    echo "   - OPENAI_API_KEY (required)"
    echo "   - FRED_API_KEY (required - get from https://fred.stlouisfed.org/docs/api/api_key.html)"
    echo "   - NEWS_API_KEY (required - get from https://newsapi.org/)"
    echo "   - EXCHANGE_RATE_API_KEY (optional - or use free tier)"
    echo ""
else
    echo "✓ .env file already exists"
fi

# Setup Backend
echo ""
echo "Setting up backend..."
echo "---"

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Backend dependencies installed"

cd ..

# Setup Frontend
echo ""
echo "Setting up frontend..."
echo "---"

cd frontend

echo "Installing Node.js dependencies..."
npm install
echo "✓ Frontend dependencies installed"

cd ..

# Create data directory
mkdir -p data
echo "✓ Data directory created"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit the .env file and add your API keys"
echo "2. Start the backend: ./start-backend.sh"
echo "3. Start the frontend: ./start-frontend.sh"
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "For more information, see the README.md file"
echo ""
