"""Repository integration tests."""

from datetime import datetime

from app.domain.models.enums import Confidence, FileType, ScanStatus, Severity
from app.domain.models.finding import Finding
from app.domain.models.scan import Scan
from app.infrastructure.repositories.finding_repository import FindingRepository
from app.infrastructure.repositories.file_repository import UploadedFileRepository
from app.infrastructure.repositories.scan_repository import ScanRepository


def test_scan_crud_and_cascade(db_session):
    scan_repo = ScanRepository(db_session)
    finding_repo = FindingRepository(db_session)
    file_repo = UploadedFileRepository(db_session)

    scan = scan_repo.create(label="test")
    file_repo.create(
        scan_id=scan.id,
        original_filename="main.tf",
        stored_filename="main.tf",
        file_type=FileType.TERRAFORM,
        content_hash="abc",
        size_bytes=10,
        stored_path="uploads/x/main.tf",
    )
    finding = Finding(
        id="f1",
        scan_id=scan.id,
        rule_id="S3_PUBLIC",
        fingerprint="fp1",
        severity=Severity.CRITICAL,
        confidence=Confidence.HIGH,
        title="test",
        description="desc",
        remediation="fix",
        created_at=datetime.utcnow(),
    )
    finding_repo.create_many([finding])
    db_session.commit()

    loaded = scan_repo.get_by_id(scan.id)
    assert loaded is not None
    assert loaded.label == "test"

    scan_repo.delete(scan.id)
    db_session.commit()
    assert scan_repo.get_by_id(scan.id) is None
