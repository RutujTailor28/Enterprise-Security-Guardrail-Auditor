"""Security rule registry — delegates to RulesEngine."""

from app.domain.engine.rules_engine import RulesEngine
from app.domain.models.resource import NormalizedResource
from app.domain.rules.base import RawFile

_engine = RulesEngine()


def evaluate_all_rules(
    scan_id: str,
    resources: list[NormalizedResource],
    raw_files: list[RawFile],
    enabled_rule_ids: list[str] | None = None,
):
    return _engine.evaluate(scan_id, resources, raw_files, enabled_rule_ids)


def get_rules_engine() -> RulesEngine:
    return _engine
