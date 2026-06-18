"""Parser protocol."""

from typing import Protocol

from app.domain.models.parse_result import ParseResult


class IaCParser(Protocol):
    def can_parse(self, filename: str) -> bool: ...

    def parse(self, content: str, filename: str) -> ParseResult: ...
