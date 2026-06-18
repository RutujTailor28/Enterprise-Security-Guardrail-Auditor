"""HTTP response helpers for safe file delivery."""

import re
from urllib.parse import quote

_UNSAFE_FILENAME = re.compile(r'[\x00-\x1f"\\/\r\n]+')


def safe_download_filename(filename: str, fallback: str = "download") -> str:
    """Return a header-safe attachment filename."""
    cleaned = _UNSAFE_FILENAME.sub("_", filename or "").strip("._")
    if not cleaned:
        cleaned = fallback
    return cleaned[:200]


def content_disposition_attachment(filename: str, fallback: str = "download") -> str:
    """Build a Content-Disposition header resistant to injection."""
    safe = safe_download_filename(filename, fallback)
    encoded = quote(safe)
    return f'attachment; filename="{safe}"; filename*=UTF-8\'\'{encoded}'
