"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.api_key import ApiKeyMiddleware
from app.api.middleware.error_handler import register_exception_handlers
from app.api.middleware.logging import LoggingMiddleware
from app.api.middleware.rate_limiter import RateLimiterMiddleware
from app.api.middleware.request_id import RequestIdMiddleware
from app.api.middleware.security_headers import SecurityHeadersMiddleware
from app.api.router import api_router
from app.config import get_settings
from app.infrastructure.database.session import ensure_data_dirs, run_migrations

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_data_dirs()
    run_migrations()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Accept", "X-Request-ID", "X-API-Key"],
    )
    app.add_middleware(ApiKeyMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimiterMiddleware)

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
