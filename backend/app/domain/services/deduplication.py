"""Finding deduplication."""

from app.domain.models.finding import Finding


def deduplicate_findings(findings: list[Finding]) -> list[Finding]:
    seen: set[str] = set()
    unique: list[Finding] = []
    for finding in findings:
        if finding.fingerprint in seen:
            continue
        seen.add(finding.fingerprint)
        unique.append(finding)
    return unique
