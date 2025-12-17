"""
Build a cached vehicle catalog using public APIs (CarQuery, EPA, NHTSA) plus a small
seed CSV for price/0-60/fuel_type fallbacks. Keeps scope small to avoid hammering
free APIs; expand MAKES/YEARS as needed.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import csv
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.services.carquery import get_trims
from app.services.epa import get_vehicle_options, get_vehicle_mpg
from app.services.nhtsa_issues import get_complaints_and_recalls

CACHE_FILE = ROOT / "app" / "data" / "cache" / "vehicles.json"
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

SEED_FILE = ROOT / "app" / "data" / "seed_specs.csv"

# Expand this list as you like. Keep it small to respect free API limits.
MAKES = ["Honda", "Subaru", "Toyota", "Nissan", "Ford"]
YEARS = [2018, 2019, 2020, 2021, 2022]


def mpg_to_l_per_100km(mpg: Optional[float]) -> Optional[float]:
    if mpg is None or mpg <= 0:
        return None
    return 235.214583 / mpg


def parse_price(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def reliability_score_from_counts(complaints: int, recalls: int) -> float:
    total = max(complaints, 0) + max(recalls, 0)
    if total <= 1:
        return 1.0
    if total >= 50:
        return 0.0
    return max(0.0, 1.0 - (total / 50.0))


def load_seed_specs() -> Dict[Tuple[str, str, int], Dict[str, Any]]:
    if not SEED_FILE.exists():
        return {}
    data: Dict[Tuple[str, str, int], Dict[str, Any]] = {}
    with SEED_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                make = row.get("make") or ""
                model = row.get("model") or ""
                year = int(row.get("year", 0))
                key = (make, model, year)
                data[key] = {
                    "price": parse_price(row.get("price")),
                    "zero_to_sixty": float(row["zero_to_sixty"]) if row.get("zero_to_sixty") else None,
                    "fuel_type": row.get("fuel_type"),
                    "l_per_100km": float(row["l_per_100km"]) if row.get("l_per_100km") else None,
                }
            except ValueError:
                continue
    return data


def pick_fuel_type(epa_fuel: Optional[str], trim: Dict[str, Any], seed: Dict[str, Any]) -> Optional[str]:
    if epa_fuel:
        return epa_fuel
    if seed.get("fuel_type"):
        return seed["fuel_type"]
    engine_fuel = (trim.get("model_engine_fuel") or "").upper()
    if engine_fuel:
        return engine_fuel
    return None


def pick_zero_to_sixty(seed: Dict[str, Any]) -> Optional[float]:
    return seed.get("zero_to_sixty")


def parse_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build_catalog() -> List[Dict[str, Any]]:
    catalog: List[Dict[str, Any]] = []
    seed_specs = load_seed_specs()

    for make in MAKES:
        for year in YEARS:
            trims = get_trims(make, year)
            if not trims:
                continue

            for trim in trims[:8]:
                model = trim.get("model_name")
                if not model:
                    continue

                seed = seed_specs.get((make, model, year), {})

                epa_options = get_vehicle_options(year, make, model)
                epa_id = epa_options[0]["id"] if epa_options else None
                epa_details = get_vehicle_mpg(epa_id) if epa_id else None

                complaints_data = get_complaints_and_recalls(year, make, model)
                reliability = reliability_score_from_counts(
                    complaints_data.get("complaints_count", 0),
                    complaints_data.get("recalls_count", 0),
                ) if isinstance(complaints_data, dict) else 0.5

                mpg = (epa_details or {}).get("mpg_combined")
                lpk = seed.get("l_per_100km") or mpg_to_l_per_100km(mpg)

                record = {
                    "id": f"{make.lower()}_{model.lower()}_{year}_{len(catalog)}",
                    "make": make,
                    "model": model,
                    "year": year,
                    "price": parse_price(trim.get("model_price")) or seed.get("price") or 0,
                    "drivetrain": (epa_details or {}).get("drive")
                    or trim.get("model_drive")
                    or trim.get("model_drivetrain")
                    or "",
                    "fuel_type": pick_fuel_type((epa_details or {}).get("fuel_type"), trim, seed),
                    "mpg": mpg or 0,
                    "mpge": (epa_details or {}).get("mpge"),
                    "l_per_100km": lpk,
                    "zero_to_sixty": pick_zero_to_sixty(seed),
                    "annual_cost": (epa_details or {}).get("fuel_cost_annual"),
                    "reliability_score": reliability,
                    "seats": trim.get("model_seats"),
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
