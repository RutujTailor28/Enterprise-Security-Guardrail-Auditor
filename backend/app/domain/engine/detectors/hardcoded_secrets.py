"""Hardcoded secrets detector."""

import re

from app.domain.engine.detection_helpers import line_number_for_match
from app.domain.engine.models import Detection, ScanContext
from app.domain.models.enums import Confidence

RULE_ID = "HARDCODED_SECRET"

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r'(?i)(password|secret|api_key|token|private_key)\s*=\s*"[^"$][^"]{2,}"'),
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
]
VAR_REFERENCE = re.compile(r"\$\{?var\.|!Ref\b|Fn::Ref")
PLACEHOLDER = re.compile(r"(?i)(changeme|placeholder|example|xxx+|todo)")


def detect(context: ScanContext) -> list[Detection]:
    detections: list[Detection] = []
    for raw in context.raw_files:
        for pattern in SECRET_PATTERNS:
            match = pattern.search(raw.content)
            if not match:
                continue
            matched_text = match.group(0)
            if PLACEHOLDER.search(matched_text):
                continue
            if VAR_REFERENCE.search(matched_text):
                continue
            detections.append(
                Detection(
                    rule_id=RULE_ID,
                    title="Hardcoded Secret Detected",
                    description=f"Potential hardcoded credential in '{raw.filename}'",
                    remediation=(
                        "Use Terraform variables, AWS Secrets Manager, or SSM Parameter Store"
                    ),
                    file_name=raw.filename,
                    line_number=line_number_for_match(raw.content, match),
                    evidence=matched_text[:200],
                    confidence=Confidence.HIGH,
                )
            )
            break
    return detections
