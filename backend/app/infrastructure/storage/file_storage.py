"""Local filesystem storage for uploads."""

import hashlib
import shutil
from pathlib import Path

from app.config import UPLOADS_DIR


class FileStorage:
    def __init__(self, base_dir: Path | None = None):
        self._base_dir = base_dir or UPLOADS_DIR

    def scan_dir(self, scan_id: str) -> Path:
        path = self._base_dir / scan_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def content_hash(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def save_file(self, scan_id: str, stored_filename: str, content: bytes) -> str:
        directory = self.scan_dir(scan_id)
        target = directory / stored_filename
        target.write_bytes(content)
        return str(target.relative_to(self._base_dir.parent))

    def read_file(self, stored_path: str) -> bytes:
        base = self._base_dir.parent.resolve()
        full_path = (base / stored_path).resolve()
        if not full_path.is_relative_to(base):
            raise ValueError("Invalid stored path")
        return full_path.read_bytes()

    def delete_scan_files(self, scan_id: str) -> None:
        directory = self._base_dir / scan_id
        if directory.exists():
            shutil.rmtree(directory, ignore_errors=True)

    def resolve_unique_name(self, scan_id: str, filename: str) -> str:
        directory = self.scan_dir(scan_id)
        candidate = filename
        counter = 2
        while (directory / candidate).exists():
            stem = Path(filename).stem
            suffix = Path(filename).suffix
            candidate = f"{stem} ({counter}){suffix}"
            counter += 1
        return candidate
