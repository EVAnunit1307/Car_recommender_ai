from pydantic import BaseModel, Field
from typing import List

class CarRecommendationRequest(BaseModel):
    budget: int = Field(gt = 0, description="The max purchasing budget")
    location: str = Field(min_length= 2, description= "The location of the user")
    annual_km : str = Field(gt = 0, desciption= "The anual km the person expects to drive")
    passengers: int = Field(ge=1, description="Number of passengers")
    priorities: List[str] = Field(description="User priorities for recommendation")

