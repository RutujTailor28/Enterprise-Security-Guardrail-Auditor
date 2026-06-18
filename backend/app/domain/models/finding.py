"""Finding domain model."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.models.enums import Confidence, Severity


@dataclass
class Finding:
    id: str
    scan_id: str
    rule_id: str
    fingerprint: str
    severity: Severity
    confidence: Confidence
    title: str
    description: str
    remediation: str
    created_at: datetime
    resource_type: str | None = None
    resource_name: str | None = None
    file_name: str | None = None
    line_number: int | None = None
    evidence: str | None = None
