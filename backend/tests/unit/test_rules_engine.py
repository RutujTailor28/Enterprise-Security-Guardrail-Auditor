"""Rules engine integration unit tests."""

from app.domain.engine.rules_engine import RulesEngine
from tests.unit.rules.conftest import load_scan_context


def test_full_pipeline_deduplicates():
    engine = RulesEngine()
    context = load_scan_context("terraform/public_s3.tf")
    findings = engine.evaluate(context.scan_id, context.resources, context.raw_files)
    fingerprints = [f.fingerprint for f in findings]
    assert len(fingerprints) == len(set(fingerprints))


def test_detect_only_returns_no_findings():
    engine = RulesEngine()
    context = load_scan_context("terraform/public_s3.tf")
    detections = engine.detect_only(context.scan_id, context.resources, context.raw_files)
    assert detections
    assert detections[0].rule_id == "S3_PUBLIC"
