"""Public database rule tests."""

from app.domain.models.enums import Severity
from tests.unit.rules.conftest import load_scan_context, rule_ids_from_context

RULE_ID = "DB_PUBLIC"


def test_detects_public_rds_cfn(rules_engine):
    context = load_scan_context("cloudformation/public_rds.json", enabled_rule_ids=[RULE_ID])
    findings = rules_engine.evaluate(context.scan_id, context.resources, context.raw_files, [RULE_ID])
    assert any(f.rule_id == RULE_ID for f in findings)
    assert findings[0].severity == Severity.CRITICAL


def test_clean_db_not_public(rules_engine):
    context = load_scan_context("terraform/clean.tf", enabled_rule_ids=[RULE_ID])
    rule_ids = rule_ids_from_context(rules_engine, context)
    assert RULE_ID not in rule_ids
