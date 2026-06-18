"""Report export routes."""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_scan_service
from app.application.report_service import ReportService
from app.application.scan_service import ScanService
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/scans", tags=["reports"])


@router.get("/{scan_id}/report.pdf")
def download_pdf(scan_id: str, session: Session = Depends(get_db)):
    pdf_bytes = ReportService(session).generate_pdf(scan_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="scan-{scan_id[:8]}-report.pdf"'},
    )


@router.get("/{scan_id}/findings.csv")
def download_csv(scan_id: str, session: Session = Depends(get_db)):
    csv_bytes = ReportService(session).generate_csv(scan_id)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="scan-{scan_id[:8]}-findings.csv"'},
    )


@router.get("/{scan_id}/reports")
def list_report_info(scan_id: str, scan_service: ScanService = Depends(get_scan_service)):
    scan = scan_service.get_scan(scan_id)
    return {
        "data": {
            "scan_id": scan_id,
            "label": scan.get("label"),
            "status": scan.get("status"),
            "risk_score": scan.get("risk_score"),
            "risk_grade": scan.get("risk_grade"),
            "findings_total": scan.get("findings_total"),
            "pdf_url": f"/api/v1/scans/{scan_id}/report.pdf",
            "csv_url": f"/api/v1/scans/{scan_id}/findings.csv",
            "generated_at": None,
        }
    }
