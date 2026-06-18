"""Scan rule repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models import ScanRuleModel
from app.infrastructure.repositories.mappers import ScanRuleRecord, scan_rule_to_record


class ScanRuleRepository:
    def __init__(self, session: Session):
        self._session = session

    def list_all(self) -> list[ScanRuleRecord]:
        models = self._session.scalars(select(ScanRuleModel).order_by(ScanRuleModel.id)).all()
        return [scan_rule_to_record(m) for m in models]

    def list_enabled_ids(self) -> list[str]:
        models = self._session.scalars(
            select(ScanRuleModel).where(ScanRuleModel.enabled.is_(True))
        ).all()
        return [m.id for m in models]
