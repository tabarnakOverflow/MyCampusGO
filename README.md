# MyCampusGO Server

FastAPI + Uvicorn service that scrapes StFX events and announcements and exposes a JSON API for the MyCampusGO Android app.

## Run locally
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn mycampusgo_api.main:app --host 0.0.0.0 --port 8000

## Endpoints
- GET /health
- GET /events?days_back=7
- GET /events/{slug}
- GET /announcements
