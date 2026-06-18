"""Finding repository."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.models.finding import Finding
from app.infrastructure.database.models import FindingModel
from app.infrastructure.repositories.mappers import finding_to_domain, finding_to_model


class FindingRepository:
    def __init__(self, session: Session):
        self._session = session

    def create_many(self, findings: list[Finding]) -> list[Finding]:
        models = [finding_to_model(f) for f in findings]
        self._session.add_all(models)
        self._session.flush()
        return findings

    def list_by_scan(
        self,
        scan_id: str,
        page: int = 1,
        page_size: int = 20,
        severity: str | None = None,
        rule_id: str | None = None,
        query_text: str | None = None,
    ) -> tuple[list[Finding], int]:
        stmt = select(FindingModel).where(FindingModel.scan_id == scan_id)
        if severity:
            stmt = stmt.where(FindingModel.severity == severity)
        if rule_id:
            stmt = stmt.where(FindingModel.rule_id == rule_id)
        if query_text:
            escaped = query_text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            pattern = f"%{escaped}%"
            stmt = stmt.where(
                FindingModel.resource_name.ilike(pattern, escape="\\")
                | FindingModel.title.ilike(pattern, escape="\\")
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self._session.scalar(count_stmt) or 0
        offset = (page - 1) * page_size
        models = self._session.scalars(
            stmt.order_by(FindingModel.severity, FindingModel.created_at).offset(offset).limit(page_size)
        ).all()
        return [finding_to_domain(m) for m in models], total

    def count_by_scan(self, scan_id: str) -> int:
        return (
            self._session.scalar(
                select(func.count()).where(FindingModel.scan_id == scan_id)
            )
            or 0
        )
