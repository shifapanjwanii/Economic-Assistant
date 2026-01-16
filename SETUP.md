# Setup and Installation Guide

## Prerequisites

Before setting up the Economic Decision Advisor, ensure you have:

1. **Python 3.8+** installed ([Download](https://www.python.org/downloads/))
2. **Node.js 16+** and npm installed ([Download](https://nodejs.org/))
3. **API Keys** (see below for how to obtain)

## Required API Keys

### 1. OpenAI API Key (Required)
- Sign up at [OpenAI](https://platform.openai.com/)
- Navigate to API Keys section
- Create a new secret key
- **Cost**: Pay-as-you-go (GPT-4 is ~$0.03 per 1K tokens)

### 2. FRED API Key (Required)
- Visit [FRED API Documentation](https://fred.stlouisfed.org/docs/api/api_key.html)
- Request an API key (free)
- Approve via email confirmation
- **Cost**: Free

### 3. NewsAPI Key (Required)
- Sign up at [NewsAPI](https://newsapi.org/)
- Get your API key from the dashboard
- **Cost**: Free tier (100 requests/day) or paid plans
- **Note**: Free tier may have limitations on article age

### 4. Exchange Rate API Key (Optional)
- The app uses [ExchangeRate-API](https://www.exchangerate-api.com/)
- Free tier available without key (limited requests)
- Sign up for a key for higher limits
- **Cost**: Free tier available

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Make setup script executable
chmod +x setup.sh start-backend.sh start-frontend.sh

# Run setup
./setup.sh

# Edit .env file with your API keys
nano .env  # or use your preferred editor

# Start backend (in one terminal)
./start-backend.sh

# Start frontend (in another terminal)
./start-frontend.sh
```

### Option 2: Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Go back to root directory
cd ..
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Go back to root directory
cd ..
```

#### Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

#### Running the Application

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
python main.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

## Verification

1. **Backend**: Open http://localhost:8000/health
   - Should return: `{"status": "healthy", "timestamp": "..."}`

2. **Frontend**: Open http://localhost:3000
   - Should display the chat interface

3. **Full Test**: Send a message in the chat interface
   - Try: "What is the current inflation rate?"

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError`
```bash
# Make sure virtual environment is activated
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

**Issue**: `OPENAI_API_KEY not configured`
- Ensure `.env` file exists in root directory
- Verify API key is correct and has no extra spaces
- Check that the key starts with `sk-`

**Issue**: `FRED API key not configured`
- Get a free key from FRED (see above)
- Add to `.env` file

### Frontend Issues

**Issue**: `Cannot connect to backend`
- Ensure backend is running on port 8000
- Check `proxy` setting in `frontend/package.json`

**Issue**: Dependencies not installing
```bash
# Clear npm cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database Issues

**Issue**: Database errors
```bash
# Remove and recreate database
rm -rf data/
mkdir data
# Restart backend - it will recreate the database
```

## Project Structure

```
Economic-Assistant/
├── README.md                    # Project overview and documentation
├── SETUP.md                     # This file
├── .env.example                 # Environment variables template
├── .env                         # Your API keys (create this)
├── .gitignore                   # Git ignore rules
├── setup.sh                     # Automated setup script
├── start-backend.sh             # Backend start script
├── start-frontend.sh            # Frontend start script
│
├── backend/                     # Python FastAPI backend
│   ├── main.py                  # FastAPI server entry point
│   ├── config.py                # Configuration management
│   ├── requirements.txt         # Python dependencies
│   │
│   ├── agent/                   # Agent reasoning system
│   │   └── economic_agent.py    # Main agentic loop
│   │
│   ├── services/                # External API integrations
│   │   ├── api_services.py      # FRED, News, Exchange Rate APIs
│   │   └── memory_service.py    # SQLite memory management
│   │
│   └── models/                  # Data models
│       └── schemas.py           # Pydantic schemas
│
├── frontend/                    # React frontend
│   ├── package.json             # Node dependencies
│   ├── public/
│   │   └── index.html           # HTML template
│   │
│   └── src/
│       ├── index.js             # React entry point
│       ├── App.js               # Main chat component
│       ├── App.css              # Styling
│       └── index.css            # Global styles
│
└── data/                        # SQLite database (auto-created)
    └── economic_advisor.db
```

## Testing the Agent

Try these example queries to test different capabilities:

### Economic Data Queries
- "What is the current inflation rate?"
- "How has unemployment changed recently?"
- "What are the current interest rates?"

### News Queries
- "What recent economic news should I know about?"
- "Show me news about inflation"
- "What's happening with the Federal Reserve?"

### Decision Support
- "Is now a good time to save or pay down debt?"
- "How does current inflation affect my purchasing power?"
- "Should I be concerned about the economic situation?"

### Currency Queries
- "What is the USD to EUR exchange rate?"
- "Compare purchasing power between USD and GBP"

## Development Notes

### Backend Development

To add new tools/capabilities:
1. Add new methods to appropriate service in `services/`
2. Register tool in `agent/economic_agent.py` tools list
3. Add execution logic in `execute_tool()` method

### Frontend Development

The frontend uses:
- **React 18** with hooks
- **Axios** for API calls
- **ReactMarkdown** for rendering agent responses
- **Lucide React** for icons

To modify the UI, edit `frontend/src/App.js` and `frontend/src/App.css`

### Database Schema

The SQLite database has three tables:
- `user_profiles`: User financial information
- `conversations`: Chat history
- `decisions`: Decision log for reflection

## Security Notes

⚠️ **Important Security Considerations**:

1. **Never commit `.env` file** - Contains sensitive API keys
2. **API Key Limits** - Monitor your usage to avoid unexpected costs
3. **Rate Limiting** - APIs have rate limits; the app handles basic errors
4. **Data Privacy** - User conversations are stored locally in SQLite

## Production Deployment

For production deployment, you would need to:

1. Use a production-grade database (PostgreSQL)
2. Add authentication and user management
3. Implement rate limiting
4. Add monitoring and logging
5. Use environment-specific configs
6. Deploy backend and frontend separately
7. Set up HTTPS
8. Implement proper error tracking

This is an educational project - additional work needed for production use.

## Support

For issues or questions:
1. Check this setup guide
2. Review the main README.md
3. Check API documentation for external services
4. Review error logs in terminal output

## License

Educational project - See main README.md for details.
