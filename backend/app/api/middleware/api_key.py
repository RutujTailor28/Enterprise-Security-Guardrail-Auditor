"""Optional API key authentication middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import get_settings


class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        if not settings.api_key:
            return await call_next(request)

        path = request.url.path
        if path.endswith("/health") or path.endswith("/health/ready"):
            return await call_next(request)

        provided = request.headers.get("X-API-Key")
        if provided != settings.api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Valid API key required",
                    }
                },
            )
        return await call_next(request)
