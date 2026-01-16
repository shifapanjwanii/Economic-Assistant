from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class UserProfile(BaseModel):
    user_id: str
    income_range: Optional[str] = None
    debt_level: Optional[float] = 0.0
    dependents: Optional[int] = 0
    risk_tolerance: Optional[str] = "moderate"
    financial_goals: Optional[Dict[str, Any]] = {}
    preferences: Optional[Dict[str, Any]] = {}


class ChatRequest(BaseModel):
    user_id: str = Field(default="default_user")
    message: str
    

class ChatResponse(BaseModel):
    response: str
    tools_used: List[str] = []
    iterations: int = 0
    timestamp: str


class UserProfileResponse(BaseModel):
    user_id: str
    income_range: Optional[str]
    debt_level: Optional[float]
    dependents: Optional[int]
    risk_tolerance: Optional[str]
    financial_goals: Optional[Dict[str, Any]]
    preferences: Optional[Dict[str, Any]]
    created_at: Optional[str]
    updated_at: Optional[str]


class ConversationHistoryResponse(BaseModel):
    conversations: List[Dict[str, Any]]
    total: int
