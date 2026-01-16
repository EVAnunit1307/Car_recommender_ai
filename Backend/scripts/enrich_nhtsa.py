"""
Script to enrich vehicle catalog with NHTSA safety and reliability data.

Fetches complaints, recalls, and calculates safety/reliability scores for all vehicles in the catalog.
"""
import sys
import json
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.data.catalog import load_cars, CACHE_FILE, DATA_DIR
from app.services.nhtsa_issues import get_complaints_and_recalls


def enrich_catalog_with_nhtsa():
    """
    Load existing catalog and enrich each vehicle with NHTSA data.
    Updates the cached catalog file with new safety/reliability information.
    """
    print("🚗 Loading vehicle catalog...")
    vehicles = load_cars()
    print(f"   Found {len(vehicles)} vehicles")
    
    enriched = []
    failed = []
    
    for idx, car in enumerate(vehicles, 1):
        make = car.get("make")
        model = car.get("model")
        year = car.get("year")
        
        if not (make and model and year):
            print(f"⚠️  Skipping vehicle {idx}/{len(vehicles)}: Missing make/model/year")
            enriched.append(car)
            continue
        
        print(f"📡 [{idx}/{len(vehicles)}] Fetching NHTSA data for {year} {make} {model}...", end=" ")
        
        try:
            nhtsa_data = get_complaints_and_recalls(year, make, model, use_cache=True)
            
            if "error" in nhtsa_data:
                print(f"❌ FAILED")
                failed.append(f"{year} {make} {model}")
                enriched.append(car)
            else:
                # Merge NHTSA data into car record
                car_enriched = {
                    **car,
                    "complaints_count": nhtsa_data.get("complaints_count", 0),
                    "recalls_count": nhtsa_data.get("recalls_count", 0),
                    "reliability_score": nhtsa_data.get("reliability_score", 0.5),
                    "safety_score": nhtsa_data.get("safety_score", 0.5),
                }
                enriched.append(car_enriched)
                print(f"✅ (Complaints: {nhtsa_data['complaints_count']}, Recalls: {nhtsa_data['recalls_count']})")
            
            # Rate limiting: sleep between requests to avoid hitting API limits
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed.append(f"{year} {make} {model}")
            enriched.append(car)
    
    # Save enriched catalog
    print("\n💾 Saving enriched catalog...")
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_FILE.open("w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2)
    
    print(f"\n✅ Enrichment complete!")
    print(f"   Total vehicles: {len(enriched)}")
    print(f"   Successfully enriched: {len(enriched) - len(failed)}")
    print(f"   Failed: {len(failed)}")
    
    if failed:
        print(f"\n⚠️  Failed vehicles:")
        for vehicle in failed:
            print(f"   - {vehicle}")
    
    print(f"\n📁 Catalog saved to: {CACHE_FILE}")


if __name__ == "__main__":
    enrich_catalog_with_nhtsa()
