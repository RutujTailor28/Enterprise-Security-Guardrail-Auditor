"""Report service unit tests."""

import pytest

from app.api.exceptions import ScanInProgressError
from app.application.report_service import ReportService
from app.domain.models.enums import ScanStatus
from app.infrastructure.repositories.scan_repository import ScanRepository


def test_report_service_rejects_in_progress_scan(db_session):
    repo = ScanRepository(db_session)
    scan = repo.create(label="in-progress")
    scan.status = ScanStatus.PROCESSING
    repo.update(scan)
    db_session.commit()

    with pytest.raises(ScanInProgressError):
        ReportService(db_session).generate_pdf(scan.id)


def test_report_service_generates_pdf_for_completed_scan(db_session):
    repo = ScanRepository(db_session)
    scan = repo.create(label="done")
    scan.status = ScanStatus.COMPLETED
    scan.risk_score = 100
    scan.raw_risk_score = 0
    scan.file_count = 1
    repo.update(scan)
    db_session.commit()

    pdf_bytes = ReportService(db_session).generate_pdf(scan.id)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500
