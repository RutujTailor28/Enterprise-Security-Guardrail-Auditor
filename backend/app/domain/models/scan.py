"""Scan domain model."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.models.enums import ScanStatus


@dataclass
class Scan:
    id: str
    status: ScanStatus
    created_at: datetime
    label: str | None = None
    risk_score: int | None = None
    normalized_score: int | None = None
    raw_risk_score: int | None = None
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    resource_count: int = 0
    file_count: int = 0
    duration_ms: int | None = None
    parser_version: str | None = None
    error_message: str | None = None
    updated_at: datetime | None = None
    completed_at: datetime | None = None

    @property
    def severity_counts(self) -> dict[str, int]:
        return {
            "critical": self.critical_count,
            "high": self.high_count,
            "medium": self.medium_count,
            "low": self.low_count,
            "info": self.info_count,
        }

    @property
    def is_terminal(self) -> bool:
        return self.status in {
            ScanStatus.COMPLETED,
            ScanStatus.COMPLETED_WITH_ERRORS,
            ScanStatus.FAILED,
            ScanStatus.CANCELLED,
        }
