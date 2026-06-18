"""Uploaded file repository."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.enums import FileType
from app.infrastructure.database.models import UploadedFileModel
from app.infrastructure.repositories.mappers import UploadedFileRecord, uploaded_file_to_record


class UploadedFileRepository:
    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        scan_id: str,
        original_filename: str,
        stored_filename: str,
        file_type: FileType,
        content_hash: str,
        size_bytes: int,
        stored_path: str,
    ) -> UploadedFileRecord:
        model = UploadedFileModel(
            id=str(uuid.uuid4()),
            scan_id=scan_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_type=file_type.value,
            content_hash=content_hash,
            size_bytes=size_bytes,
            stored_path=stored_path,
            created_at=datetime.utcnow(),
        )
        self._session.add(model)
        self._session.flush()
        return uploaded_file_to_record(model)

    def list_by_scan(self, scan_id: str) -> list[UploadedFileRecord]:
        models = self._session.scalars(
            select(UploadedFileModel).where(UploadedFileModel.scan_id == scan_id)
        ).all()
        return [uploaded_file_to_record(m) for m in models]

    def get_by_id(self, file_id: str) -> UploadedFileRecord | None:
        model = self._session.get(UploadedFileModel, file_id)
        return uploaded_file_to_record(model) if model else None
