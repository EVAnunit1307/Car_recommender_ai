from typing import Any, Dict, List

from app.data.catalog import load_cars_with_meta
from app.models import CarRecommendationRequest
from app.recommender import (
    acceleration_score,
    fuel_score,
    normalize_weights,
    ownership_cost_score,
    price_fit_score,
    reliability_score,
    safety_score,
    winter_score,
)


DEFAULT_WEIGHTS = {
    "winter_driving": 0.15,
    "fuel_efficiency": 0.15,
    "price_fit": 0.20,
    "ownership_cost": 0.15,
    "acceleration": 0.10,
    "reliability": 0.15,
    "safety": 0.10,
}


def build_recommendations(request: CarRecommendationRequest, limit: int = 5) -> Dict[str, Any]:
    raw_weights = request.weights or DEFAULT_WEIGHTS
    weights = normalize_weights(raw_weights)

    catalog, using_mock, last_updated = load_cars_with_meta()
    budget_cutoff = request.budget * 1.2
    results: List[Dict[str, Any]] = []

    for car in catalog:
        if car.get("price") and car["price"] > budget_cutoff:
            continue
        if car.get("seats") and car["seats"] < request.passengers:
            continue
        if request.fuel_type:
            ftype = (request.fuel_type or "").lower()
            ctype = (car.get("fuel_type") or "").lower()
            if ctype and ctype != ftype:
                continue

        w_winter = weights.get("winter_driving", 0.0)
        w_fuel = weights.get("fuel_efficiency", 0.0)
        w_price = weights.get("price_fit", 0.0)
        w_accel = weights.get("acceleration", 0.0)
        w_own = weights.get("ownership_cost", 0.0)
        w_rely = weights.get("reliability", 0.0)
        w_safety = weights.get("safety", 0.0)

        winter_points = winter_score(car.get("drivetrain", ""), w_winter)
        fuel_points = fuel_score(
            car.get("l_per_100km"),
            car.get("mpg"),
            car.get("fuel_type"),
            w_fuel,
        )
        price_points = price_fit_score(car.get("price", 0.0), request.budget, w_price)
        accel_points = acceleration_score(car.get("zero_to_sixty", 0.0), w_accel)
        own_points = ownership_cost_score(car.get("annual_cost", 0.0), w_own)
        rely_points = reliability_score(car.get("reliability_score", 0.0), w_rely)
        safety_points = safety_score(car.get("safety_score", 0.0), w_safety)

        total_score = (
            winter_points
            + fuel_points
            + price_points
            + accel_points
            + own_points
            + rely_points
            + safety_points
        )

        results.append(
            {
                "id": car.get("id"),
                "make": car.get("make"),
                "model": car.get("model"),
                "year": car.get("year"),
                "drivetrain": car.get("drivetrain"),
                "price": car.get("price"),
                "mpg": car.get("mpg"),
                "l_per_100km": car.get("l_per_100km"),
                "fuel_type": car.get("fuel_type"),
                "zero_to_sixty": car.get("zero_to_sixty"),
                "annual_cost": car.get("annual_cost"),
                "reliability_score": car.get("reliability_score"),
                "safety_score": car.get("safety_score"),
                "complaints_count": car.get("complaints_count"),
                "recalls_count": car.get("recalls_count"),
                "winter_points": round(winter_points, 4),
                "fuel_points": round(fuel_points, 4),
                "price_points": round(price_points, 4),
                "acceleration_points": round(accel_points, 4),
                "ownership_cost_points": round(own_points, 4),
                "reliability_points": round(rely_points, 4),
                "safety_points": round(safety_points, 4),
                "total_score": round(total_score, 4),
            }
        )

    results.sort(key=lambda x: x["total_score"], reverse=True)
    return {
        "weights_used": weights,
        "using_mock_data": using_mock,
        "catalog_last_updated": last_updated,
        "results": results[:limit],
    }
