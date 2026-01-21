# MyCampusGO Server

FastAPI + Uvicorn service that scrapes StFX events and announcements in order to expose an API for the MyCampusGO client.

## Run locally
python -m venv .venv \
source .venv/bin/activate \
pip install -r requirements.txt \
uvicorn mycampusgo_api.main:app --host 0.0.0.0 --port 8000 \

## Endpoints
- GET /health
- GET /events?days_back=7
- GET /events/{slug}
- GET /announcements

## Setup as Systemd Service
Ensure that the server is running with proper permissions in /opt/mycampusgo_server. Then edit mycampusgo.service to set the user that will be running the service. Move the service to /etc/systemd/system/, then sudo systemctl daemon-reload and sudo systemctl enable --now mycampusgo.service. \
