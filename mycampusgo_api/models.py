from __future__ import annotations

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventSummary(BaseModel):
    title: str
    url: str
    slug: str
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    teaser: Optional[str] = None
    image_url: Optional[str] = None

class EventDetail(BaseModel):
    title: str
    url: str
    slug: str
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    image_url: Optional[str] = None

class Announcement(BaseModel):
    headline: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    is_new: bool = False
