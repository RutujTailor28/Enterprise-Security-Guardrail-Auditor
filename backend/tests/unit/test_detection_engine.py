"""Detection engine unit tests."""

from app.domain.engine.detection_engine import DetectionEngine
from app.domain.engine.detectors.s3_public import RULE_ID as S3_RULE
from tests.unit.rules.conftest import load_scan_context


def test_runs_single_enabled_detector():
    engine = DetectionEngine()
    context = load_scan_context("terraform/public_s3.tf", enabled_rule_ids=[S3_RULE])
    detections = engine.run(context)
    assert all(d.rule_id == S3_RULE for d in detections)
    assert len(detections) >= 1


def test_skips_disabled_detectors():
    engine = DetectionEngine()
    context = load_scan_context("terraform/public_s3.tf", enabled_rule_ids=["SG_SSH_OPEN"])
    detections = engine.run(context)
    assert detections == []


def test_run_single_detector():
    engine = DetectionEngine()
    context = load_scan_context("terraform/open_ssh.tf")
    detections = engine.run_single("SG_SSH_OPEN", context)
    assert len(detections) >= 1
