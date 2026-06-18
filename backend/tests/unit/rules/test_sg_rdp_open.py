"""Open RDP rule tests."""

from tests.unit.rules.conftest import load_scan_context, rule_ids_from_context

RULE_ID = "SG_RDP_OPEN"


def test_detects_open_rdp(rules_engine):
    context = load_scan_context("terraform/open_rdp.tf", enabled_rule_ids=[RULE_ID])
    rule_ids = rule_ids_from_context(rules_engine, context)
    assert RULE_ID in rule_ids


def test_clean_no_open_rdp(rules_engine):
    context = load_scan_context("terraform/clean.tf", enabled_rule_ids=[RULE_ID])
    rule_ids = rule_ids_from_context(rules_engine, context)
    assert RULE_ID not in rule_ids
