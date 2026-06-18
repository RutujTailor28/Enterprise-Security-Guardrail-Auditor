"""Normalized IaC resource model."""

from dataclasses import dataclass, field

from app.domain.models.enums import Resolution


@dataclass
class NormalizedResource:
    id: str
    source_file: str
    provider: str
    resource_type: str
    resource_name: str
    properties: dict
    resolution: Resolution = Resolution.RESOLVED
    source_line: int | None = None
    related_resources: list[str] = field(default_factory=list)
    raw_block: str = ""
