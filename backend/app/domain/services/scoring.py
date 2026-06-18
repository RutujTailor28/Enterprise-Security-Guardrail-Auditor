"""Risk scoring constants, grade bands, and calculation."""

from __future__ import annotations

import math
from typing import Final

from app.config import Settings
from app.domain.models.enums import Severity
from app.domain.models.finding import Finding
from app.domain.models.risk_score import RiskScoreResult

MAX_SECURITY_SCORE: Final[int] = 100

SEVERITY_PENALTY_POINTS: Final[dict[Severity, int]] = {
    Severity.CRITICAL: 10,
    Severity.HIGH: 7,
    Severity.MEDIUM: 4,
    Severity.LOW: 1,
    Severity.INFO: 0,
}

GRADE_EXCELLENT: Final[str] = "Excellent"
GRADE_GOOD: Final[str] = "Good"
GRADE_WARNING: Final[str] = "Warning"
GRADE_CRITICAL: Final[str] = "Critical"


def penalty_for_severity(severity: Severity, settings: Settings | None = None) -> int:
    """Return penalty points for a finding severity."""
    if settings is not None:
        mapping = {
            Severity.CRITICAL: settings.severity_weight_critical,
            Severity.HIGH: settings.severity_weight_high,
            Severity.MEDIUM: settings.severity_weight_medium,
            Severity.LOW: settings.severity_weight_low,
            Severity.INFO: settings.severity_weight_info,
        }
        return mapping[severity]
    return SEVERITY_PENALTY_POINTS[severity]


def compute_grade(security_score: int | None) -> str | None:
    """Map a 0-100 security posture score to an overall grade."""
    if security_score is None:
        return None
    if security_score >= 90:
        return GRADE_EXCELLENT
    if security_score >= 70:
        return GRADE_GOOD
    if security_score >= 50:
        return GRADE_WARNING
    return GRADE_CRITICAL


def compute_security_score(penalty_points: int) -> int:
    """Convert accumulated penalty points into a 0-100 security posture score."""
    capped_penalty = min(MAX_SECURITY_SCORE, max(0, penalty_points))
    return MAX_SECURITY_SCORE - capped_penalty


def compute_risk_score(
    findings: list[Finding], resource_count: int, settings: Settings
) -> RiskScoreResult:
    """Compute penalty totals, security scores, severity counts, and overall grade."""
    counts = {severity: 0 for severity in Severity}
    raw_penalty = 0

    for finding in findings:
        counts[finding.severity] += 1
        raw_penalty += penalty_for_severity(finding.severity, settings)

    risk_score = compute_security_score(raw_penalty)

    normalized_penalty = 0
    if resource_count > 0:
        normalized_penalty = min(
            MAX_SECURITY_SCORE,
            round(raw_penalty / math.sqrt(resource_count) * 2),
        )
    normalized_score = compute_security_score(normalized_penalty)

    return RiskScoreResult(
        raw_risk_score=raw_penalty,
        risk_score=risk_score,
        normalized_score=normalized_score,
        risk_grade=compute_grade(risk_score),
        critical_count=counts[Severity.CRITICAL],
        high_count=counts[Severity.HIGH],
        medium_count=counts[Severity.MEDIUM],
        low_count=counts[Severity.LOW],
        info_count=counts[Severity.INFO],
    )
