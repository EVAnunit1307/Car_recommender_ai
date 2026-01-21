from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import json
import re

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent
RAW_DIR = DATA_DIR / "kaggle_raw"
CACHE_DIR = DATA_DIR / "cache"
CACHE_FILE = CACHE_DIR / "kaggle_vehicles.json"
DATASET_SLUG = "abdulmalik1518/cars-datasets-2025"

YEAR_FALLBACK = 2025


def _normalize_text(value: Any) -> str:
    return str(value).strip()


def _title_case(value: Any) -> Optional[str]:
    text = _normalize_text(value)
    if not text or text.lower() == "nan":
        return None
    return text.title()


def _slugify(parts: Iterable[Optional[str]]) -> str:
    raw = "_".join([p for p in parts if p])
    raw = raw.lower()
    raw = re.sub(r"[^a-z0-9]+", "_", raw)
    return raw.strip("_")


def _parse_number_list(text: str) -> List[float]:
    matches = re.findall(r"\d[\d,]*(?:\.\d+)?", text)
    numbers = []
    for match in matches:
        cleaned = match.replace(",", "")
        try:
            numbers.append(float(cleaned))
        except ValueError:
            continue
    if "k" in text.lower():
        numbers = [n * 1000 if n < 1000 else n for n in numbers]
    return numbers


def parse_price(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = _normalize_text(value)
    if not text or text.lower() == "nan":
        return None
    numbers = _parse_number_list(text)
    if not numbers:
        return None
    if len(numbers) == 1:
        return numbers[0]
    return sum(numbers) / len(numbers)


def parse_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = _normalize_text(value)
    if not text or text.lower() == "nan":
        return None
    numbers = _parse_number_list(text)
    return numbers[0] if numbers else None


def parse_int(value: Any) -> Optional[int]:
    number = parse_float(value)
    if number is None:
        return None
    return int(round(number))


def normalize_fuel_type(value: Any) -> Optional[str]:
    text = _normalize_text(value).lower()
    if not text or text == "nan":
        return None
    if "electric" in text or "ev" in text:
        return "ev"
    if "hybrid" in text:
        return "hybrid"
    if "diesel" in text:
        return "diesel"
    if "petrol" in text or "gas" in text:
        return "gas"
    return None


def build_kaggle_catalog(csv_path: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    df = pd.read_csv(csv_path, encoding="utf-8", encoding_errors="replace")
    if limit:
        df = df.head(limit)

    cars: List[Dict[str, Any]] = []
    seen_ids = set()

    for _, row in df.iterrows():
        make = _title_case(row.get("Company Names"))
        model = _title_case(row.get("Cars Names"))
        if not make or not model:
            continue

        year = YEAR_FALLBACK
        price = parse_price(row.get("Cars Prices"))
        fuel_type = normalize_fuel_type(row.get("Fuel Types"))
        seats = parse_int(row.get("Seats"))
        zero_to_sixty = parse_float(row.get("Performance(0 - 100 )KM/H"))

        car_id = _slugify([make, model, str(year)])
        if car_id in seen_ids:
            car_id = f"{car_id}_{len(seen_ids)}"
        seen_ids.add(car_id)

        cars.append(
            {
                "id": car_id,
                "make": make,
                "model": model,
                "year": year,
                "price": price,
                "drivetrain": None,
                "seats": seats,
                "fuel_type": fuel_type,
                "mpg": None,
                "l_per_100km": None,
                "zero_to_sixty": zero_to_sixty,
                "annual_cost": None,
                "reliability_score": None,
                "safety_score": None,
                "horsepower": parse_float(row.get("HorsePower")),
                "engine": _normalize_text(row.get("Engines")),
                "engine_cc_or_battery": _normalize_text(row.get("CC/Battery Capacity")),
                "top_speed_kmh": parse_float(row.get("Total Speed")),
                "torque": _normalize_text(row.get("Torque")),
                "source": "kaggle",
                "source_dataset": DATASET_SLUG,
                "price_raw": _normalize_text(row.get("Cars Prices")),
            }
        )

    return cars


def write_catalog(cars: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(cars, f, indent=2)
