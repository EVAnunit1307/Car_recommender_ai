from pydantic import BaseModel, Field

class AgeGuessRequest(BaseModel):
        name: str = Field(min_length=1, description="First name to querey") #rejects empty strings