"""Report generation service."""

from sqlalchemy.orm import Session

from app.api.exceptions import NotFoundError, ScanInProgressError
from app.domain.models.enums import ScanStatus
from app.infrastructure.repositories.finding_repository import FindingRepository
from app.infrastructure.repositories.scan_repository import ScanRepository
from app.infrastructure.reports.csv_exporter import export_findings_csv
from app.infrastructure.reports.pdf_generator import generate_scan_pdf


class ReportService:
    def __init__(self, session: Session):
        self._scan_repo = ScanRepository(session)
        self._finding_repo = FindingRepository(session)

    def _get_completed_scan(self, scan_id: str):
        scan = self._scan_repo.get_by_id(scan_id)
        if not scan:
            raise NotFoundError(f"Scan '{scan_id}' not found")
        if scan.status in (ScanStatus.PENDING, ScanStatus.PROCESSING):
            raise ScanInProgressError()
        return scan

    def generate_pdf(self, scan_id: str) -> bytes:
        scan = self._get_completed_scan(scan_id)
        findings, _ = self._finding_repo.list_by_scan(scan_id, page=1, page_size=500)
        return generate_scan_pdf(scan, findings)

    def generate_csv(self, scan_id: str) -> bytes:
        self._get_completed_scan(scan_id)
        findings, _ = self._finding_repo.list_by_scan(scan_id, page=1, page_size=5000)
        return export_findings_csv(findings)
