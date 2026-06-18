"""Dashboard analytics service."""

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.models.enums import ScanStatus
from app.domain.services.scoring import compute_grade
from app.infrastructure.database.models import FindingModel, ScanModel


class DashboardService:
    def __init__(self, session: Session):
        self._session = session

    def get_summary(self) -> dict:
        total_scans = self._session.scalar(select(func.count()).select_from(ScanModel)) or 0

        latest = self._session.scalar(
            select(ScanModel)
            .where(ScanModel.status.in_([ScanStatus.COMPLETED.value, ScanStatus.COMPLETED_WITH_ERRORS.value]))
            .order_by(ScanModel.completed_at.desc())
            .limit(1)
        )

        severity_rows = self._session.execute(
            select(FindingModel.severity, func.count())
            .group_by(FindingModel.severity)
        ).all()
        findings_by_severity = {row[0]: row[1] for row in severity_rows}

        rule_rows = self._session.execute(
            select(FindingModel.rule_id, func.count())
            .group_by(FindingModel.rule_id)
            .order_by(func.count().desc())
            .limit(10)
        ).all()
        findings_by_rule = [{"rule_id": r[0], "count": r[1]} for r in rule_rows]

        return {
            "total_scans": total_scans,
            "latest_risk_score": latest.risk_score if latest else None,
            "latest_risk_grade": compute_grade(latest.risk_score) if latest else None,
            "open_critical_findings": latest.critical_count if latest else 0,
            "findings_by_severity": {
                "critical": findings_by_severity.get("critical", 0),
                "high": findings_by_severity.get("high", 0),
                "medium": findings_by_severity.get("medium", 0),
                "low": findings_by_severity.get("low", 0),
                "info": findings_by_severity.get("info", 0),
            },
            "findings_by_rule": findings_by_rule,
            "last_scan_at": latest.completed_at.isoformat() + "Z" if latest and latest.completed_at else None,
        }

    def get_trends(self, days: int = 30) -> dict:
        since = datetime.utcnow() - timedelta(days=days)
        scans = self._session.scalars(
            select(ScanModel)
            .where(ScanModel.completed_at.is_not(None))
            .where(ScanModel.completed_at >= since)
            .order_by(ScanModel.completed_at.asc())
        ).all()

        risk_scores = []
        findings_over_time = []
        for scan in scans:
            if not scan.completed_at:
                continue
            date_key = scan.completed_at.strftime("%Y-%m-%d")
            risk_scores.append({"date": date_key, "score": scan.risk_score or 0})
            findings_over_time.append(
                {
                    "date": date_key,
                    "critical": scan.critical_count,
                    "high": scan.high_count,
                    "medium": scan.medium_count,
                }
            )

        return {"risk_scores": risk_scores, "findings_over_time": findings_over_time}
