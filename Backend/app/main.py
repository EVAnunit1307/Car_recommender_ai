from fastapi import FastAPI
from app.models import CarRecommendationRequest
from app.services.nhtsa_issues import get_complaints_and_recalls
app = FastAPI()


@app.post("/recommend")
def recommend_car(request: CarRecommendationRequest) -> dict:
    return {
        "message": "Recommendation logic not implemented yet",
        "input_received": request.dict()
    }

@app.get("/nhtsa/issues")
def nhtsa_issues(make: str, model: str, model_year: int) -> dict:
    return get_complaints_and_recalls(model_year, make, model)
