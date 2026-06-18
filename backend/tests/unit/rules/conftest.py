"""Shared fixtures for rules engine unit tests."""

from pathlib import Path

import pytest

from app.domain.engine.models import ScanContext
from app.domain.engine.rules_engine import RulesEngine
from app.domain.rules.base import RawFile
from app.infrastructure.parsers.parser_registry import parse_file

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"


@pytest.fixture
def rules_engine():
    return RulesEngine()


def load_scan_context(
    fixture_path: str,
    scan_id: str = "test-scan",
    enabled_rule_ids: list[str] | None = None,
) -> ScanContext:
    path = FIXTURES_DIR / fixture_path
    content = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    result = parse_file(content, path.name)
    return ScanContext(
        scan_id=scan_id,
        resources=result.resources,
        raw_files=[RawFile(filename=path.name, content=content)],
        enabled_rule_ids=enabled_rule_ids,
    )


def rule_ids_from_context(engine: RulesEngine, context: ScanContext) -> set[str]:
    findings = engine.evaluate(
        context.scan_id,
        context.resources,
        context.raw_files,
        context.enabled_rule_ids,
    )
    return {f.rule_id for f in findings}
