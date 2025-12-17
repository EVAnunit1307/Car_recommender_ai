from pathlib import Path
import json
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

# Fallback sample data so the app works even without a cached catalog
MOCK_CARS: List[Dict[str, Any]] = [
  {"id":"honda_civic_2018","make":"Honda","model":"Civic","year":2018,"price":19000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.4,"city_l_per_100km":8.2,"hwy_l_per_100km":6.3,"zero_to_sixty":8.2,"reliability_score":0.82},
  {"id":"honda_civic_2020","make":"Honda","model":"Civic","year":2020,"price":23000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.3,"city_l_per_100km":8.1,"hwy_l_per_100km":6.2,"zero_to_sixty":8.0,"reliability_score":0.83},
  {"id":"honda_accord_2018","make":"Honda","model":"Accord","year":2018,"price":24000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.8,"city_l_per_100km":8.8,"hwy_l_per_100km":6.7,"zero_to_sixty":7.4,"reliability_score":0.80},
  {"id":"honda_crv_2018","make":"Honda","model":"CR-V","year":2018,"price":26000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.7,"city_l_per_100km":9.6,"hwy_l_per_100km":7.6,"zero_to_sixty":8.3,"reliability_score":0.81},
  {"id":"honda_hrv_2019","make":"Honda","model":"HR-V","year":2019,"price":22000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.4,"city_l_per_100km":9.1,"hwy_l_per_100km":7.5,"zero_to_sixty":9.5,"reliability_score":0.78},

  {"id":"toyota_corolla_2019","make":"Toyota","model":"Corolla","year":2019,"price":18500,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.1,"city_l_per_100km":7.9,"hwy_l_per_100km":6.2,"zero_to_sixty":8.5,"reliability_score":0.87},
  {"id":"toyota_corolla_2021","make":"Toyota","model":"Corolla","year":2021,"price":23000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":6.9,"city_l_per_100km":7.6,"hwy_l_per_100km":6.0,"zero_to_sixty":8.2,"reliability_score":0.88},
  {"id":"toyota_camry_2018","make":"Toyota","model":"Camry","year":2018,"price":24000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.9,"city_l_per_100km":8.8,"hwy_l_per_100km":6.8,"zero_to_sixty":7.6,"reliability_score":0.85},
  {"id":"toyota_rav4_2019","make":"Toyota","model":"RAV4","year":2019,"price":29000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.7,"city_l_per_100km":9.5,"hwy_l_per_100km":7.8,"zero_to_sixty":8.5,"reliability_score":0.86},
  {"id":"toyota_highlander_2018","make":"Toyota","model":"Highlander","year":2018,"price":32000,"drivetrain":"AWD","seats":7,"fuel_type":"gas","combined_l_per_100km":10.7,"city_l_per_100km":11.8,"hwy_l_per_100km":9.5,"zero_to_sixty":8.0,"reliability_score":0.83},

  {"id":"mazda3_2018","make":"Mazda","model":"Mazda3","year":2018,"price":17500,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.2,"city_l_per_100km":8.0,"hwy_l_per_100km":6.3,"zero_to_sixty":8.3,"reliability_score":0.80},
  {"id":"mazda3_2020","make":"Mazda","model":"Mazda3","year":2020,"price":23000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.7,"city_l_per_100km":8.6,"hwy_l_per_100km":6.6,"zero_to_sixty":8.1,"reliability_score":0.81},
  {"id":"mazda6_2018","make":"Mazda","model":"Mazda6","year":2018,"price":22000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.1,"city_l_per_100km":9.1,"hwy_l_per_100km":6.9,"zero_to_sixty":7.8,"reliability_score":0.78},
  {"id":"mazda_cx5_2019","make":"Mazda","model":"CX-5","year":2019,"price":27000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":9.0,"city_l_per_100km":10.0,"hwy_l_per_100km":7.9,"zero_to_sixty":8.2,"reliability_score":0.79},
  {"id":"mazda_cx30_2021","make":"Mazda","model":"CX-30","year":2021,"price":28000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.2,"city_l_per_100km":9.1,"hwy_l_per_100km":7.1,"zero_to_sixty":8.1,"reliability_score":0.80},

  {"id":"subaru_impreza_2018","make":"Subaru","model":"Impreza","year":2018,"price":19000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.0,"city_l_per_100km":8.8,"hwy_l_per_100km":7.0,"zero_to_sixty":9.0,"reliability_score":0.75},
  {"id":"subaru_crosstrek_2019","make":"Subaru","model":"Crosstrek","year":2019,"price":25000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.5,"city_l_per_100km":9.3,"hwy_l_per_100km":7.4,"zero_to_sixty":9.3,"reliability_score":0.76},
  {"id":"subaru_forester_2018","make":"Subaru","model":"Forester","year":2018,"price":26000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.8,"city_l_per_100km":9.5,"hwy_l_per_100km":7.9,"zero_to_sixty":8.7,"reliability_score":0.74},
  {"id":"subaru_outback_2018","make":"Subaru","model":"Outback","year":2018,"price":27000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":9.4,"city_l_per_100km":10.2,"hwy_l_per_100km":8.3,"zero_to_sixty":8.5,"reliability_score":0.74},
  {"id":"subaru_legacy_2019","make":"Subaru","model":"Legacy","year":2019,"price":23000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.6,"city_l_per_100km":9.4,"hwy_l_per_100km":7.5,"zero_to_sixty":8.1,"reliability_score":0.73},

  {"id":"hyundai_elantra_2019","make":"Hyundai","model":"Elantra","year":2019,"price":16500,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.4,"city_l_per_100km":8.2,"hwy_l_per_100km":6.4,"zero_to_sixty":8.8,"reliability_score":0.76},
  {"id":"hyundai_elantra_2021","make":"Hyundai","model":"Elantra","year":2021,"price":21000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.2,"city_l_per_100km":8.0,"hwy_l_per_100km":6.2,"zero_to_sixty":8.6,"reliability_score":0.77},
  {"id":"hyundai_sonata_2019","make":"Hyundai","model":"Sonata","year":2019,"price":21000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.1,"city_l_per_100km":9.0,"hwy_l_per_100km":6.9,"zero_to_sixty":7.9,"reliability_score":0.75},
  {"id":"hyundai_tucson_2018","make":"Hyundai","model":"Tucson","year":2018,"price":21000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":10.0,"city_l_per_100km":11.2,"hwy_l_per_100km":8.5,"zero_to_sixty":9.1,"reliability_score":0.73},
  {"id":"hyundai_kona_2020","make":"Hyundai","model":"Kona","year":2020,"price":22000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.7,"city_l_per_100km":9.6,"hwy_l_per_100km":7.6,"zero_to_sixty":8.4,"reliability_score":0.74},

  {"id":"kia_forte_2019","make":"Kia","model":"Forte","year":2019,"price":16000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.3,"city_l_per_100km":8.2,"hwy_l_per_100km":6.2,"zero_to_sixty":8.7,"reliability_score":0.75},
  {"id":"kia_optima_2018","make":"Kia","model":"Optima","year":2018,"price":19000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.2,"city_l_per_100km":9.2,"hwy_l_per_100km":6.9,"zero_to_sixty":7.9,"reliability_score":0.74},
  {"id":"kia_sportage_2019","make":"Kia","model":"Sportage","year":2019,"price":22000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":10.2,"city_l_per_100km":11.4,"hwy_l_per_100km":8.7,"zero_to_sixty":9.2,"reliability_score":0.72},
  {"id":"kia_soul_2020","make":"Kia","model":"Soul","year":2020,"price":21000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.4,"city_l_per_100km":9.3,"hwy_l_per_100km":7.2,"zero_to_sixty":9.0,"reliability_score":0.73},
  {"id":"kia_seltos_2021","make":"Kia","model":"Seltos","year":2021,"price":26000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.8,"city_l_per_100km":9.8,"hwy_l_per_100km":7.6,"zero_to_sixty":8.4,"reliability_score":0.74},

  {"id":"ford_focus_2017","make":"Ford","model":"Focus","year":2017,"price":12000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.9,"city_l_per_100km":8.9,"hwy_l_per_100km":6.7,"zero_to_sixty":8.7,"reliability_score":0.62},
  {"id":"ford_fusion_2018","make":"Ford","model":"Fusion","year":2018,"price":17000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.7,"city_l_per_100km":9.7,"hwy_l_per_100km":7.4,"zero_to_sixty":8.2,"reliability_score":0.66},
  {"id":"ford_escape_2019","make":"Ford","model":"Escape","year":2019,"price":23000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":9.8,"city_l_per_100km":10.9,"hwy_l_per_100km":8.3,"zero_to_sixty":8.6,"reliability_score":0.67},
  {"id":"ford_edge_2018","make":"Ford","model":"Edge","year":2018,"price":25000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":11.0,"city_l_per_100km":12.4,"hwy_l_per_100km":9.1,"zero_to_sixty":7.8,"reliability_score":0.64},
  {"id":"ford_explorer_2018","make":"Ford","model":"Explorer","year":2018,"price":28000,"drivetrain":"AWD","seats":7,"fuel_type":"gas","combined_l_per_100km":12.3,"city_l_per_100km":13.7,"hwy_l_per_100km":10.4,"zero_to_sixty":7.7,"reliability_score":0.63},

  {"id":"chevy_cruze_2018","make":"Chevrolet","model":"Cruze","year":2018,"price":14000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.6,"city_l_per_100km":8.5,"hwy_l_per_100km":6.5,"zero_to_sixty":8.9,"reliability_score":0.68},
  {"id":"chevy_malibu_2019","make":"Chevrolet","model":"Malibu","year":2019,"price":18000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.2,"city_l_per_100km":9.2,"hwy_l_per_100km":7.0,"zero_to_sixty":8.1,"reliability_score":0.66},
  {"id":"chevy_equinox_2019","make":"Chevrolet","model":"Equinox","year":2019,"price":22000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":9.9,"city_l_per_100km":11.0,"hwy_l_per_100km":8.3,"zero_to_sixty":8.7,"reliability_score":0.65},
  {"id":"chevy_trax_2020","make":"Chevrolet","model":"Trax","year":2020,"price":19000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":9.2,"city_l_per_100km":10.3,"hwy_l_per_100km":7.8,"zero_to_sixty":9.5,"reliability_score":0.64},
  {"id":"chevy_traverse_2018","make":"Chevrolet","model":"Traverse","year":2018,"price":30000,"drivetrain":"AWD","seats":7,"fuel_type":"gas","combined_l_per_100km":12.1,"city_l_per_100km":13.6,"hwy_l_per_100km":10.1,"zero_to_sixty":7.6,"reliability_score":0.64},

  {"id":"nissan_sentra_2019","make":"Nissan","model":"Sentra","year":2019,"price":15000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.6,"city_l_per_100km":8.5,"hwy_l_per_100km":6.6,"zero_to_sixty":9.0,"reliability_score":0.66},
  {"id":"nissan_altima_2019","make":"Nissan","model":"Altima","year":2019,"price":21000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.3,"city_l_per_100km":9.1,"hwy_l_per_100km":7.2,"zero_to_sixty":7.8,"reliability_score":0.67},
  {"id":"nissan_rogue_2018","make":"Nissan","model":"Rogue","year":2018,"price":22000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.8,"city_l_per_100km":9.7,"hwy_l_per_100km":7.7,"zero_to_sixty":8.4,"reliability_score":0.66},
  {"id":"nissan_qashqai_2019","make":"Nissan","model":"Qashqai","year":2019,"price":20000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":8.9,"city_l_per_100km":9.9,"hwy_l_per_100km":7.6,"zero_to_sixty":9.2,"reliability_score":0.65},
  {"id":"nissan_murano_2018","make":"Nissan","model":"Murano","year":2018,"price":26000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":10.7,"city_l_per_100km":11.8,"hwy_l_per_100km":9.2,"zero_to_sixty":7.5,"reliability_score":0.64},

  {"id":"vw_golf_2018","make":"Volkswagen","model":"Golf","year":2018,"price":17000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":7.1,"city_l_per_100km":8.0,"hwy_l_per_100km":6.0,"zero_to_sixty":8.3,"reliability_score":0.70},
  {"id":"vw_jetta_2019","make":"Volkswagen","model":"Jetta","year":2019,"price":18000,"drivetrain":"FWD","seats":5,"fuel_type":"gas","combined_l_per_100km":6.8,"city_l_per_100km":7.6,"hwy_l_per_100km":5.8,"zero_to_sixty":8.4,"reliability_score":0.71},
  {"id":"vw_tiguan_2019","make":"Volkswagen","model":"Tiguan","year":2019,"price":26000,"drivetrain":"AWD","seats":7,"fuel_type":"gas","combined_l_per_100km":10.0,"city_l_per_100km":11.1,"hwy_l_per_100km":8.5,"zero_to_sixty":8.9,"reliability_score":0.70},
  {"id":"mitsubishi_rvr_2019","make":"Mitsubishi","model":"RVR","year":2019,"price":19000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":9.5,"city_l_per_100km":10.6,"hwy_l_per_100km":8.0,"zero_to_sixty":10.0,"reliability_score":0.68},
  {"id":"gmc_terrain_2019","make":"GMC","model":"Terrain","year":2019,"price":24000,"drivetrain":"AWD","seats":5,"fuel_type":"gas","combined_l_per_100km":10.1,"city_l_per_100km":11.2,"hwy_l_per_100km":8.6,"zero_to_sixty":8.8,"reliability_score":0.65}
]


DATA_DIR = Path(__file__).resolve().parent
CACHE_FILE = DATA_DIR / "cache" / "vehicles.json"


def _read_cache() -> Tuple[List[Dict[str, Any]], bool, Optional[str]]:
    """
    Return data, using_mock flag, and last_updated timestamp (ISO) if cache exists.
    """
    if CACHE_FILE.exists():
        try:
            with CACHE_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                ts = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime).isoformat()
                return data, False, ts
        except (OSError, json.JSONDecodeError):
            pass
    return MOCK_CARS, True, None


def load_cars() -> List[Dict[str, Any]]:
    """
    Load cars from the cached catalog file if present; otherwise fall back to MOCK_CARS.
    """
    data, _, _ = _read_cache()
    return data


def load_cars_with_meta() -> Tuple[List[Dict[str, Any]], bool, Optional[str]]:
    """
    Return cars, a flag indicating if mock data was used, and last_updated timestamp.
    """
    return _read_cache()
