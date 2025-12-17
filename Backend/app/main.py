from fastapi import FastAPI
from app.models import CarRecommendationRequest
from app.services.nhtsa_issues import get_complaints_and_recalls
from app.recommender import winter_score, fuel_score
from app.data.catalog import MOCK_CARS
app = FastAPI()


@app.post("/recommend")
def recommend_car(request: CarRecommendationRequest) -> dict:
    w_winter = request.weights.get("winter_driving", 0.4) if request.weights else 0.4
    w_fuel = request.weights.get("fuel_efficiency", 0.4) if request.weights else 0.4

    results = []
    for car in MOCK_CARS:
        winter_points = winter_score(car["drivetrain"], w_winter) #computes points for winter by lookign up car and computing with weight 
        fuel_points = fuel_score(car["mpg"], w_fuel)

        results.append({
            "id": car["id"],
            "make": car["make"],
            "model": car["model"],
            "year": car["year"],
            "drivetrain": car["drivetrain"],
            "winter_points": round(winter_points, 4),
            "fuel_points": round(fuel_points, 4),
        })
    return {"weights_used": {"winter_driving": w_winter}, "results": results}

@app.get("/nhtsa/issues")
def nhtsa_issues(make: str, model: str, model_year: int) -> dict:
    return get_complaints_and_recalls(model_year, make, model)
