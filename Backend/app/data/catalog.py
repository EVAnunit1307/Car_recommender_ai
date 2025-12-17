from pathlib import Path
import json
from typing import List, Dict, Any

# Fallback sample data so the app works even without a cached catalog
MOCK_CARS: List[Dict[str, Any]] = [
    {
        "id": "civic_2018",
        "make": "Honda",
        "model": "Civic",
        "year": 2018,
        "price": 19000,
        "drivetrain": "FWD",
        "mpg": 32,
        "seats": 5,
        "zero_to_sixty": 8.2,
        "annual_cost": 2300,
        "reliability_score": 0.8,
    },
    {
        "id": "wrx_2018",
        "make": "Subaru",
        "model": "WRX",
        "year": 2018,
        "price": 24000,
        "drivetrain": "AWD",
        "mpg": 24,
        "seats": 5,
        "zero_to_sixty": 5.5,
        "annual_cost": 3200,
        "reliability_score": 0.6,
    },
    {
        "id": "leaf_2019",
        "make": "Nissan",
        "model": "Leaf",
        "year": 2019,
        "price": 17000,
        "drivetrain": "FWD",
        "mpg": 0,
        "seats": 5,
        "zero_to_sixty": 7.9,
        "annual_cost": 1800,
        "reliability_score": 0.7,
    },
]

DATA_DIR = Path(__file__).resolve().parent
CACHE_FILE = DATA_DIR / "cache" / "vehicles.json"


def load_cars() -> List[Dict[str, Any]]:
    """
    Load cars from the cached catalog file if present; otherwise fall back to MOCK_CARS.
    """
    if CACHE_FILE.exists():
        try:
            with CACHE_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data
        except (OSError, json.JSONDecodeError):
            pass
    return MOCK_CARS
