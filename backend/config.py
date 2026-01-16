import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY", "")

# Server Configuration
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "3000"))

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/economic_advisor.db")

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai or openrouter
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# API Endpoints
FRED_BASE_URL = "https://api.stlouisfed.org/fred"
NEWS_API_BASE_URL = "https://newsapi.org/v2"
EXCHANGE_RATE_BASE_URL = "https://api.exchangerate-api.com/v4"
