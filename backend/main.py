from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import config
from models.schemas import (
    ChatRequest, 
    ChatResponse, 
    UserProfile,
    UserProfileResponse,
    ConversationHistoryResponse
)
from agent.economic_agent import EconomicAgent
from services.memory_service import MemoryService
from services.api_services import FREDService, NewsAPIService, ExchangeRateService


# Initialize services
memory_service = MemoryService()
agent = EconomicAgent()
fred_service = FREDService()
news_service = NewsAPIService()
exchange_rate_service = ExchangeRateService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    await memory_service.initialize_database()
    yield


# Create FastAPI app
app = FastAPI(
    title="Pulse API",
    description="Agentic AI system for economic decision-making",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Pulse API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a user query through the economic agent
    """
    try:
        # Ensure user profile exists
        profile = await memory_service.get_user_profile(request.user_id)
        if not profile:
            # Create default profile
            await memory_service.create_or_update_user_profile(
                request.user_id,
                {"risk_tolerance": "moderate"}
            )
        
        # Process query through agent
        result = await agent.process_query(request.user_id, request.message)
        
        return ChatResponse(
            response=result["response"],
            tools_used=result.get("tools_used", []),
            iterations=result.get("iterations", 0),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(user_id: str):
    """
    Get user profile
    """
    try:
        profile = await memory_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users/{user_id}/profile", response_model=UserProfileResponse)
async def update_user_profile(user_id: str, profile: UserProfile):
    """
    Create or update user profile
    """
    try:
        updated_profile = await memory_service.create_or_update_user_profile(
            user_id,
            profile.model_dump(exclude={"user_id"})
        )
        return updated_profile
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(user_id: str, limit: int = 20):
    """
    Get conversation history for a user
    """
    try:
        conversations = await memory_service.get_conversation_history(user_id, limit)
        return ConversationHistoryResponse(
            conversations=conversations,
            total=len(conversations)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/users/{user_id}/history")
async def clear_conversation_history(user_id: str):
    """
    Clear conversation history for a user
    """
    try:
        result = await memory_service.clear_conversation_history(user_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard")
async def get_dashboard_data():
    """
    Get aggregated dashboard data including economic indicators, news, and exchange rates
    """
    try:
        # Fetch economic indicators in parallel
        inflation = await fred_service.get_inflation_rate()
        unemployment = await fred_service.get_unemployment_rate()
        federal_funds = await fred_service.get_federal_funds_rate()
        gdp = await fred_service.get_gdp_growth()
        
        # Fetch news
        news = await news_service.get_economic_news(page_size=8)
        
        # Fetch exchange rates
        exchange_rates = await exchange_rate_service.get_exchange_rates("USD")
        
        return {
            "indicators": {
                "inflation": inflation,
                "unemployment": unemployment,
                "federal_funds_rate": federal_funds,
                "gdp": gdp
            },
            "news": news,
            "exchange_rates": exchange_rates,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/exchange-rates/historical/{currency}")
async def get_historical_exchange_rates(currency: str, days: int = 365):
    """
    Get historical exchange rates for a specific currency from FRED
    """
    try:
        historical_data = await fred_service.get_historical_exchange_rates(
            currency=currency.upper(),
            days=days
        )
        
        if not historical_data.get("success"):
            raise HTTPException(status_code=500, detail=historical_data.get("error", "Failed to fetch data"))
        
        return historical_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.BACKEND_PORT,
        reload=True
    )
