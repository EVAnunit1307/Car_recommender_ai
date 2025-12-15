import requests

BASE = "https://api.nhtsa.gov"

def _get_count(url: str, params: dict) -> int:
    r = requests.get(url, params=params, timeout=6)
    r.raise_for_status()
    data = r.json()

    # Most NHTSA endpoints include "results" as a list
    results = data.get("results", [])
    return len(results)

def get_complaints_and_recalls(model_year: int, make: str, model: str) -> dict:
    params = {"make": make, "model": model, "modelYear": model_year}

    try:
        complaints = _get_count(f"{BASE}/complaints/complaintsByVehicle", params)
        recalls = _get_count(f"{BASE}/recalls/recallsByVehicle", params)
    except requests.RequestException:
        return {"error": "NHTSA service unavailable"}

    return {
        "model_year": model_year,
        "make": make,
        "model": model,
        "complaints_count": complaints,
        "recalls_count": recalls,
    }
