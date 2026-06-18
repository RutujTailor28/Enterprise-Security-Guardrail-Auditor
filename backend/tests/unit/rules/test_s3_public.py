"""S3 public bucket rule tests."""

from app.domain.models.enums import Severity
from tests.unit.rules.conftest import load_scan_context, rule_ids_from_context

RULE_ID = "S3_PUBLIC"


def test_detects_public_s3(rules_engine):
    context = load_scan_context("terraform/public_s3.tf", enabled_rule_ids=[RULE_ID])
    findings = rules_engine.evaluate(context.scan_id, context.resources, context.raw_files, [RULE_ID])
    assert len(findings) >= 1
    assert findings[0].rule_id == RULE_ID
    assert findings[0].severity == Severity.CRITICAL


def test_clean_s3_not_flagged(rules_engine):
    context = load_scan_context("terraform/clean.tf", enabled_rule_ids=[RULE_ID])
    rule_ids = rule_ids_from_context(rules_engine, context)
    assert RULE_ID not in rule_ids
