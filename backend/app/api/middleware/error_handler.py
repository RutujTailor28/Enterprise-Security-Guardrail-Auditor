"""Global error handlers."""

import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.exceptions import AppError
from app.api.middleware.request_id import get_request_id

logger = logging.getLogger(__name__)


def build_error_response(error: AppError, request_id: str) -> dict[str, Any]:
    return {
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details,
        },
        "meta": {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        request_id = get_request_id(request)
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_response(exc, request_id),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = get_request_id(request)
        details = [
            {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
            for e in exc.errors()
        ]
        error = AppError("VALIDATION_ERROR", "Request validation failed", 400, details)
        return JSONResponse(status_code=400, content=build_error_response(error, request_id))

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        request_id = get_request_id(request)
        error = AppError("HTTP_ERROR", str(exc.detail), exc.status_code)
        return JSONResponse(status_code=exc.status_code, content=build_error_response(error, request_id))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = get_request_id(request)
        logger.exception("Unhandled error request_id=%s: %s", request_id, exc)
        error = AppError("INTERNAL_ERROR", "An unexpected error occurred", 500)
        return JSONResponse(status_code=500, content=build_error_response(error, request_id))
