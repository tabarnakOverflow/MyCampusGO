from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Tuple
from time import time

@dataclass
class TTLCache:
    ttl_seconds: int
    _store: Dict[str, Tuple[float, Any]]

    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self._store = {}

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if not item:
            return None
        ts, value = item
        if (time() - ts) > self.ttl_seconds:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time(), value)

async def cached(cache: TTLCache, key: str, fn: Callable[[], Awaitable[Any]]) -> Any:
    v = cache.get(key)
    if v is not None:
        return v
    v = await fn()
    cache.set(key, v)
    return v
