"""
Pull a small catalog of cars from public APIs and cache to app/data/cache/vehicles.json.
This is designed to be simple and safe to run; adjust the make/year lists as needed.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json

from app.services.carquery import get_trims
from app.services.epa import get_vehicle_options, get_vehicle_mpg
from app.services.nhtsa_issues import get_complaints_and_recalls

ROOT = Path(__file__).resolve().parents[1]
CACHE_FILE = ROOT / "app" / "data" / "cache" / "vehicles.json"
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

# Keep scope small to avoid hammering the free APIs. Expand as needed.
MAKES = ["Honda", "Subaru", "Nissan"]
YEARS = [2018, 2019, 2020]

# Temporary lookup for 0-60 times (seconds). Extend or replace with a real source.
ZERO_TO_SIXTY = {
    ("Honda", "Civic"): 8.2,
    ("Subaru", "WRX"): 5.5,
    ("Nissan", "Leaf"): 7.9,
}


def parse_price(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def reliability_score_from_counts(complaints: int, recalls: int) -> float:
    # Simple inverse: more issues -> lower score. Clamp between 0 and 1.
    total = max(complaints, 0) + max(recalls, 0)
    if total <= 1:
        return 1.0
    if total >= 50:
        return 0.0
    return max(0.0, 1.0 - (total / 50.0))


def pick_zero_to_sixty(make: str, model: str) -> Optional[float]:
    return ZERO_TO_SIXTY.get((make, model))


def build_catalog() -> List[Dict[str, Any]]:
    catalog: List[Dict[str, Any]] = []

    for make in MAKES:
        for year in YEARS:
            trims = get_trims(make, year)
            if not trims:
                continue

            # Keep it small per make/year to respect rate limits
            for trim in trims[:5]:
                model = trim.get("model_name")
                if not model:
                    continue

                epa_options = get_vehicle_options(year, make, model)
                epa_id = epa_options[0]["id"] if epa_options else None
                epa_details = get_vehicle_mpg(epa_id) if epa_id else None

                complaints_data = get_complaints_and_recalls(year, make, model)
                reliability = reliability_score_from_counts(
                    complaints_data.get("complaints_count", 0),
                    complaints_data.get("recalls_count", 0),
                ) if isinstance(complaints_data, dict) else 0.5

                record = {
                    "id": f"{make.lower()}_{model.lower()}_{year}_{len(catalog)}",
                    "make": make,
                    "model": model,
                    "year": year,
                    "price": parse_price(trim.get("model_price")) or 0,
                    "drivetrain": (epa_details or {}).get("drive")
                    or trim.get("model_drive")
                    or trim.get("model_drivetrain")
                    or "",
                    "mpg": (epa_details or {}).get("mpg_combined") or 0,
                    "zero_to_sixty": pick_zero_to_sixty(make, model),
                    "annual_cost": (epa_details or {}).get("fuel_cost_annual"),
                    "reliability_score": reliability,
                    "source": {
                        "carquery_trim_id": trim.get("model_id"),
                        "epa_vehicle_id": epa_id,
                    },
                }
                catalog.append(record)

    return catalog


def main() -> None:
    catalog = build_catalog()
    CACHE_FILE.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"Wrote {len(catalog)} vehicles to {CACHE_FILE}")


if __name__ == "__main__":
    main()
