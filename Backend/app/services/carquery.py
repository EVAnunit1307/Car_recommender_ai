import json
from typing import List, Dict, Any

import requests

BASE_URL = "https://www.carqueryapi.com/api/0.3/"
TIMEOUT = 10


def _parse_json_maybe_jsonp(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Handle JSONP or prefixed responses by slicing the first '{' or '['
    start = len(text)
    for ch in ("{", "["):
        idx = text.find(ch)
        if idx != -1:
            start = min(start, idx)

    end = max(text.rfind("}"), text.rfind("]"))
    if start < end:
        snippet = text[start : end + 1]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError:
            return None
    return None


def get_trims(make: str, year: int, sold_in_us: int = 1) -> List[Dict[str, Any]]:
    """
    Fetch trims for a make/year from CarQuery.
    Returns a list of dictionaries with fields like model_name, model_trim, etc.
    """
    try:
        resp = requests.get(
            BASE_URL,
            params={"cmd": "getTrims", "make": make, "year": year, "sold_in_us": sold_in_us},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException:
        return []

    data = _parse_json_maybe_jsonp(resp.text)
    if not data:
        return []

    trims = data.get("Trims") if isinstance(data, dict) else None
    return trims if isinstance(trims, list) else []
