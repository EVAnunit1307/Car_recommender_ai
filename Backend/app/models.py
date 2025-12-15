from pydantic import BaseModel, Field
from typing import List, Dict, Optional

"""input validation file"""

class CarRecommendationRequest(BaseModel):
    budget: int = Field(gt = 0, description="The max purchasing budget") #gt= greater than 
    location: str = Field(min_length= 2, description= "The location of the user")
    annual_km : int = Field(gt = 0, desciption= "The anual km the person expects to drive")
    passengers: int = Field(ge=1, description="Number of passengers") #greater/equal to 
    priorities: List[str] = Field(description="User priorities for recommendation")
    weights: Optional[Dict[str, float]] =Field(
        defualt = None,
        description="Optinal weights for priorities (0.0 to 1.0)"
     )


