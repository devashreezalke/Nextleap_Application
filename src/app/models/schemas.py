from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal

class Restaurant(BaseModel):
    id: str
    name: str
    location: str
    cuisines: List[str]
    rating: float
    estimated_cost: float
    budget_band: Literal["low", "medium", "high"]
    votes: int
    address: str

class UserPreferences(BaseModel):
    location: str = Field(..., min_length=1, description="Location/City where the user is looking for dining.")
    budget: Literal["low", "medium", "high"] = Field(..., description="Desired cost level.")
    cuisine: Optional[str] = Field(default=None, description="Preferred cuisine category.")
    min_rating: float = Field(default=3.5, ge=0.0, le=5.0, description="Minimum acceptable rating.")
    additional_preferences: Optional[str] = Field(default=None, max_length=300, description="Optional free-text preference details.")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of suggestions to generate.")

    @field_validator("location")
    @classmethod
    def clean_location(cls, val: str) -> str:
        return val.strip()

    @field_validator("cuisine")
    @classmethod
    def clean_cuisine(cls, val: Optional[str]) -> Optional[str]:
        if val is None or not val.strip():
            return None
        return val.strip()

class Recommendation(BaseModel):
    rank: int
    restaurant: Restaurant
    explanation: str

class RecommendationResponse(BaseModel):
    summary: Optional[str] = None
    recommendations: List[Recommendation]
    meta: dict = Field(default_factory=dict)
