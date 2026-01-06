# Car Recommender AI

Personalized car recommendations backed by a FastAPI service and a simple web UI.
The backend scores vehicles on winter driving, fuel efficiency, price fit, ownership
cost, acceleration, and reliability, then returns the top matches.

## Features
- Weighted multi-factor scoring with presets
- FastAPI JSON API for recommendations + model lookup
- Optional data sync from public sources (CarQuery, EPA, NHTSA)
- Mock catalog fallback so the app runs out of the box

## Stack
- Backend: Python, FastAPI, Pydantic
- Frontend: Vanilla HTML/CSS/JS
- Data sources: CarQuery API, EPA FuelEconomy API, NHTSA Complaints/Recalls

## Quick start

### Backend
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
Open `frontend/index.html` in a browser. The UI talks to the backend at
`http://127.0.0.1:8000` by default (see `frontend/app.js`).

## API

### `POST /recommend`
Returns the top 5 vehicles by weighted score.

Example:
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/recommend -Method Post -ContentType "application/json" -Body @'
{
  "budget": 20000,
  "location": "NY",
  "annual_km": 12000,
  "passengers": 4,
  "fuel_type": "ICE",
  "priorities": ["fuel", "winter", "price"],
  "weights": {
    "winter_driving": 0.2,
    "fuel_efficiency": 0.2,
    "price_fit": 0.2,
    "ownership_cost": 0.2,
    "acceleration": 0.1,
    "reliability": 0.1
  }
}
'@
```

### `GET /models`
Returns unique make/model/year combinations in the catalog.

### `GET /nhtsa/issues?make=Toyota&model=Camry&model_year=2019`
Returns complaint and recall counts from NHTSA.

### `GET /`
Health + catalog metadata.

## Data sync (optional)
The backend uses a cached catalog if present; otherwise it falls back to a small
mock dataset in `backend/app/data/catalog.py`.

To build a cached catalog using public APIs:
```powershell
cd backend
python scripts\sync_catalog.py
```

This writes `backend/app/data/cache/vehicles.json`. Expand `MAKES` and `YEARS` in
`backend/scripts/sync_catalog.py` as needed, and keep the list small to respect
free API rate limits.

## Project structure
```
backend/
  app/
    main.py            FastAPI routes
    recommender.py     Scoring logic
    services/          External API clients
    data/              Catalog + seed data
  scripts/             Data sync tooling
frontend/
  index.html           UI
  app.js               UI logic + API calls
  styles.css           UI styling
```

## Notes
- The scoring model is intentionally transparent and easy to tweak.
- Fuel efficiency and cost scoring are normalized to 0..1 and weighted by user
  preferences.

## Next ideas
- Add more trims and years to the catalog
- Persist user profiles and favorites
- Add a lightweight explanation panel per recommendation
