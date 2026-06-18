"""Shared API schemas."""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MetaResponse(BaseModel):
    request_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorBody
    meta: MetaResponse


class DataResponse(BaseModel, Generic[T]):
    data: T
    meta: MetaResponse


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PaginationMeta
    request_meta: MetaResponse


class SeverityCounts(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


def wrap_data(data: Any, request_id: str) -> dict[str, Any]:
    return {
        "data": data,
        "meta": {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    }
