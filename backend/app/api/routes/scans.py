"""Scan routes."""

import math

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    Query,
    Request,
    UploadFile,
    status,
)

from app.api.deps import get_scan_service
from app.api.middleware.request_id import get_request_id
from app.api.schemas.common import wrap_data
from app.application.scan_service import ScanService

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_scan(
    request: Request,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    label: str | None = Form(default=None),
    scan_service: ScanService = Depends(get_scan_service),
):
    data = await scan_service.create_scan(files, label, background_tasks)
    return wrap_data(data, get_request_id(request))


@router.get("")
def list_scans(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    sort: str = Query("-created_at"),
    scan_service: ScanService = Depends(get_scan_service),
):
    items, total = scan_service.list_scans(page, page_size, status_filter, sort)
    total_pages = math.ceil(total / page_size) if page_size else 0
    return {
        "data": items,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "request_id": get_request_id(request),
            "timestamp": wrap_data({}, get_request_id(request))["meta"]["timestamp"],
        },
    }


@router.get("/{scan_id}")
def get_scan(
    request: Request,
    scan_id: str,
    include: str | None = Query(None),
    scan_service: ScanService = Depends(get_scan_service),
):
    include_set = set(include.split(",")) if include else set()
    data = scan_service.get_scan(scan_id, include_set)
    return wrap_data(data, get_request_id(request))


@router.post("/{scan_id}/cancel")
def cancel_scan(
    request: Request,
    scan_id: str,
    scan_service: ScanService = Depends(get_scan_service),
):
    data = scan_service.cancel_scan(scan_id)
    return wrap_data(data, get_request_id(request))


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scan(scan_id: str, scan_service: ScanService = Depends(get_scan_service)):
    scan_service.delete_scan(scan_id)
