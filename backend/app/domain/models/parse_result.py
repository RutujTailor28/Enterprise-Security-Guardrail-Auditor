"""Parse result model."""

from dataclasses import dataclass, field

from app.domain.models.resource import NormalizedResource


@dataclass
class ParseResult:
    resources: list[NormalizedResource] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return not self.errors
