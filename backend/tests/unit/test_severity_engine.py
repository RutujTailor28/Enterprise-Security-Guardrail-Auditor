"""Severity engine unit tests."""

from app.domain.engine.models import Detection
from app.domain.engine.severity_engine import SeverityEngine
from app.domain.models.enums import Confidence, Severity


def test_resolves_critical_for_s3():
    engine = SeverityEngine()
    detection = Detection(
        rule_id="S3_PUBLIC",
        title="t",
        description="d",
        remediation="r",
    )
    severity, confidence = engine.resolve(detection)
    assert severity == Severity.CRITICAL
    assert confidence == Confidence.HIGH


def test_resolves_medium_for_logging():
    engine = SeverityEngine()
    detection = Detection(
        rule_id="MISSING_LOGGING",
        title="t",
        description="d",
        remediation="r",
        confidence=Confidence.MEDIUM,
    )
    severity, confidence = engine.resolve(detection)
    assert severity == Severity.MEDIUM
    assert confidence == Confidence.MEDIUM


def test_unknown_rule_defaults_medium():
    engine = SeverityEngine()
    detection = Detection(rule_id="UNKNOWN", title="t", description="d", remediation="r")
    severity, _ = engine.resolve(detection)
    assert severity == Severity.MEDIUM
