"""Missing logging rule tests."""

from tests.unit.rules.conftest import load_scan_context, rule_ids_from_context

RULE_ID = "MISSING_LOGGING"


def test_detects_missing_s3_logging(rules_engine):
    context = load_scan_context("terraform/missing_logging.tf", enabled_rule_ids=[RULE_ID])
    rule_ids = rule_ids_from_context(rules_engine, context)
    assert RULE_ID in rule_ids


def test_clean_has_logging(rules_engine):
    context = load_scan_context("terraform/clean.tf", enabled_rule_ids=[RULE_ID])
    rule_ids = rule_ids_from_context(rules_engine, context)
    assert RULE_ID not in rule_ids
