"""Security hardening unit tests."""

import pytest

from app.infrastructure.storage.file_storage import FileStorage
from app.infrastructure.storage.safe_http import content_disposition_attachment, safe_download_filename


def test_safe_download_filename_strips_unsafe_chars():
    assert safe_download_filename('evil"\r\nname.tf', "fallback") == "evil_name.tf"


def test_content_disposition_has_no_quotes_injection():
    header = content_disposition_attachment('bad"name.tf', "report.pdf")
    assert "bad_name.tf" in header
    assert 'filename="' in header


def test_read_file_rejects_path_traversal(tmp_path):
    base = tmp_path / "data"
    uploads = base / "uploads"
    uploads.mkdir(parents=True)
    storage = FileStorage(uploads)
    with pytest.raises(ValueError, match="Invalid stored path"):
        storage.read_file("../secrets.txt")
