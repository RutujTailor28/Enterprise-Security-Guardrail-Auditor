"""Overly permissive security group rule tests."""

from tests.unit.rules.conftest import load_scan_context, rule_ids_from_context

RULE_ID = "SG_OVERLY_PERMISSIVE"


def test_detects_overly_permissive_sg(rules_engine):
    context = load_scan_context("terraform/overly_permissive_sg.tf", enabled_rule_ids=[RULE_ID])
    rule_ids = rule_ids_from_context(rules_engine, context)
    assert RULE_ID in rule_ids


def test_ssh_only_not_overly_permissive(rules_engine):
    context = load_scan_context("terraform/open_ssh.tf", enabled_rule_ids=[RULE_ID])
    rule_ids = rule_ids_from_context(rules_engine, context)
    assert RULE_ID not in rule_ids
