"""Build prioritized remediation recommendations from scan findings."""

from __future__ import annotations

from app.domain.models.enums import Severity
from app.domain.models.finding import Finding

_SEVERITY_ORDER = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.INFO: 4,
}

_DEFAULT_RECOMMENDATION = {
    "rule_id": "GENERAL",
    "severity": "info",
    "title": "Maintain security posture",
    "remediation": (
        "No security findings were detected in this scan. Continue regular infrastructure "
        "reviews, enforce least-privilege access, and re-scan after material changes."
    ),
}


def build_recommendations(findings: list[Finding]) -> list[dict[str, str]]:
    """Return deduplicated recommendations ordered by severity."""
    if not findings:
        return [_DEFAULT_RECOMMENDATION]

    seen: set[tuple[str, str]] = set()
    recommendations: list[dict[str, str]] = []

    ordered = sorted(
        findings,
        key=lambda finding: (_SEVERITY_ORDER[finding.severity], finding.rule_id, finding.title),
    )

    for finding in ordered:
        remediation = (finding.remediation or "").strip()
        if not remediation:
            continue
        key = (finding.rule_id, remediation)
        if key in seen:
            continue
        seen.add(key)
        recommendations.append(
            {
                "rule_id": finding.rule_id,
                "severity": finding.severity.value,
                "title": finding.title,
                "remediation": remediation,
            }
        )

    return recommendations or [_DEFAULT_RECOMMENDATION]
