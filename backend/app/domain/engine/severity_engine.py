"""Rule severity and confidence assignment."""

from dataclasses import dataclass

from app.domain.engine.models import Detection
from app.domain.models.enums import Confidence, Severity


@dataclass(frozen=True)
class RuleSeverityProfile:
    rule_id: str
    severity: Severity
    default_confidence: Confidence = Confidence.HIGH


RULE_SEVERITY_PROFILES: dict[str, RuleSeverityProfile] = {
    "S3_PUBLIC": RuleSeverityProfile("S3_PUBLIC", Severity.CRITICAL),
    "SG_SSH_OPEN": RuleSeverityProfile("SG_SSH_OPEN", Severity.HIGH),
    "SG_RDP_OPEN": RuleSeverityProfile("SG_RDP_OPEN", Severity.HIGH),
    "IAM_WILDCARD": RuleSeverityProfile("IAM_WILDCARD", Severity.CRITICAL),
    "MISSING_ENCRYPTION": RuleSeverityProfile("MISSING_ENCRYPTION", Severity.HIGH),
    "DB_PUBLIC": RuleSeverityProfile("DB_PUBLIC", Severity.CRITICAL),
    "MISSING_LOGGING": RuleSeverityProfile("MISSING_LOGGING", Severity.MEDIUM),
    "MISSING_BACKUP": RuleSeverityProfile("MISSING_BACKUP", Severity.MEDIUM),
    "HARDCODED_SECRET": RuleSeverityProfile("HARDCODED_SECRET", Severity.CRITICAL),
    "SG_OVERLY_PERMISSIVE": RuleSeverityProfile("SG_OVERLY_PERMISSIVE", Severity.HIGH),
}


class SeverityEngine:
    """Maps detections to severity levels and resolves confidence scores."""

    def __init__(self, profiles: dict[str, RuleSeverityProfile] | None = None):
        self._profiles = profiles or RULE_SEVERITY_PROFILES

    def resolve(self, detection: Detection) -> tuple[Severity, Confidence]:
        profile = self._profiles.get(detection.rule_id)
        if not profile:
            return Severity.MEDIUM, detection.confidence
        confidence = detection.confidence or profile.default_confidence
        return profile.severity, confidence

    def severity_for_rule(self, rule_id: str) -> Severity:
        profile = self._profiles.get(rule_id)
        return profile.severity if profile else Severity.MEDIUM

    def list_profiles(self) -> list[RuleSeverityProfile]:
        return list(self._profiles.values())
