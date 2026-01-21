from pydantic import BaseModel, Field
from typing import List, Dict, Optional

"""Input validation for recommendation requests."""

class CarRecommendationRequest(BaseModel):
    budget: int = Field(gt=0, description="Max purchase budget")
    location: str = Field(min_length=2, description="User location")
    annual_km: int = Field(gt=0, description="Expected annual distance (km)")
    passengers: int = Field(ge=1, description="Number of passengers")
    fuel_type: Optional[str] = Field(
        default=None,
        description="Optional fuel type filter (e.g., ICE, Hybrid, EV)"
    )
    priorities: List[str] = Field(description="User priorities for recommendation")
    weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional weights for metrics (0.0 to 1.0)"
    )


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="User message")
    session_id: Optional[str] = Field(default=None, description="Optional session ID")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatResponse(BaseModel):
    session_id: str
    message: str
    history: List[ChatMessage]
