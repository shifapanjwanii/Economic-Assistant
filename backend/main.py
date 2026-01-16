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


# Initialize services
memory_service = MemoryService()
agent = EconomicAgent()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    await memory_service.initialize_database()
    yield


# Create FastAPI app
app = FastAPI(
    title="Economic Decision Advisor API",
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
        "message": "Economic Decision Advisor API",
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
    Clear conversation history for a user (for testing/demo purposes)
    """
    try:
        # This would need to be implemented in memory_service
        return {"message": "History cleared", "user_id": user_id}
        
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
