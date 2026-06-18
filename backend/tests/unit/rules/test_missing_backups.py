"""Missing backup rule tests."""

from tests.unit.rules.conftest import load_scan_context, rule_ids_from_context

RULE_ID = "MISSING_BACKUP"


def test_detects_missing_backup(rules_engine):
    context = load_scan_context("terraform/missing_backup.tf", enabled_rule_ids=[RULE_ID])
    rule_ids = rule_ids_from_context(rules_engine, context)
    assert RULE_ID in rule_ids
    findings = rules_engine.evaluate(
        context.scan_id, context.resources, context.raw_files, [RULE_ID]
    )
    assert len(findings) >= 2
