"""Secret redaction tests."""

from app.domain.services.redaction import redact_text


def test_redact_aws_key():
    text = 'access_key = "AKIAIOSFODNN7EXAMPLE"'
    result = redact_text(text)
    assert "AKIA" not in result
    assert "[REDACTED]" in result
