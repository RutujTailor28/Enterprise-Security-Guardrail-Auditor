"""Risk score result."""

from dataclasses import dataclass


@dataclass
class RiskScoreResult:
    raw_risk_score: int
    risk_score: int
    normalized_score: int
    risk_grade: str | None
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
