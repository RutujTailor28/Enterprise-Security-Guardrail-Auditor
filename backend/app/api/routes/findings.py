"""Finding routes."""

import math

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_scan_service
from app.api.exceptions import NotFoundError
from app.api.middleware.request_id import get_request_id
from app.api.schemas.common import wrap_data
from app.application.scan_service import ScanService
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.finding_repository import FindingRepository

router = APIRouter(prefix="/scans", tags=["findings"])


@router.get("/{scan_id}/findings")
def list_findings(
    request: Request,
    scan_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: str | None = None,
    rule_id: str | None = None,
    q: str | None = None,
    scan_service: ScanService = Depends(get_scan_service),
    session: Session = Depends(get_db),
):
    if not scan_service._scan_repo.get_by_id(scan_id):
        raise NotFoundError(f"Scan '{scan_id}' not found")
    repo = FindingRepository(session)
    findings, total = repo.list_by_scan(scan_id, page, page_size, severity, rule_id, q)
    total_pages = math.ceil(total / page_size) if page_size else 0
    data = [
        scan_service._finding_to_dict(f) for f in findings
    ]
    return {
        "data": data,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "request_id": get_request_id(request),
            "timestamp": wrap_data({}, get_request_id(request))["meta"]["timestamp"],
        },
    }
