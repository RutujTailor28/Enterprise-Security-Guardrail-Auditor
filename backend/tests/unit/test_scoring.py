"""Risk scoring unit tests."""

from datetime import datetime

from app.config import get_settings
from app.domain.models.enums import Confidence, Severity
from app.domain.models.finding import Finding
from app.domain.services.scoring import (
    GRADE_CRITICAL,
    GRADE_EXCELLENT,
    GRADE_GOOD,
    GRADE_WARNING,
    compute_grade,
    compute_risk_score,
    compute_security_score,
    penalty_for_severity,
)


def _finding(severity: Severity) -> Finding:
    return Finding(
        id="1",
        scan_id="s",
        rule_id="TEST",
        fingerprint="fp",
        severity=severity,
        confidence=Confidence.HIGH,
        title="t",
        description="d",
        remediation="r",
        created_at=datetime.utcnow(),
    )


def test_penalty_points_match_spec():
    settings = get_settings()
    assert penalty_for_severity(Severity.CRITICAL, settings) == 10
    assert penalty_for_severity(Severity.HIGH, settings) == 7
    assert penalty_for_severity(Severity.MEDIUM, settings) == 4
    assert penalty_for_severity(Severity.LOW, settings) == 1
    assert penalty_for_severity(Severity.INFO, settings) == 0


def test_compute_grade_bands():
    assert compute_grade(100) == GRADE_EXCELLENT
    assert compute_grade(90) == GRADE_EXCELLENT
    assert compute_grade(89) == GRADE_GOOD
    assert compute_grade(70) == GRADE_GOOD
    assert compute_grade(69) == GRADE_WARNING
    assert compute_grade(50) == GRADE_WARNING
    assert compute_grade(49) == GRADE_CRITICAL
    assert compute_grade(0) == GRADE_CRITICAL
    assert compute_grade(None) is None


def test_compute_security_score():
    assert compute_security_score(0) == 100
    assert compute_security_score(10) == 90
    assert compute_security_score(100) == 0
    assert compute_security_score(150) == 0


def test_scoring_single_critical():
    settings = get_settings()
    result = compute_risk_score([_finding(Severity.CRITICAL)], 1, settings)
    assert result.raw_risk_score == 10
    assert result.risk_score == 90
    assert result.risk_grade == GRADE_EXCELLENT


def test_scoring_mixed_findings():
    settings = get_settings()
    findings = [
        _finding(Severity.CRITICAL),
        _finding(Severity.HIGH),
        _finding(Severity.MEDIUM),
        _finding(Severity.LOW),
    ]
    result = compute_risk_score(findings, 4, settings)
    assert result.raw_risk_score == 22
    assert result.risk_score == 78
    assert result.risk_grade == GRADE_GOOD


def test_scoring_caps_penalty_at_100():
    settings = get_settings()
    findings = [_finding(Severity.CRITICAL) for _ in range(15)]
    result = compute_risk_score(findings, 10, settings)
    assert result.raw_risk_score == 150
    assert result.risk_score == 0
    assert result.risk_grade == GRADE_CRITICAL


def test_scoring_empty():
    settings = get_settings()
    result = compute_risk_score([], 0, settings)
    assert result.raw_risk_score == 0
    assert result.risk_score == 100
    assert result.risk_grade == GRADE_EXCELLENT


def test_scoring_warning_threshold():
    settings = get_settings()
    findings = [_finding(Severity.CRITICAL) for _ in range(5)]
    result = compute_risk_score(findings, 10, settings)
    assert result.raw_risk_score == 50
    assert result.risk_score == 50
    assert result.risk_grade == GRADE_WARNING
