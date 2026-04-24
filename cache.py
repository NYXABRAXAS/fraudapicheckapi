from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any

import redis

from app.core.config import get_settings


class InMemoryCache:
    def __init__(self) -> None:
        self._lock = Lock()
        self._values: dict[str, tuple[Any, datetime | None]] = {}
        self._counters: dict[str, int] = defaultdict(int)

    def get(self, key: str) -> Any | None:
        with self._lock:
            value = self._values.get(key)
            if not value:
                return None
            payload, expires_at = value
            if expires_at and expires_at < datetime.now(timezone.utc):
                self._values.pop(key, None)
                return None
            return payload

    def setex(self, key: str, ttl_seconds: int, value: Any) -> None:
        with self._lock:
            self._values[key] = (
                value,
                datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
            )

    def incr(self, key: str) -> int:
        with self._lock:
            self._counters[key] += 1
            return self._counters[key]

    def expire(self, key: str, ttl_seconds: int) -> None:
        with self._lock:
            value = self._counters.get(key)
            if value is None:
                return
            self._values[f"counter:{key}"] = (
                value,
                datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
            )


class CacheClient:
    def __init__(self) -> None:
        self._client: redis.Redis | InMemoryCache | None = None

    def get_client(self) -> redis.Redis | InMemoryCache:
        if self._client:
            return self._client
        settings = get_settings()
        try:
            client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
            client.ping()
            self._client = client
        except redis.RedisError:
            self._client = InMemoryCache()
        return self._client


cache_client = CacheClient()
