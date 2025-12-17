from pathlib import Path
import json
from typing import List, Dict, Any, Tuple

# Fallback sample data so the app works even without a cached catalog
MOCK_CARS: List[Dict[str, Any]] = [
    {
        "id": "civic_2018",
        "make": "Honda",
        "model": "Civic",
        "year": 2018,
        "price": 19000,
        "drivetrain": "FWD",
        "fuel_type": "ICE",
        "mpg": 32,
        "l_per_100km": 7.35,
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
        "fuel_type": "ICE",
        "mpg": 24,
        "l_per_100km": 9.8,
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
        "fuel_type": "EV",
        "mpg": 0,
        "l_per_100km": None,
        "seats": 5,
        "zero_to_sixty": 7.9,
        "annual_cost": 1800,
        "reliability_score": 0.7,
    },
]

DATA_DIR = Path(__file__).resolve().parent
CACHE_FILE = DATA_DIR / "cache" / "vehicles.json"


def _read_cache() -> Tuple[List[Dict[str, Any]], bool]:
    if CACHE_FILE.exists():
        try:
            with CACHE_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data, False
        except (OSError, json.JSONDecodeError):
            pass
    return MOCK_CARS, True


def load_cars() -> List[Dict[str, Any]]:
    """
    Load cars from the cached catalog file if present; otherwise fall back to MOCK_CARS.
    """
    data, _ = _read_cache()
    return data


def load_cars_with_meta() -> Tuple[List[Dict[str, Any]], bool]:
    """
    Return cars and a flag indicating if mock data was used.
    """
    return _read_cache()
