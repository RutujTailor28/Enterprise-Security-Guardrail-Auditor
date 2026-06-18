"""Finding fingerprint generation."""

import hashlib


def generate_fingerprint(
    rule_id: str,
    resource_type: str | None,
    resource_name: str | None,
    file_name: str | None,
    line_number: int | None,
) -> str:
    payload = "|".join(
        [
            rule_id,
            resource_type or "",
            resource_name or "",
            file_name or "",
            str(line_number or ""),
        ]
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]
