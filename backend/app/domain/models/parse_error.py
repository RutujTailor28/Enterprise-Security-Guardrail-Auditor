"""Parse error domain model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ParseErrorRecord:
    id: str
    scan_id: str
    filename: str
    error_code: str
    message: str
    created_at: datetime
    line_number: int | None = None
