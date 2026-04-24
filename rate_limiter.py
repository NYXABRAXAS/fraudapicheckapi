from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.db.session import get_cache


class RateLimitMiddleware(BaseHTTPMiddleware):
    _fallback_windows: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        identifier = request.client.host if request.client else "unknown"
        key = f"ratelimit:{identifier}:{int(time.time() // 60)}"
        cache = get_cache()

        try:
            current = cache.incr(key)
            if current == 1 and hasattr(cache, "expire"):
                cache.expire(key, 60)
        except Exception:
            now = time.time()
            window = self._fallback_windows[identifier]
            self._fallback_windows[identifier] = [ts for ts in window if now - ts < 60]
            self._fallback_windows[identifier].append(now)
            current = len(self._fallback_windows[identifier])

        if current > settings.rate_limit_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"},
            )

        return await call_next(request)
