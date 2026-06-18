"""Detection engine — runs all security detectors against scan context."""

import logging

from app.domain.engine.detectors import ALL_DETECTORS
from app.domain.engine.models import Detection, ScanContext

logger = logging.getLogger(__name__)


class DetectionEngine:
    """Executes registered detectors and collects raw detections."""

    def __init__(self, detectors: list | None = None):
        self._detectors = detectors or ALL_DETECTORS

    def run(self, context: ScanContext) -> list[Detection]:
        enabled = set(context.enabled_rule_ids) if context.enabled_rule_ids else None
        detections: list[Detection] = []

        for rule_id, detector_fn in self._detectors:
            if enabled is not None and rule_id not in enabled:
                continue
            try:
                results = detector_fn(context)
                detections.extend(results)
                if results:
                    logger.debug("Detector %s found %d issue(s)", rule_id, len(results))
            except Exception as exc:
                logger.exception("Detector %s failed: %s", rule_id, exc)

        return detections

    def run_single(self, rule_id: str, context: ScanContext) -> list[Detection]:
        for registered_id, detector_fn in self._detectors:
            if registered_id == rule_id:
                return detector_fn(context)
        return []
