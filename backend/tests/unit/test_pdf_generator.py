"""Unit tests for report recommendations and PDF generation."""

from datetime import datetime

from app.domain.models.enums import Confidence, ScanStatus, Severity
from app.domain.models.finding import Finding
from app.domain.models.scan import Scan
from app.infrastructure.reports.pdf_generator import generate_scan_pdf
from app.infrastructure.reports.recommendations import build_recommendations


def _finding(
    rule_id: str = "S3_PUBLIC",
    severity: Severity = Severity.CRITICAL,
    remediation: str = "Restrict bucket ACL and enable block public access.",
) -> Finding:
    return Finding(
        id="f1",
        scan_id="scan-1",
        rule_id=rule_id,
        fingerprint="fp",
        severity=severity,
        confidence=Confidence.HIGH,
        title="Public S3 bucket detected",
        description="Bucket allows public read access.",
        remediation=remediation,
        resource_type="aws_s3_bucket",
        resource_name="logs",
        file_name="main.tf",
        line_number=12,
        created_at=datetime.utcnow(),
    )


def _scan() -> Scan:
    return Scan(
        id="scan-12345678",
        label="Production audit",
        status=ScanStatus.COMPLETED,
        created_at=datetime(2026, 6, 17, 10, 0, 0),
        completed_at=datetime(2026, 6, 17, 10, 0, 5),
        risk_score=90,
        raw_risk_score=10,
        normalized_score=88,
        critical_count=1,
        high_count=0,
        medium_count=0,
        low_count=0,
        info_count=0,
        resource_count=4,
        file_count=1,
        duration_ms=2500,
        parser_version="1.0.0",
    )


def test_build_recommendations_deduplicates_by_rule_and_text():
    findings = [
        _finding(),
        _finding(remediation="Restrict bucket ACL and enable block public access."),
        _finding(rule_id="SG_SSH_OPEN", severity=Severity.HIGH, remediation="Close port 22 to 0.0.0.0/0."),
    ]
    recommendations = build_recommendations(findings)
    assert len(recommendations) == 2
    assert recommendations[0]["rule_id"] == "S3_PUBLIC"
    assert recommendations[1]["rule_id"] == "SG_SSH_OPEN"


def test_build_recommendations_default_when_no_findings():
    recommendations = build_recommendations([])
    assert len(recommendations) == 1
    assert recommendations[0]["rule_id"] == "GENERAL"


def test_generate_scan_pdf_returns_valid_document():
    pdf_bytes = generate_scan_pdf(
        _scan(),
        [_finding()],
        generated_at=datetime(2026, 6, 17, 12, 0, 0),
    )
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1500


def test_generate_scan_pdf_produces_substantial_output():
    pdf_bytes = generate_scan_pdf(_scan(), [_finding()], generated_at=datetime(2026, 6, 17, 12, 0, 0))
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 2000
