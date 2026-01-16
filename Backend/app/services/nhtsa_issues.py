import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

BASE = "https://api.nhtsa.gov"

# Cache directory for NHTSA data
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"
NHTSA_CACHE_FILE = CACHE_DIR / "nhtsa_cache.json"
CACHE_DURATION_DAYS = 30  # Cache NHTSA data for 30 days


def _load_cache() -> Dict[str, Any]:
    """Load NHTSA cache from disk."""
    if NHTSA_CACHE_FILE.exists():
        try:
            with NHTSA_CACHE_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def _save_cache(cache: Dict[str, Any]) -> None:
    """Save NHTSA cache to disk."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with NHTSA_CACHE_FILE.open("w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except OSError:
        pass  # Fail silently if we can't write cache


def _get_count(url: str, params: dict) -> int:
    """Fetch count of results from NHTSA endpoint."""
    r = requests.get(url, params=params, timeout=6)
    r.raise_for_status()
    data = r.json()

    # Most NHTSA endpoints include "results" as a list
    results = data.get("results", [])
    return len(results)


def calculate_reliability_from_nhtsa(
    complaints_count: int, 
    recalls_count: int,
    vehicle_age_years: int = 0
) -> float:
    """
    Calculate reliability score (0.0 to 1.0) based on NHTSA data.
    
    Lower complaints and recalls = higher reliability.
    Adjusts for vehicle age (older vehicles may have more accumulated issues).
    
    Args:
        complaints_count: Number of NHTSA complaints
        recalls_count: Number of NHTSA recalls
        vehicle_age_years: Years since manufacture (for normalization)
    
    Returns:
        Reliability score between 0.0 and 1.0
    """
    # Normalize by age to be fair to older vehicles
    age_factor = max(1, vehicle_age_years)
    
    # Per-year complaint rate (assuming linear accumulation)
    complaints_per_year = complaints_count / age_factor
    recalls_per_year = recalls_count / age_factor
    
    # Penalties (tuned based on typical ranges)
    # Average car: ~20-50 complaints/year, 0-2 recalls/year
    complaint_penalty = min(0.5, complaints_per_year * 0.01)  # Max 0.5 penalty
    recall_penalty = min(0.3, recalls_per_year * 0.15)  # Max 0.3 penalty
    
    # Start at 0.8 (good baseline), reduce by penalties
    reliability = 0.8 - complaint_penalty - recall_penalty
    
    # Clamp between 0.3 (minimum) and 1.0 (maximum)
    return max(0.3, min(1.0, reliability))


def calculate_safety_score(recalls_count: int, vehicle_age_years: int = 0) -> float:
    """
    Calculate safety score (0.0 to 1.0) based on recalls.
    
    Fewer recalls = safer vehicle.
    
    Args:
        recalls_count: Number of NHTSA recalls
        vehicle_age_years: Years since manufacture
    
    Returns:
        Safety score between 0.0 and 1.0
    """
    age_factor = max(1, vehicle_age_years)
    recalls_per_year = recalls_count / age_factor
    
    # 0 recalls = 1.0, each recall per year reduces score
    penalty = min(0.6, recalls_per_year * 0.20)
    safety = 1.0 - penalty
    
    return max(0.4, min(1.0, safety))


def get_complaints_and_recalls(
    model_year: int, 
    make: str, 
    model: str,
    use_cache: bool = True
) -> dict:
    """
    Fetch complaint and recall counts from NHTSA API with caching.
    
    Args:
        model_year: Vehicle model year
        make: Vehicle make (e.g., "Toyota")
        model: Vehicle model (e.g., "Camry")
        use_cache: Whether to use cached data
    
    Returns:
        Dictionary with complaints, recalls, and calculated scores
    """
    cache_key = f"{model_year}_{make}_{model}".lower().replace(" ", "_")
    
    # Check cache first
    if use_cache:
        cache = _load_cache()
        if cache_key in cache:
            cached_data = cache[cache_key]
            cached_time = datetime.fromisoformat(cached_data.get("cached_at", "2000-01-01"))
            if datetime.now() - cached_time < timedelta(days=CACHE_DURATION_DAYS):
                return cached_data["data"]
    
    params = {"make": make, "model": model, "modelYear": model_year}
    
    try:
        complaints = _get_count(f"{BASE}/complaints/complaintsByVehicle", params)
        recalls = _get_count(f"{BASE}/recalls/recallsByVehicle", params)
    except requests.RequestException as e:
        return {
            "error": "NHTSA service unavailable",
            "model_year": model_year,
            "make": make,
            "model": model,
        }
    
    # Calculate age
    current_year = datetime.now().year
    vehicle_age = max(1, current_year - model_year)
    
    # Calculate scores
    reliability = calculate_reliability_from_nhtsa(complaints, recalls, vehicle_age)
    safety = calculate_safety_score(recalls, vehicle_age)
    
    result = {
        "model_year": model_year,
        "make": make,
        "model": model,
        "complaints_count": complaints,
        "recalls_count": recalls,
        "vehicle_age_years": vehicle_age,
        "reliability_score": round(reliability, 3),
        "safety_score": round(safety, 3),
    }
    
    # Save to cache
    if use_cache:
        cache = _load_cache()
        cache[cache_key] = {
            "data": result,
            "cached_at": datetime.now().isoformat(),
        }
        _save_cache(cache)
    
    return result