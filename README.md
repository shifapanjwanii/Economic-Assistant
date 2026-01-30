# Pulse — An AI-Powered Economic Decision Assistant

## Project Overview

**Pulse** is an intelligent agentic AI system that helps users make informed everyday economic and financial decisions by analyzing real-time macroeconomic data. Built with a React frontend and FastAPI backend, Pulse leverages large language models (LLMs) to autonomously reason about user queries, fetch relevant economic data, and provide personalized financial guidance.

The system implements a complete **Reason-Act-Observe-Reflect** loop where the AI agent dynamically determines which data sources to query, orchestrates API calls, interprets results, and synthesizes evidence-based recommendations tailored to each user's financial profile and goals.

## Core Features

### 🤖 Agentic AI System

Pulse implements an autonomous agent architecture with four key phases:

1. **Reason**: The LLM analyzes user queries to determine relevant data sources and information needs
2. **Act**: The agent dynamically selects and invokes appropriate tools (FRED API, NewsAPI, Exchange Rates)
3. **Observe**: Retrieved data is integrated and interpreted for patterns and insights
4. **Reflect**: All observations are synthesized into coherent, personalized recommendations

The agent iteratively loops through these phases until it can provide a comprehensive response, with transparency into which tools were used and how many reasoning iterations occurred.

### 📊 Real-Time Economic Dashboard

Interactive dashboard displaying:
- **Key Economic Indicators**: Real-time data on inflation (CPI), unemployment rate, Federal Funds Rate, and GDP growth from FRED
- **Economic News Feed**: Latest financial news articles relevant to current economic conditions
- **Exchange Rates**: Live currency exchange rates with historical trend charts
- **Historical Visualizations**: Interactive line charts showing currency trends over the past year (365 days)
- **Auto-refresh**: Data updates every 5 minutes to stay current

### 💬 Conversational Chat Interface

- **Natural language queries**: Ask questions in plain English about economic conditions and personal finance decisions
- **Persistent conversation history**: All interactions are saved and retrievable
- **Real-time typing indicators**: Visual feedback during agent processing
- **Tool usage transparency**: See which data sources the agent consulted for each response
- **Markdown rendering**: Rich text formatting for clear, readable responses
- **Message timestamps**: Track when each interaction occurred
- **Clear history option**: Ability to wipe conversation history and start fresh

### 👤 User Profile & Personalization

Comprehensive user profiles that enable personalized guidance:

**Financial Context:**
- Annual income range
- Current debt level
- Number of dependents
- Risk tolerance (conservative, moderate, aggressive)

**Goals Tracking:**
- Short-term goals (emergency fund, debt payoff, travel savings, etc.)
- Long-term goals (home purchase, retirement, education fund, wealth building, etc.)

**Preferences:**
- **Explanation Depth**: Choose between brief, moderate, or detailed responses
- **Focus Areas**: Select topics of interest (inflation, interest rates, employment, housing market, debt management, retirement, currency/exchange rates)

The agent uses this profile to:
- Tailor recommendations to your specific situation
- Adjust response verbosity based on preferences
- Prioritize relevant data sources
- Maintain context across conversations

### 🧠 Long-Term Memory System

SQLite-based memory storage that persists:
- **User Profiles**: Complete financial context and preferences
- **Conversation History**: Full record of all user queries and agent responses
- **Decision Logs**: Track of recommendations and whether users acted on them
- **Tools Used**: Record of which data sources were consulted for each query

Memory enables the agent to:
- Remember previous interactions and build continuity
- Reference past advice and avoid repetition
- Detect changes in user circumstances
- Provide increasingly personalized guidance over time

## Data Sources & Tools

The agent integrates three primary external data sources, each accessible via dedicated tool functions:

### 1. Federal Reserve Economic Data (FRED) API

**Available Tools:**
- `get_inflation_data()`: Current CPI inflation rate (year-over-year percentage change)
- `get_unemployment_rate()`: Current U.S. unemployment rate
- `get_interest_rates()`: Current Federal Funds Rate
- `get_gdp_growth()`: Real GDP growth rate (adjusted for inflation)
- `get_historical_exchange_rates(currency, days)`: Historical currency data for trend analysis

**Why It's Valuable:**  
FRED provides authoritative, regularly updated macroeconomic data from the U.S. Federal Reserve. This data directly affects personal financial decisions around saving, borrowing, and spending.

**Example Use Cases:**
- "Is now a good time to save or pay down debt?" → Agent fetches real interest rates and inflation
- "How has the economy changed in the last year?" → Agent pulls historical GDP and unemployment data

### 2. Financial News API (NewsAPI)

**Available Tools:**
- `get_economic_news(query)`: Real-time economic and financial news headlines

**Why It's Valuable:**  
News captures market sentiment, policy announcements, and emerging economic risks not yet reflected in historical data. Provides narrative context for economic trends.

**Example Use Cases:**
- "What recent economic news should influence my spending?" → Agent retrieves headlines on inflation, employment, Fed policy
- "Is there anything I should know about the job market?" → Agent searches for employment-related news

### 3. Currency & Exchange Rate API

**Available Tools:**
- `get_exchange_rates(base_currency)`: Current exchange rates for all major currencies
- `compare_purchasing_power(amount, from_currency, to_currency)`: Compare purchasing power across currencies

**Why It's Valuable:**  
Exchange rates affect the real value of savings, import costs, and international investments. Essential for understanding purchasing power in a global context.

**Example Use Cases:**
- "How does inflation affect my purchasing power?" → Agent compares currency values and inflation impact
- "Should I exchange currency now or wait?" → Agent analyzes current rates and recent trends

## API Endpoints

The FastAPI backend provides the following REST endpoints:

### Chat & Agent
- `POST /api/chat` - Process user query through the economic agent
  - Request: `{ "user_id": string, "message": string }`
  - Response: `{ "response": string, "tools_used": string[], "iterations": int, "timestamp": string }`

### User Profile
- `GET /api/users/{user_id}/profile` - Retrieve user profile
- `POST /api/users/{user_id}/profile` - Create or update user profile

### Conversation History
- `GET /api/users/{user_id}/history?limit={n}` - Get conversation history
- `DELETE /api/users/{user_id}/history` - Clear conversation history

### Dashboard Data
- `GET /api/dashboard` - Get aggregated economic indicators, news, and exchange rates
- `GET /api/exchange-rates/historical/{currency}?days={n}` - Get historical exchange rate data

### Health & Status
- `GET /` - Root endpoint with API info
- `GET /health` - Health check with timestamp

## Technology Stack

### Backend
- **Framework**: FastAPI (Python) - Modern, fast web framework for building APIs
- **LLM Integration**: OpenAI GPT-4/GPT-4o via AsyncOpenAI client (compatible with OpenRouter)
- **Database**: SQLite with aiosqlite for async operations
- **Data Validation**: Pydantic models for request/response schemas
- **HTTP Client**: httpx for async API calls to external services
- **CORS**: Configured for local development (React frontend at localhost:3000)

### Frontend
- **Framework**: React 18 with functional components and hooks
- **HTTP Client**: Axios for API communication
- **Markdown Rendering**: react-markdown for rich text responses
- **Charts**: Recharts for interactive data visualizations
- **Icons**: Lucide React icon library
- **Styling**: Custom CSS with responsive design

### Data Sources
- **FRED API**: Federal Reserve Economic Data
- **NewsAPI**: Financial news aggregation
- **Exchange Rate API**: Real-time currency data

### Development Tools
- **Package Management**: npm (frontend), pip (backend)
- **Shell Scripts**: Automated setup and startup scripts
- **Environment Variables**: `.env` file for API keys and configuration

## Project Structure

```
Economic-Assistant/
├── backend/
│   ├── main.py                 # FastAPI application & endpoints
│   ├── config.py              # Configuration & environment variables
│   ├── requirements.txt       # Python dependencies
│   ├── agent/
│   │   ├── economic_agent.py  # Core agentic loop implementation
│   ├── services/
│   │   ├── api_services.py    # FRED, NewsAPI, Exchange Rate services
│   │   ├── memory_service.py  # SQLite-based memory management
│   ├── models/
│   │   ├── schemas.py         # Pydantic data models
│   └── data/
│       └── memory.db          # SQLite database (auto-created)
├── frontend/
│   ├── src/
│   │   ├── App.js             # Main chat interface
│   │   ├── Dashboard.js       # Economic dashboard view
│   │   ├── ProfileModal.js    # User profile editor
│   │   ├── index.js           # React entry point
│   │   └── *.css              # Component styles
│   ├── public/
│   ├── package.json           # Node dependencies
│   └── build/                 # Production build output
├── setup.sh                   # Automated setup script
├── start-backend.sh          # Backend startup script
├── start-frontend.sh         # Frontend startup script
├── .env                      # Environment variables (create from .env.example)
├── README.md                 # This file
└── SETUP.md                  # Installation instructions
```

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+ and npm
- API Keys:
  - OpenAI API key (or OpenRouter API key)
  - FRED API key (free at https://fred.stlouisfed.org/docs/api/api_key.html)
  - NewsAPI key (free at https://newsapi.org/register)
  - Exchange Rate API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Economic-Assistant
   ```

2. **Configure environment variables**
   - Copy `.env.example` to `.env` (if available) or create `.env` file
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_key
     FRED_API_KEY=your_fred_key
     NEWS_API_KEY=your_news_api_key
     EXCHANGE_RATE_API_KEY=your_exchange_rate_key
     ```

3. **Run automated setup**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   This script will:
   - Install Python dependencies
   - Install Node.js dependencies
   - Initialize the SQLite database
   - Verify configuration

### Running the Application

**Option 1: Using startup scripts**
```bash
# Terminal 1 - Backend
./start-backend.sh

# Terminal 2 - Frontend
./start-frontend.sh
```

**Option 2: Manual startup**
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (interactive Swagger UI)

### First Steps

1. Open http://localhost:3000 in your browser
2. Click the profile icon to set up your financial profile
3. Start chatting with Pulse about economic decisions
4. Switch to the Dashboard tab to view real-time economic indicators

## Example Use Cases

### 1. Debt vs. Savings Decision
**User**: "Is now a good time to prioritize saving or paying down debt?"

**What Pulse Does**:
- Retrieves your financial profile (debt level, risk tolerance, goals)
- Fetches current interest rates and inflation from FRED
- Analyzes real interest rate (nominal rate minus inflation)
- Compares your debt interest rate against potential savings returns
- Provides personalized recommendation based on your specific situation

### 2. Understanding Inflation Impact
**User**: "How does current inflation affect my purchasing power?"

**What Pulse Does**:
- Gets latest inflation data from FRED
- Reviews your focus areas from profile (e.g., housing, groceries)
- Searches for sector-specific inflation news
- Calculates real purchasing power change
- Explains practical impact on your budget categories

### 3. Economic News Briefing
**User**: "What recent economic news should I know about?"

**What Pulse Does**:
- Queries NewsAPI for latest financial headlines
- Filters news based on your profile focus areas
- Cross-references news with FRED data for context
- Summarizes most relevant developments
- Explains implications for your financial decisions

### 4. Currency and Travel Planning
**User**: "Should I exchange currency now or wait for my trip next month?"

**What Pulse Does**:
- Fetches current exchange rates
- Retrieves historical trend data (charts on dashboard)
- Analyzes recent currency volatility
- Considers economic news affecting exchange rates
- Provides timing recommendation with rationale

### 5. Personalized Economic Analysis
**User**: "Given my situation, what economic indicators should I watch?"

**What Pulse Does**:
- Reviews your complete financial profile
- Identifies most relevant economic metrics based on your goals
- Explains why each indicator matters to you specifically
- Sets context for ongoing monitoring
- Suggests actions based on indicator changes

## Configuration

### Backend Configuration (config.py)

The backend uses environment variables for configuration. Key settings include:

```python
# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = "gpt-4o"  # or "gpt-4"
LLM_TEMPERATURE = 0.7
LLM_PROVIDER = "openai"  # or "openrouter"

# API Keys
FRED_API_KEY = os.getenv("FRED_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

# Database
DATABASE_PATH = "./data/memory.db"

# Server
BACKEND_PORT = 8000
```

### Frontend Configuration

Update `REACT_APP_API_URL` in your environment or directly in the code if needed:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

## Key Design Decisions

### Agentic Architecture
- **Autonomous Tool Selection**: The LLM dynamically chooses which APIs to call rather than following predefined rules
- **Iterative Reasoning**: Agent loops up to 5 times to gather sufficient context before responding
- **Tool Transparency**: Users see which data sources were consulted for each answer

### Memory Management
- **Conversation Persistence**: All chats saved to SQLite for continuity
- **Profile-Driven Personalization**: Every response considers user's financial context
- **Explanation Depth Preference**: Users control response verbosity (brief/moderate/detailed)

### User Experience
- **Dual Interface**: Chat for conversations, Dashboard for data exploration
- **Real-Time Updates**: Dashboard auto-refreshes economic indicators
- **Interactive Visualizations**: Historical charts for deeper trend analysis
- **Profile Management**: Easy-to-use modal for updating financial information

## Limitations & Disclaimers

⚠️ **Important**: Pulse is designed for educational purposes and general economic understanding. It is **NOT** a substitute for professional financial advice.

**Current Limitations:**
- Does not provide specific investment recommendations or stock picks
- Economic data has inherent lag (GDP is quarterly, some indicators are monthly)
- News sentiment analysis is based on headline availability, not deep analysis
- Cannot access real-time market data or user-specific account information
- Recommendations are generalized and may not account for all personal factors

**Use Responsibly:**
- Always verify important financial decisions with qualified professionals
- Be aware that economic conditions can change rapidly
- Consider multiple sources of information before making financial choices
- Understand that past economic patterns don't guarantee future outcomes

## Contributing

This project welcomes contributions! Areas for improvement include:

- **Additional Data Sources**: Integration with more economic APIs
- **Enhanced Visualizations**: More chart types and data analysis features
- **Mobile Responsiveness**: Better mobile UI/UX
- **Advanced Memory**: Improved context tracking and decision logging
- **Multi-User Support**: Authentication and user management
- **Export Features**: Ability to export conversation history and insights
- **Testing**: Comprehensive test coverage for backend and frontend

## Acknowledgments

- **FRED API**: Federal Reserve Bank of St. Louis for comprehensive economic data
- **NewsAPI**: For real-time financial news aggregation
- **OpenAI**: For GPT-4 LLM capabilities
- **React & FastAPI Communities**: For excellent documentation and tools
