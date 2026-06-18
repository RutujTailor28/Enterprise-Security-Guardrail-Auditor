"""Rules engine — orchestrates detection, severity assignment, and finding creation."""

from app.domain.engine.detection_engine import DetectionEngine
from app.domain.engine.models import Detection, ScanContext
from app.domain.engine.severity_engine import SeverityEngine
from app.domain.models.finding import Finding
from app.domain.models.resource import NormalizedResource
from app.domain.rules.base import RawFile, make_finding
from app.domain.services.deduplication import deduplicate_findings


class RulesEngine:
    """
    Top-level scanning engine pipeline:
      ScanContext → DetectionEngine → SeverityEngine → Finding[]
    """

    def __init__(
        self,
        detection_engine: DetectionEngine | None = None,
        severity_engine: SeverityEngine | None = None,
    ):
        self._detection_engine = detection_engine or DetectionEngine()
        self._severity_engine = severity_engine or SeverityEngine()

    def evaluate(
        self,
        scan_id: str,
        resources: list[NormalizedResource],
        raw_files: list[RawFile],
        enabled_rule_ids: list[str] | None = None,
    ) -> list[Finding]:
        context = ScanContext(
            scan_id=scan_id,
            resources=resources,
            raw_files=raw_files,
            enabled_rule_ids=enabled_rule_ids,
        )
        detections = self._detection_engine.run(context)
        findings = self._to_findings(scan_id, detections)
        return deduplicate_findings(findings)

    def detect_only(
        self,
        scan_id: str,
        resources: list[NormalizedResource],
        raw_files: list[RawFile],
        enabled_rule_ids: list[str] | None = None,
    ) -> list[Detection]:
        context = ScanContext(
            scan_id=scan_id,
            resources=resources,
            raw_files=raw_files,
            enabled_rule_ids=enabled_rule_ids,
        )
        return self._detection_engine.run(context)

    def _to_findings(self, scan_id: str, detections: list[Detection]) -> list[Finding]:
        findings: list[Finding] = []
        for detection in detections:
            severity, confidence = self._severity_engine.resolve(detection)
            findings.append(
                make_finding(
                    scan_id=scan_id,
                    rule_id=detection.rule_id,
                    severity=severity,
                    title=detection.title,
                    description=detection.description,
                    remediation=detection.remediation,
                    resource_type=detection.resource_type,
                    resource_name=detection.resource_name,
                    file_name=detection.file_name,
                    line_number=detection.line_number,
                    evidence=detection.evidence,
                    confidence=confidence,
                )
            )
        return findings
