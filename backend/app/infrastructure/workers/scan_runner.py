"""Background scan execution."""

import logging
import time
from datetime import datetime

from app.config import get_settings
from app.domain.models.enums import ScanStatus
from app.domain.rules.base import RawFile
from app.domain.rules.registry import evaluate_all_rules
from app.domain.services.deduplication import deduplicate_findings
from app.domain.services.redaction import redact_text, truncate_evidence
from app.domain.services.scoring import compute_risk_score
from app.infrastructure.parsers.parser_registry import parse_file
from app.infrastructure.repositories.finding_repository import FindingRepository
from app.infrastructure.repositories.parse_error_repository import ParseErrorRepository
from app.infrastructure.repositories.rule_repository import ScanRuleRepository
from app.infrastructure.repositories.scan_repository import ScanRepository
from app.infrastructure.storage.file_storage import FileStorage

logger = logging.getLogger(__name__)

_cancelled_scans: set[str] = set()


def request_cancel(scan_id: str) -> None:
    _cancelled_scans.add(scan_id)


def is_cancelled(scan_id: str, session=None) -> bool:
    if scan_id in _cancelled_scans:
        return True
    if session is not None:
        scan = ScanRepository(session).get_by_id(scan_id)
        if scan and scan.status == ScanStatus.CANCELLED:
            return True
    return False


def run_scan(scan_id: str, file_records: list[dict]) -> None:
    settings = get_settings()
    from app.infrastructure.database.session import get_session_factory

    session = get_session_factory()()
    start = time.perf_counter()
    try:
        scan_repo = ScanRepository(session)
        finding_repo = FindingRepository(session)
        parse_error_repo = ParseErrorRepository(session)
        rule_repo = ScanRuleRepository(session)
        storage = FileStorage()

        scan = scan_repo.get_by_id(scan_id)
        if not scan:
            return

        if is_cancelled(scan_id, session):
            scan.status = ScanStatus.CANCELLED
            scan.completed_at = datetime.utcnow()
            scan_repo.update(scan)
            session.commit()
            return

        scan.status = ScanStatus.PROCESSING
        scan_repo.update(scan)
        session.commit()

        all_resources = []
        raw_files: list[RawFile] = []
        parse_failures = 0
        parse_successes = 0

        for record in file_records:
            if is_cancelled(scan_id, session):
                break
            if time.perf_counter() - start > settings.scan_timeout_seconds:
                raise TimeoutError("Scan timed out")

            content_bytes = storage.read_file(record["stored_path"])
            content = content_bytes.decode("utf-8").replace("\r\n", "\n")
            raw_files.append(RawFile(filename=record["original_filename"], content=content))
            result = parse_file(content, record["original_filename"])

            if result.errors:
                parse_failures += 1
                parse_error_repo.create(
                    scan_id=scan_id,
                    filename=record["original_filename"],
                    error_code="PARSE_ERROR",
                    message="; ".join(result.errors),
                )
            else:
                parse_successes += 1
                all_resources.extend(result.resources)

        if parse_successes == 0 and parse_failures > 0:
            scan.status = ScanStatus.FAILED
            scan.error_message = "PARSE_ERROR: All files failed to parse"
            scan.completed_at = datetime.utcnow()
            scan.duration_ms = int((time.perf_counter() - start) * 1000)
            scan.parser_version = settings.parser_version
            scan_repo.update(scan)
            session.commit()
            return

        if is_cancelled(scan_id, session):
            scan.status = ScanStatus.CANCELLED
            scan.completed_at = datetime.utcnow()
            scan_repo.update(scan)
            session.commit()
            return

        enabled_rules = rule_repo.list_enabled_ids()
        findings = evaluate_all_rules(scan_id, all_resources, raw_files, enabled_rules)
        findings = deduplicate_findings(findings)

        for finding in findings:
            finding.evidence = truncate_evidence(
                redact_text(finding.evidence), settings.max_evidence_length
            )

        if findings:
            finding_repo.create_many(findings)

        score = compute_risk_score(findings, len(all_resources), settings)
        scan.resource_count = len(all_resources)
        scan.raw_risk_score = score.raw_risk_score
        scan.risk_score = score.risk_score
        scan.normalized_score = score.normalized_score
        scan.critical_count = score.critical_count
        scan.high_count = score.high_count
        scan.medium_count = score.medium_count
        scan.low_count = score.low_count
        scan.info_count = score.info_count
        scan.duration_ms = int((time.perf_counter() - start) * 1000)
        scan.parser_version = settings.parser_version
        scan.completed_at = datetime.utcnow()

        if parse_failures > 0:
            scan.status = ScanStatus.COMPLETED_WITH_ERRORS
        else:
            scan.status = ScanStatus.COMPLETED

        scan_repo.update(scan)
        session.commit()
        logger.info("Scan %s completed with status %s", scan_id, scan.status.value)

    except TimeoutError:
        session.rollback()
        scan_repo = ScanRepository(session)
        scan = scan_repo.get_by_id(scan_id)
        if scan:
            scan.status = ScanStatus.FAILED
            scan.error_message = "SCAN_TIMEOUT"
            scan.completed_at = datetime.utcnow()
            scan.duration_ms = int((time.perf_counter() - start) * 1000)
            scan_repo.update(scan)
            session.commit()
    except Exception as exc:
        session.rollback()
        logger.exception("Scan %s failed: %s", scan_id, exc)
        scan_repo = ScanRepository(session)
        scan = scan_repo.get_by_id(scan_id)
        if scan:
            scan.status = ScanStatus.FAILED
            scan.error_message = "INTERNAL_ERROR"
            scan.completed_at = datetime.utcnow()
            scan_repo.update(scan)
            session.commit()
    finally:
        session.close()
        _cancelled_scans.discard(scan_id)
