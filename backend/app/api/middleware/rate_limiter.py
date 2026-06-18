"""In-memory rate limiter middleware."""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.api.exceptions import RateLimitedError
from app.api.middleware.error_handler import build_error_response
from app.api.middleware.request_id import get_request_id
from app.config import get_settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _client_key(self, request: Request) -> str:
        if request.client:
            return request.client.host
        return "unknown"

    def _is_limited(self, key: str, limit: int) -> bool:
        now = time.time()
        window_start = now - 60
        self._hits[key] = [t for t in self._hits[key] if t > window_start]
        if len(self._hits[key]) >= limit:
            return True
        self._hits[key].append(now)
        return False

    async def dispatch(self, request: Request, call_next) -> Response:
        settings = get_settings()
        if self._is_limited(self._client_key(request), settings.rate_limit_per_minute):
            request_id = get_request_id(request)
            error = RateLimitedError()
            body = build_error_response(error, request_id)
            return JSONResponse(status_code=429, content=body, headers={"Retry-After": "60"})
        return await call_next(request)
