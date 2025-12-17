import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

import requests

fuel_economy_link = "https://api.fueleconomy.gov/ws/rest"


def _fetch_xml(path: str, params: Dict) -> Optional[ET.Element]:
    try:
        resp = requests.get(f"{fuel_economy_link}/{path}", params=params, timeout=5)
        resp.raise_for_status()
        return ET.fromstring(resp.text)
    except (requests.RequestException, ET.ParseError):
        return None


def get_vehicle_options(year: int, make: str, model: str) -> List[Dict[str, str]]:
    """
    Look up EPA vehicle option IDs for a given make/model/year.
    Returns a list of {"id": "...", "text": "..."} dictionaries.
    """
    root = _fetch_xml("vehicle/menu/options", {"year": year, "make": make, "model": model})
    if root is None:
        return []

    options: List[Dict[str, str]] = []
    for item in root.findall(".//menuItem"):
        val = item.findtext("value")
        txt = item.findtext("text") or ""
        if val:
            options.append({"id": val, "text": txt})
    return options


def get_vehicle_mpg(vehicle_id: str) -> Optional[Dict[str, Optional[float]]]:
    """
    Fetch fuel economy and fuel cost info for a specific EPA vehicle ID.
    Returns None on failure.
    """
    root = _fetch_xml(f"vehicle/{vehicle_id}", {})
    if root is None:
        return None

    def as_float(tag: str) -> Optional[float]:
        value = root.findtext(tag)
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    return {
        "mpg_city": as_float("city08"),
        "mpg_highway": as_float("highway08"),
        "mpg_combined": as_float("comb08"),
        "fuel_cost_annual": as_float("fuelCost08"),
        "drive": root.findtext("drive"),
        "transmission": root.findtext("trany"),
    }
