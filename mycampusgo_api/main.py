from __future__ import annotations

from fastapi import FastAPI, HTTPException
from typing import List

from .models import EventSummary, EventDetail, Announcement
from .scrape import scrape_events, scrape_event_detail, scrape_announcements
from .cache import TTLCache, cached
from .config import settings

app = FastAPI(title="MyCampusGO Scraper API", version="0.1")

cache = TTLCache(settings.cache_ttl_seconds)

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/events", response_model=List[EventSummary])
async def get_events(days_back: int = 7):
    if days_back < 0 or days_back > 365:
        raise HTTPException(status_code=400, detail="days_back must be between 0 and 365")
    return await cached(cache, f"events:{days_back}", lambda: scrape_events(days_back=days_back))

@app.get("/events/{slug}", response_model=EventDetail)
async def get_event_detail(slug: str):
    detail = await cached(cache, f"event:{slug}", lambda: scrape_event_detail(slug))
    if detail is None:
        raise HTTPException(status_code=404, detail="Event not found or could not parse")
    return detail

@app.get("/announcements", response_model=List[Announcement])
async def get_announcements():
    return await cached(cache, "announcements", scrape_announcements)
