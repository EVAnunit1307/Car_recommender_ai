import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

import requests

BASE_URL = "https://api.fueleconomy.gov/ws/rest"
TIMEOUT = 8


def _fetch_xml(path: str, params: Dict) -> Optional[ET.Element]:
    try:
        resp = requests.get(f"{BASE_URL}/{path}", params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return ET.fromstring(resp.text)
    except (requests.RequestException, ET.ParseError):
        return None


def get_vehicle_options(year: int, make: str, model: str) -> List[Dict[str, str]]: #get car type
  
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


def get_vehicle_mpg(vehicle_id: str) -> Optional[Dict[str, Optional[float]]]: #get fuel economy 

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
        "mpge": as_float("combE"),
        "fuel_cost_annual": as_float("fuelCost08"),
        "drive": root.findtext("drive"),
        "transmission": root.findtext("trany"),
        "fuel_type": root.findtext("fuelType1"),
    }
