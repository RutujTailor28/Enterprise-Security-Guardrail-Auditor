"""Security rule protocol and helpers."""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.domain.models.enums import Confidence, Severity
from app.domain.models.finding import Finding
from app.domain.models.resource import NormalizedResource
from app.domain.services.fingerprint import generate_fingerprint


@dataclass
class RawFile:
    filename: str
    content: str


class SecurityRule(Protocol):
    rule_id: str

    def evaluate(
        self,
        scan_id: str,
        resources: list[NormalizedResource],
        raw_files: list[RawFile],
    ) -> list[Finding]: ...


def make_finding(
    scan_id: str,
    rule_id: str,
    severity: Severity,
    title: str,
    description: str,
    remediation: str,
    resource_type: str | None = None,
    resource_name: str | None = None,
    file_name: str | None = None,
    line_number: int | None = None,
    evidence: str | None = None,
    confidence: Confidence = Confidence.HIGH,
) -> Finding:
    fingerprint = generate_fingerprint(rule_id, resource_type, resource_name, file_name, line_number)
    return Finding(
        id=str(uuid.uuid4()),
        scan_id=scan_id,
        rule_id=rule_id,
        fingerprint=fingerprint,
        severity=severity,
        confidence=confidence,
        title=title,
        description=description,
        remediation=remediation,
        resource_type=resource_type,
        resource_name=resource_name,
        file_name=file_name,
        line_number=line_number,
        evidence=evidence,
        created_at=datetime.utcnow(),
    )


def is_open_cidr(cidr) -> bool:
    if cidr is None:
        return False
    if isinstance(cidr, list):
        return any(is_open_cidr(c) for c in cidr)
    return str(cidr) in ("0.0.0.0/0", "::/0")


def port_matches(rule: dict, target_port: int) -> bool:
    from_port = (
        rule.get("from_port")
        if rule.get("from_port") is not None
        else rule.get("FromPort")
    )
    to_port = (
        rule.get("to_port") if rule.get("to_port") is not None else rule.get("ToPort")
    )
    if from_port is None and to_port is None:
        return False
    try:
        fp = int(from_port) if from_port is not None else int(to_port)
        tp = int(to_port) if to_port is not None else int(from_port)
    except (TypeError, ValueError):
        return False
    return fp <= target_port <= tp
