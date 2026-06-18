"""Hardcoded secrets rule."""

import re

from app.domain.models.enums import Confidence, Severity
from app.domain.rules.base import make_finding

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r'(?i)(password|secret|api_key|token)\s*=\s*"[^"$][^"]+"'),
]
VAR_PATTERN = re.compile(r"\$\{?var\.|!Ref")


class HardcodedSecretsRule:
    rule_id = "HARDCODED_SECRET"

    def evaluate(self, scan_id, resources, raw_files):
        findings = []
        for raw in raw_files:
            if VAR_PATTERN.search(raw.content) and not any(
                p.search(raw.content) for p in SECRET_PATTERNS
            ):
                continue
            for pattern in SECRET_PATTERNS:
                match = pattern.search(raw.content)
                if match:
                    line_number = raw.content[: match.start()].count("\n") + 1
                    findings.append(
                        make_finding(
                            scan_id=scan_id,
                            rule_id=self.rule_id,
                            severity=Severity.CRITICAL,
                            title="Hardcoded Secret Detected",
                            description=f"Potential secret found in '{raw.filename}'",
                            remediation="Use variables, secrets manager, or parameter store instead of literals",
                            file_name=raw.filename,
                            line_number=line_number,
                            evidence=match.group(0)[:200],
                            confidence=Confidence.HIGH,
                        )
                    )
                    break
        return findings
