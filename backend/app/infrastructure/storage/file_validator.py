"""File upload validation."""

import unicodedata
from pathlib import Path

from app.api.exceptions import PayloadTooLargeError, UnsupportedMediaTypeError, ValidationError
from app.config import Settings
from app.domain.services.file_safety import (
    ALLOWED_EXTENSIONS,
    BLOCKED_EXTENSIONS,
    get_file_type,
)


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    if ".." in filename or name != Path(filename).name:
        raise ValidationError("Invalid filename")
    name = unicodedata.normalize("NFC", name)
    name = name.replace('"', "_").replace("\r", "").replace("\n", "")
    return name[:255] if len(name) > 255 else name


def validate_file_content(content: bytes, filename: str, settings: Settings) -> None:
    if len(content) == 0:
        raise ValidationError(f"File '{filename}' is empty")
    if len(content) > settings.max_file_size_bytes:
        raise PayloadTooLargeError(
            f"File '{filename}' exceeds maximum size of {settings.max_file_size_bytes} bytes"
        )
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"File '{filename}' must be valid UTF-8 text") from exc


def validate_filename(filename: str) -> str:
    safe_name = sanitize_filename(filename)
    lower = safe_name.lower()
    for blocked in BLOCKED_EXTENSIONS:
        if lower.endswith(blocked):
            raise UnsupportedMediaTypeError(f"File type '{blocked}' is not allowed")
    if not any(lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise UnsupportedMediaTypeError(
            f"File '{safe_name}' has unsupported extension. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    if get_file_type(safe_name) is None:
        raise UnsupportedMediaTypeError(f"Unable to determine file type for '{safe_name}'")
    return safe_name
