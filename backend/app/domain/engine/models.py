"""Scanning engine domain models."""

from dataclasses import dataclass, field

from app.domain.models.enums import Confidence
from app.domain.models.resource import NormalizedResource
from app.domain.rules.base import RawFile


@dataclass
class Detection:
    """Raw security detection before severity assignment and persistence."""

    rule_id: str
    title: str
    description: str
    remediation: str
    resource_type: str | None = None
    resource_name: str | None = None
    file_name: str | None = None
    line_number: int | None = None
    evidence: str | None = None
    confidence: Confidence = Confidence.HIGH


@dataclass
class ScanContext:
    """Input context for the detection engine."""

    scan_id: str
    resources: list[NormalizedResource] = field(default_factory=list)
    raw_files: list[RawFile] = field(default_factory=list)
    enabled_rule_ids: list[str] | None = None

    def resources_of_type(self, *types: str) -> list[NormalizedResource]:
        return [r for r in self.resources if r.resource_type in types]

    def has_resource_type(self, resource_type: str) -> bool:
        return any(r.resource_type == resource_type for r in self.resources)
