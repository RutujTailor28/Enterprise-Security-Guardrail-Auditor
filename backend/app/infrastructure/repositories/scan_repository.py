"""Scan repository."""

import uuid
from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.domain.models.enums import ScanStatus
from app.domain.models.scan import Scan
from app.infrastructure.database.models import ScanModel
from app.infrastructure.repositories.mappers import scan_to_domain, scan_to_model


class ScanRepository:
    def __init__(self, session: Session):
        self._session = session

    def create(self, label: str | None = None) -> Scan:
        now = datetime.utcnow()
        scan = Scan(
            id=str(uuid.uuid4()),
            label=label,
            status=ScanStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._session.add(scan_to_model(scan))
        self._session.flush()
        return scan

    def get_by_id(self, scan_id: str) -> Scan | None:
        model = self._session.get(ScanModel, scan_id)
        return scan_to_domain(model) if model else None

    def update(self, scan: Scan) -> Scan:
        model = self._session.get(ScanModel, scan.id)
        if not model:
            return scan
        scan.updated_at = datetime.utcnow()
        for field in (
            "label",
            "status",
            "risk_score",
            "normalized_score",
            "raw_risk_score",
            "critical_count",
            "high_count",
            "medium_count",
            "low_count",
            "info_count",
            "resource_count",
            "file_count",
            "duration_ms",
            "parser_version",
            "error_message",
            "updated_at",
            "completed_at",
        ):
            value = getattr(scan, field)
            if field == "status":
                value = value.value
            setattr(model, field, value)
        self._session.flush()
        return scan_to_domain(model)

    def delete(self, scan_id: str) -> bool:
        model = self._session.get(ScanModel, scan_id)
        if not model:
            return False
        self._session.delete(model)
        self._session.flush()
        return True

    def list_scans(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        sort: str = "-created_at",
    ) -> tuple[list[Scan], int]:
        query = select(ScanModel)
        if status:
            query = query.where(ScanModel.status == status)
        if sort in ("created_at", "-created_at"):
            query = query.order_by(
                desc(ScanModel.created_at) if sort.startswith("-") else ScanModel.created_at
            )
        elif sort in ("risk_score", "-risk_score"):
            query = query.order_by(
                desc(ScanModel.risk_score) if sort.startswith("-") else ScanModel.risk_score
            )
        else:
            query = query.order_by(desc(ScanModel.created_at))

        count_query = select(func.count()).select_from(ScanModel)
        if status:
            count_query = count_query.where(ScanModel.status == status)
        total = self._session.scalar(count_query) or 0
        offset = (page - 1) * page_size
        models = self._session.scalars(query.offset(offset).limit(page_size)).all()
        return [scan_to_domain(m) for m in models], total
