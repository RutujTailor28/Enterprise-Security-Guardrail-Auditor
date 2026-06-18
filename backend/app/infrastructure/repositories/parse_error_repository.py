"""Parse error repository."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.parse_error import ParseErrorRecord
from app.infrastructure.database.models import ParseErrorModel
from app.infrastructure.repositories.mappers import parse_error_to_domain


class ParseErrorRepository:
    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        scan_id: str,
        filename: str,
        error_code: str,
        message: str,
        line_number: int | None = None,
    ) -> ParseErrorRecord:
        model = ParseErrorModel(
            id=str(uuid.uuid4()),
            scan_id=scan_id,
            filename=filename,
            error_code=error_code,
            message=message,
            line_number=line_number,
            created_at=datetime.utcnow(),
        )
        self._session.add(model)
        self._session.flush()
        return parse_error_to_domain(model)

    def list_by_scan(self, scan_id: str) -> list[ParseErrorRecord]:
        models = self._session.scalars(
            select(ParseErrorModel).where(ParseErrorModel.scan_id == scan_id)
        ).all()
        return [parse_error_to_domain(m) for m in models]
