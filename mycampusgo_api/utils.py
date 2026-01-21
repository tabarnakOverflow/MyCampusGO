from __future__ import annotations

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from dateutil import parser as dtparser

def abs_url(base: str, maybe_relative: str | None) -> str | None:
    if not maybe_relative:
        return None
    return urljoin(base, maybe_relative)

def slug_from_url(full_url: str) -> str:
    parts = full_url.rstrip("/").split("/")
    return parts[-1] if parts else ""

def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return dtparser.isoparse(value)
    except Exception:
        return None

def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return " ".join(soup.get_text(" ", strip=True).split())
