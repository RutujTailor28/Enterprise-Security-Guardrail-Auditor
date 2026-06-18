"""ORM to domain mappers."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.models.enums import Confidence, FileType, ScanStatus, Severity
from app.domain.models.finding import Finding
from app.domain.models.parse_error import ParseErrorRecord
from app.domain.models.scan import Scan
from app.infrastructure.database.models import (
    FindingModel,
    ParseErrorModel,
    ScanModel,
    ScanRuleModel,
    UploadedFileModel,
)


@dataclass
class UploadedFileRecord:
    id: str
    scan_id: str
    original_filename: str
    stored_filename: str
    file_type: FileType
    content_hash: str
    size_bytes: int
    stored_path: str
    created_at: datetime


@dataclass
class ScanRuleRecord:
    id: str
    name: str
    severity_default: str
    description: str
    enabled: bool


def scan_to_domain(model: ScanModel) -> Scan:
    return Scan(
        id=model.id,
        label=model.label,
        status=ScanStatus(model.status),
        risk_score=model.risk_score,
        normalized_score=model.normalized_score,
        raw_risk_score=model.raw_risk_score,
        critical_count=model.critical_count,
        high_count=model.high_count,
        medium_count=model.medium_count,
        low_count=model.low_count,
        info_count=model.info_count,
        resource_count=model.resource_count,
        file_count=model.file_count,
        duration_ms=model.duration_ms,
        parser_version=model.parser_version,
        error_message=model.error_message,
        created_at=model.created_at,
        updated_at=model.updated_at,
        completed_at=model.completed_at,
    )


def scan_to_model(domain: Scan) -> ScanModel:
    return ScanModel(
        id=domain.id,
        label=domain.label,
        status=domain.status.value,
        risk_score=domain.risk_score,
        normalized_score=domain.normalized_score,
        raw_risk_score=domain.raw_risk_score,
        critical_count=domain.critical_count,
        high_count=domain.high_count,
        medium_count=domain.medium_count,
        low_count=domain.low_count,
        info_count=domain.info_count,
        resource_count=domain.resource_count,
        file_count=domain.file_count,
        duration_ms=domain.duration_ms,
        parser_version=domain.parser_version,
        error_message=domain.error_message,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
        completed_at=domain.completed_at,
    )


def finding_to_domain(model: FindingModel) -> Finding:
    return Finding(
        id=model.id,
        scan_id=model.scan_id,
        rule_id=model.rule_id,
        fingerprint=model.fingerprint,
        severity=Severity(model.severity),
        confidence=Confidence(model.confidence),
        title=model.title,
        description=model.description,
        remediation=model.remediation,
        resource_type=model.resource_type,
        resource_name=model.resource_name,
        file_name=model.file_name,
        line_number=model.line_number,
        evidence=model.evidence,
        created_at=model.created_at,
    )


def finding_to_model(domain: Finding) -> FindingModel:
    return FindingModel(
        id=domain.id,
        scan_id=domain.scan_id,
        rule_id=domain.rule_id,
        fingerprint=domain.fingerprint,
        severity=domain.severity.value,
        confidence=domain.confidence.value,
        title=domain.title,
        description=domain.description,
        remediation=domain.remediation,
        resource_type=domain.resource_type,
        resource_name=domain.resource_name,
        file_name=domain.file_name,
        line_number=domain.line_number,
        evidence=domain.evidence,
        created_at=domain.created_at,
    )


def parse_error_to_domain(model: ParseErrorModel) -> ParseErrorRecord:
    return ParseErrorRecord(
        id=model.id,
        scan_id=model.scan_id,
        filename=model.filename,
        error_code=model.error_code,
        message=model.message,
        line_number=model.line_number,
        created_at=model.created_at,
    )


def uploaded_file_to_record(model: UploadedFileModel) -> UploadedFileRecord:
    return UploadedFileRecord(
        id=model.id,
        scan_id=model.scan_id,
        original_filename=model.original_filename,
        stored_filename=model.stored_filename,
        file_type=FileType(model.file_type),
        content_hash=model.content_hash,
        size_bytes=model.size_bytes,
        stored_path=model.stored_path,
        created_at=model.created_at,
    )


def scan_rule_to_record(model: ScanRuleModel) -> ScanRuleRecord:
    return ScanRuleRecord(
        id=model.id,
        name=model.name,
        severity_default=model.severity_default,
        description=model.description,
        enabled=model.enabled,
    )
