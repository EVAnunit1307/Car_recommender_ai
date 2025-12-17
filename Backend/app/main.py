from fastapi import FastAPI
from app.models import CarRecommendationRequest
from app.services.nhtsa_issues import get_complaints_and_recalls
from app.recommender import (
    normalize_weights,
    winter_score,
    fuel_score,
    price_fit_score,
    acceleration_score,
    ownership_cost_score,
    reliability_score,
)
from app.data.catalog import load_cars

app = FastAPI()
CATALOG = load_cars()


@app.post("/recommend")
def recommend_car(request: CarRecommendationRequest) -> dict:
    default_weights = {
        "winter_driving": 0.2,
        "fuel_efficiency": 0.2,
        "price_fit": 0.2,
        "ownership_cost": 0.2,
        "acceleration": 0.1,
        "reliability": 0.1,
    }

    raw_weights = request.weights or default_weights
    weights = normalize_weights(raw_weights)

    results = []
    for car in CATALOG:
        w_winter = weights.get("winter_driving", 0.0)
        w_fuel = weights.get("fuel_efficiency", 0.0)
        w_price = weights.get("price_fit", 0.0)
        w_accel = weights.get("acceleration", 0.0)
        w_own = weights.get("ownership_cost", 0.0)
        w_rely = weights.get("reliability", 0.0)

        winter_points = winter_score(car.get("drivetrain", ""), w_winter)
        fuel_points = fuel_score(car.get("mpg", 0.0), w_fuel)
        price_points = price_fit_score(car.get("price", 0.0), request.budget, w_price)
        accel_points = acceleration_score(car.get("zero_to_sixty", 0.0), w_accel)
        own_points = ownership_cost_score(car.get("annual_cost", 0.0), w_own)
        rely_points = reliability_score(car.get("reliability_score", 0.0), w_rely)

        total_score = (
            winter_points
            + fuel_points
            + price_points
            + accel_points
            + own_points
            + rely_points
        )

        results.append(
            {
                "id": car["id"],
                "make": car["make"],
                "model": car["model"],
                "year": car["year"],
                "drivetrain": car["drivetrain"],
                "price": car["price"],
                "mpg": car.get("mpg"),
                "zero_to_sixty": car.get("zero_to_sixty"),
                "annual_cost": car.get("annual_cost"),
                "reliability_score": car.get("reliability_score"),
                "winter_points": round(winter_points, 4),
                "fuel_points": round(fuel_points, 4),
                "price_points": round(price_points, 4),
                "acceleration_points": round(accel_points, 4),
                "ownership_cost_points": round(own_points, 4),
                "reliability_points": round(rely_points, 4),
                "total_score": round(total_score, 4),
            }
        )

    results.sort(key=lambda x: x["total_score"], reverse=True)
    return {
        "weights_used": weights,
        "results": results[:5],
    }


@app.get("/nhtsa/issues")
def nhtsa_issues(make: str, model: str, model_year: int) -> dict:
    return get_complaints_and_recalls(model_year, make, model)
