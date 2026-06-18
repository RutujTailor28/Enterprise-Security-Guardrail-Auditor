"""Secret redaction service."""

import re

AWS_KEY_PATTERN = re.compile(r"AKIA[0-9A-Z]{16}")
SECRET_ASSIGNMENT = re.compile(
    r'(?i)(password|secret|api_key|token|private_key)\s*=\s*"[^"]+"'
)
PEM_PATTERN = re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----")
VAR_REFERENCE = re.compile(r"\$\{?var\.|!Ref|Fn::Ref")

REDACTED = "[REDACTED]"


def redact_text(text: str | None) -> str | None:
    if not text:
        return text
    if VAR_REFERENCE.search(text) and not AWS_KEY_PATTERN.search(text):
        return text
    result = AWS_KEY_PATTERN.sub(REDACTED, text)
    result = SECRET_ASSIGNMENT.sub(lambda m: m.group(0).split("=")[0] + '= "' + REDACTED + '"', result)
    result = PEM_PATTERN.sub(REDACTED, result)
    return result


def truncate_evidence(text: str | None, max_length: int = 4096) -> str | None:
    if text is None:
        return None
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
