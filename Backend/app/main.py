from fastapi import FastAPI
from app.models import CarRecommendationRequest
from app.services.nhtsa_issues import get_complaints_and_recalls
from app.recommender import winter_score
from app.data.catalog import MOCK_CARS
app = FastAPI()


@app.post("/recommend")
def recommend_car(request: CarRecommendationRequest) -> dict:
    w_winter = 0.4
    if request.weights and "winter_driving" in request.weights:
        w_winter = float(request.weights["winter_driving"])

    results = []
    for car in MOCK_CARS:
        winter_points = winter_score(car["drivetrain"], w_winter)

        results.append({
            "id": car["id"],
            "make": car["make"],
            "model": car["model"],
            "year": car["year"],
            "drivetrain": car["drivetrain"],
            "winter_points": round(winter_points, 4),
        })

    return {"weights_used": {"winter_driving": w_winter}, "results": results}

@app.get("/nhtsa/issues")
def nhtsa_issues(make: str, model: str, model_year: int) -> dict:
    return get_complaints_and_recalls(model_year, make, model)
    