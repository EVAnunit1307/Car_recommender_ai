# Car Recommender

A FastAPI service and lightweight web UI for generating data-driven car recommendations.

## Highlights
- Weighted multi-factor scoring for recommendations
- FastAPI JSON API for recommendations, models, and safety issues
- Optional Kaggle dataset sync with cached catalog support
- NHTSA complaints/recalls enrichment for reliability and safety scoring
- Clean, dependency-light frontend

## Architecture
```
backend/
  app/
    main.py            FastAPI routes
    recommender.py     Scoring logic
    recommendations.py Recommendation orchestration
    services/          External API clients
    data/              Catalog + cached data
  scripts/             Data sync tooling
frontend/
  index.html           UI
  app.js               UI logic + API calls
  styles.css           UI styling
```

## Requirements
- Python 3.10+
- Node.js not required

## Quick start
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `frontend/index.html` in a browser. The UI targets `http://127.0.0.1:8000` by default.

## Environment variables
- `GOOGLE_API_KEY` (required for `/chat/*` endpoints)
- `GEMINI_MODEL` (optional, default: `gemini-1.5-flash`)

## API

### `POST /recommend`
Returns the top 5 vehicles by weighted score.

Example:
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/recommend -Method Post -ContentType "application/json" -Body (Get-Content request.json -Raw)
```

### `GET /models`
Returns unique make/model/year combinations in the catalog.

### `GET /nhtsa/issues?make=Toyota&model=Camry&model_year=2019`
Returns complaint and recall counts from NHTSA.

### `GET /`
Health + catalog metadata.

### `POST /chat/message`
Send a message to the assistant.

### `GET /chat/history/{session_id}`
Retrieve chat history for a session.

### `POST /chat/reset/{session_id}`
Clear chat history for a session.

## Data sync
The backend uses a cached catalog if present; otherwise it falls back to a small
mock dataset in `backend/app/data/catalog.py`.

### Kaggle dataset sync
1) Configure Kaggle credentials:
   - Create an API token at https://www.kaggle.com/account
   - Save `kaggle.json` to `C:\Users\<You>\.kaggle\kaggle.json`

2) Run the sync script:
```powershell
cd backend
python scripts\sync_kaggle_catalog.py
```

This writes `backend/app/data/cache/kaggle_vehicles.json`, which is preferred
when present.

### Public API catalog sync
```powershell
cd backend
python scripts\sync_catalog.py
```

This writes `backend/app/data/cache/vehicles.json`. Expand `MAKES` and `YEARS` in
`backend/scripts/sync_catalog.py` as needed.

### NHTSA enrichment
```powershell
cd backend
python scripts\enrich_nhtsa.py
```

The script caches results for 30 days to respect API limits.
