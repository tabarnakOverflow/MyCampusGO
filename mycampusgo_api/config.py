from __future__ import annotations

from dataclasses import dataclass
from zoneinfo import ZoneInfo

@dataclass(frozen=True)
class Settings:
    base_url: str = "https://www.stfx.ca"
    events_path: str = "/events"
    announcements_path: str = "/mycampus/announcements"
    timezone: ZoneInfo = ZoneInfo("America/Halifax")
    user_agent: str = "MyCampusGO-SchoolProject/0.1 (+contact: student project)"
    cache_ttl_seconds: int = 300

settings = Settings()
