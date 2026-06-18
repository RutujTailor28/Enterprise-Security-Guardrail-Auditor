"""Uploaded file routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from app.api.deps import get_scan_service
from app.api.middleware.request_id import get_request_id
from app.api.schemas.common import wrap_data
from app.application.scan_service import ScanService
from app.infrastructure.storage.safe_http import content_disposition_attachment

router = APIRouter(prefix="/scans", tags=["files"])


@router.get("/{scan_id}/files")
def list_files(
    request: Request,
    scan_id: str,
    scan_service: ScanService = Depends(get_scan_service),
):
    data = scan_service.get_scan(scan_id, {"files"})
    return wrap_data(data.get("files", []), get_request_id(request))


@router.get("/{scan_id}/files/{file_id}")
def download_file(
    scan_id: str,
    file_id: str,
    scan_service: ScanService = Depends(get_scan_service),
):
    content, filename = scan_service.get_file_content(scan_id, file_id)
    return Response(
        content=content,
        media_type="text/plain",
        headers={
            "Content-Disposition": content_disposition_attachment(filename, "upload.txt"),
        },
    )
