from __future__ import annotations

import json
from typing import Any, Dict, List

from langchain.tools import Tool

from app.data.catalog import load_cars_with_meta
from app.models import CarRecommendationRequest
from app.recommendations import build_recommendations
from app.services.nhtsa_issues import get_complaints_and_recalls


DEFAULT_REQUEST: Dict[str, Any] = {
    "budget": 30000,
    "location": "US",
    "annual_km": 12000,
    "passengers": 4,
    "priorities": ["fuel", "winter", "price"],
}


def _parse_json_payload(input_str: str) -> Dict[str, Any]:
    try:
        payload = json.loads(input_str) if input_str else {}
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        return {}
    return {}


def _coerce_request(payload: Dict[str, Any]) -> CarRecommendationRequest:
    data = {**DEFAULT_REQUEST, **payload}
    return CarRecommendationRequest(**data)


def search_cars_by_criteria(input_str: str) -> str:
    payload = _parse_json_payload(input_str)
    request = _coerce_request(payload)
    limit = payload.get("limit", 5)
    results = build_recommendations(request, limit=limit)
    return json.dumps(results, ensure_ascii=True)


def get_car_details(input_str: str) -> str:
    car_id = (input_str or "").strip()
    catalog, _, _ = load_cars_with_meta()
    for car in catalog:
        if car.get("id") == car_id:
            return json.dumps(car, ensure_ascii=True)
    return json.dumps({"error": "car_not_found", "car_id": car_id}, ensure_ascii=True)


def compare_cars(input_str: str) -> str:
    payload = _parse_json_payload(input_str)
    ids = payload.get("ids", []) if isinstance(payload, dict) else []
    if not isinstance(ids, list):
        return json.dumps({"error": "ids_must_be_list"}, ensure_ascii=True)
    catalog, _, _ = load_cars_with_meta()
    matches = [car for car in catalog if car.get("id") in ids]
    return json.dumps({"matches": matches}, ensure_ascii=True)


def get_safety_info(input_str: str) -> str:
    payload = _parse_json_payload(input_str)
    make = payload.get("make")
    model = payload.get("model")
    year = payload.get("year")
    if not make or not model or not year:
        return json.dumps({"error": "make_model_year_required"}, ensure_ascii=True)
    try:
        year_int = int(year)
    except (TypeError, ValueError):
        return json.dumps({"error": "invalid_year"}, ensure_ascii=True)
    data = get_complaints_and_recalls(year_int, make, model)
    return json.dumps(data, ensure_ascii=True)


def build_tools() -> List[Tool]:
    return [
        Tool(
            name="search_cars_by_criteria",
            func=search_cars_by_criteria,
            description="Search for cars by budget, passengers, fuel_type, and weights.",
        ),
        Tool(
            name="get_car_details",
            func=get_car_details,
            description="Fetch full details for a car by its id.",
        ),
        Tool(
            name="compare_cars",
            func=compare_cars,
            description="Compare multiple cars by ids (JSON: {\"ids\": [\"id1\", \"id2\"]}).",
        ),
        Tool(
            name="get_safety_info",
            func=get_safety_info,
            description="Get NHTSA complaints and recalls (JSON: {\"make\": \"Toyota\", \"model\": \"Camry\", \"year\": 2019}).",
        ),
    ]
