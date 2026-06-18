"""Health check routes."""

from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

from app.api.middleware.request_id import get_request_id
from app.api.schemas.common import wrap_data
from app.config import get_settings
from app.infrastructure.database.session import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health")
def health(request: Request):
    settings = get_settings()
    return wrap_data(
        {"status": "ok", "version": settings.app_version},
        get_request_id(request),
    )


@router.get("/health/ready")
def health_ready(request: Request):
    if not check_db_connection():
        return JSONResponse(
            status_code=503,
            content=wrap_data({"status": "unavailable"}, get_request_id(request)),
        )
    return wrap_data({"status": "ready"}, get_request_id(request))
