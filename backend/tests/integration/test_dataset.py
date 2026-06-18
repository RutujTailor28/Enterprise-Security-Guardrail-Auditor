"""Validate the canonical IaC test dataset against the rules engine."""

import json
from pathlib import Path

import pytest

from app.domain.engine.rules_engine import RulesEngine
from app.domain.rules.base import RawFile
from app.infrastructure.parsers.parser_registry import parse_file

DATASET_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "dataset"
MANIFEST_PATH = DATASET_DIR / "manifest.json"


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rules_engine() -> RulesEngine:
    return RulesEngine()


def _rule_ids_for_fixture(relative_path: str, rules_engine: RulesEngine) -> set[str]:
    path = DATASET_DIR / relative_path
    content = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    result = parse_file(content, path.name)
    assert not result.errors, f"Parse errors in {relative_path}: {result.errors}"
    findings = rules_engine.evaluate(
        scan_id="dataset-scan",
        resources=result.resources,
        raw_files=[RawFile(filename=path.name, content=content)],
    )
    return {finding.rule_id for finding in findings}


def test_manifest_structure(manifest):
    assert manifest["version"]
    assert len(manifest["entries"]) >= 20
    ids = [entry["id"] for entry in manifest["entries"]]
    assert len(ids) == len(set(ids))
    for entry in manifest["entries"]:
        assert (DATASET_DIR / entry["path"]).is_file()
        assert entry["classification"] in ("secure", "insecure")


@pytest.mark.parametrize(
    "entry",
    json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["entries"],
    ids=[entry["id"] for entry in json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["entries"]],
)
def test_dataset_entry_rules(entry, rules_engine):
    found = _rule_ids_for_fixture(entry["path"], rules_engine)

    for rule_id in entry.get("expected_rules", []):
        assert rule_id in found, (
            f"{entry['id']}: expected rule {rule_id} not found; got {sorted(found)}"
        )

    for rule_id in entry.get("forbidden_rules", []):
        assert rule_id not in found, (
            f"{entry['id']}: rule {rule_id} should not trigger; got {sorted(found)}"
        )

    if entry["classification"] == "secure":
        assert not found, f"{entry['id']}: secure fixture triggered {sorted(found)}"
