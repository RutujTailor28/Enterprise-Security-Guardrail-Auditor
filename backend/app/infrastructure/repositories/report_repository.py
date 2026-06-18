"""Report repository."""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.infrastructure.database.models import ReportModel


class ReportRepository:
    def __init__(self, session: Session):
        self._session = session

    def upsert(self, scan_id: str, file_path: str, content_hash: str) -> None:
        existing = self._session.query(ReportModel).filter_by(scan_id=scan_id).first()
        if existing:
            existing.file_path = file_path
            existing.content_hash = content_hash
            existing.generated_at = datetime.utcnow()
        else:
            self._session.add(
                ReportModel(
                    id=str(uuid.uuid4()),
                    scan_id=scan_id,
                    file_path=file_path,
                    content_hash=content_hash,
                    generated_at=datetime.utcnow(),
                )
            )
        self._session.flush()

    def get_by_scan_id(self, scan_id: str) -> ReportModel | None:
        return self._session.query(ReportModel).filter_by(scan_id=scan_id).first()
