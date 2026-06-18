"""Scoring application service."""

from app.config import Settings
from app.domain.models.finding import Finding
from app.domain.models.risk_score import RiskScoreResult
from app.domain.services.scoring import compute_risk_score


class ScoringService:
    def __init__(self, settings: Settings):
        self._settings = settings

    def score(self, findings: list[Finding], resource_count: int) -> RiskScoreResult:
        return compute_risk_score(findings, resource_count, self._settings)
