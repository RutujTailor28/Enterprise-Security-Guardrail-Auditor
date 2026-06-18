"""Scan application service."""

from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.api.exceptions import NotFoundError, ValidationError
from app.config import Settings
from app.domain.models.enums import FileType, ScanStatus
from app.domain.services.file_safety import get_file_type
from app.infrastructure.repositories.file_repository import UploadedFileRepository
from app.infrastructure.repositories.finding_repository import FindingRepository
from app.infrastructure.repositories.parse_error_repository import ParseErrorRepository
from app.infrastructure.repositories.scan_repository import ScanRepository
from app.infrastructure.storage.file_storage import FileStorage
from app.infrastructure.storage.safe_http import content_disposition_attachment
from app.infrastructure.storage.upload_reader import read_upload_with_limit
from app.infrastructure.storage.file_validator import validate_file_content, validate_filename
from app.domain.services.scoring import compute_grade
from app.infrastructure.workers.scan_runner import request_cancel, run_scan


class ScanService:
    def __init__(self, session: Session, settings: Settings):
        self._session = session
        self._settings = settings
        self._scan_repo = ScanRepository(session)
        self._file_repo = UploadedFileRepository(session)
        self._finding_repo = FindingRepository(session)
        self._parse_error_repo = ParseErrorRepository(session)
        self._storage = FileStorage()

    async def create_scan(self, files: list[UploadFile], label: str | None, background_tasks) -> dict:
        if not files:
            raise ValidationError("At least one file is required", [{"field": "files", "message": "required"}])
        if len(files) > self._settings.max_files_per_scan:
            raise ValidationError(f"Maximum {self._settings.max_files_per_scan} files per scan")
        if label and len(label) > 120:
            raise ValidationError("Label must be 120 characters or fewer", [{"field": "label", "message": "too long"}])

        total_size = 0
        validated: list[tuple[str, bytes]] = []
        for upload in files:
            filename = upload.filename or "unknown"
            safe_name = validate_filename(filename)
            content = await read_upload_with_limit(upload, self._settings.max_file_size_bytes)
            validate_file_content(content, safe_name, self._settings)
            total_size += len(content)
            validated.append((safe_name, content))

        if total_size > self._settings.max_batch_size_bytes:
            from app.api.exceptions import PayloadTooLargeError

            raise PayloadTooLargeError("Total upload size exceeds batch limit")

        scan = self._scan_repo.create(label=label)
        file_records: list[dict] = []

        for safe_name, content in validated:
            stored_name = self._storage.resolve_unique_name(scan.id, safe_name)
            stored_path = self._storage.save_file(scan.id, stored_name, content)
            file_type = FileType(get_file_type(safe_name))
            record = self._file_repo.create(
                scan_id=scan.id,
                original_filename=safe_name,
                stored_filename=stored_name,
                file_type=file_type,
                content_hash=FileStorage.content_hash(content),
                size_bytes=len(content),
                stored_path=stored_path,
            )
            file_records.append(
                {
                    "original_filename": record.original_filename,
                    "stored_path": record.stored_path,
                }
            )

        scan.file_count = len(file_records)
        self._scan_repo.update(scan)
        self._session.commit()

        background_tasks.add_task(run_scan, scan.id, file_records)

        return {
            "id": scan.id,
            "label": scan.label,
            "status": scan.status.value,
            "status_url": f"{self._settings.api_v1_prefix}/scans/{scan.id}",
            "file_count": scan.file_count,
            "created_at": scan.created_at.isoformat() + "Z",
        }

    def get_scan(self, scan_id: str, include: set[str] | None = None) -> dict:
        scan = self._scan_repo.get_by_id(scan_id)
        if not scan:
            raise NotFoundError(f"Scan '{scan_id}' not found")
        include = include or set()
        data = self._scan_to_dict(scan)
        if "findings" in include:
            findings, total = self._finding_repo.list_by_scan(scan_id, page=1, page_size=50)
            data["findings"] = [self._finding_to_dict(f) for f in findings]
            data["findings_url"] = f"{self._settings.api_v1_prefix}/scans/{scan_id}/findings"
            data["findings_total"] = total
        if "files" in include:
            data["files"] = [
                self._file_to_dict(f) for f in self._file_repo.list_by_scan(scan_id)
            ]
        if "parse_errors" in include:
            data["parse_errors"] = [
                self._parse_error_to_dict(e) for e in self._parse_error_repo.list_by_scan(scan_id)
            ]
        return data

    def list_scans(self, page: int, page_size: int, status: str | None, sort: str) -> tuple[list, int]:
        scans, total = self._scan_repo.list_scans(page, page_size, status, sort)
        return [self._scan_summary(s) for s in scans], total

    def cancel_scan(self, scan_id: str) -> dict:
        scan = self._scan_repo.get_by_id(scan_id)
        if not scan:
            raise NotFoundError(f"Scan '{scan_id}' not found")
        if scan.is_terminal:
            raise ValidationError("Scan has already finished and cannot be cancelled")
        request_cancel(scan_id)
        scan.status = ScanStatus.CANCELLED
        scan.completed_at = datetime.utcnow()
        self._scan_repo.update(scan)
        self._session.commit()
        return self._scan_to_dict(scan)

    def get_file_content(self, scan_id: str, file_id: str) -> tuple[bytes, str]:
        if not self._settings.allow_raw_file_download:
            raise ValidationError("Raw file download is disabled")
        scan = self._scan_repo.get_by_id(scan_id)
        if not scan:
            raise NotFoundError(f"Scan '{scan_id}' not found")
        file_record = self._file_repo.get_by_id(file_id)
        if not file_record or file_record.scan_id != scan_id:
            raise NotFoundError("File not found")
        content = self._storage.read_file(file_record.stored_path)
        return content, file_record.original_filename

    def delete_scan(self, scan_id: str) -> None:
        scan = self._scan_repo.get_by_id(scan_id)
        if not scan:
            raise NotFoundError(f"Scan '{scan_id}' not found")
        if scan.status in (ScanStatus.PENDING, ScanStatus.PROCESSING):
            request_cancel(scan_id)
            scan.status = ScanStatus.CANCELLED
            scan.completed_at = datetime.utcnow()
            self._scan_repo.update(scan)
            self._session.commit()
        self._scan_repo.delete(scan_id)
        self._storage.delete_scan_files(scan_id)

    def _scan_summary(self, scan) -> dict:
        return {
            "id": scan.id,
            "label": scan.label,
            "status": scan.status.value,
            "risk_score": scan.risk_score,
            "risk_grade": compute_grade(scan.risk_score),
            "severity_counts": scan.severity_counts,
            "file_count": scan.file_count,
            "created_at": scan.created_at.isoformat() + "Z",
        }

    def _scan_to_dict(self, scan) -> dict:
        return {
            **self._scan_summary(scan),
            "normalized_score": scan.normalized_score,
            "raw_risk_score": scan.raw_risk_score,
            "resource_count": scan.resource_count,
            "duration_ms": scan.duration_ms,
            "parser_version": scan.parser_version,
            "error_message": scan.error_message,
            "completed_at": scan.completed_at.isoformat() + "Z" if scan.completed_at else None,
        }

    @staticmethod
    def _finding_to_dict(finding) -> dict:
        return {
            "id": finding.id,
            "rule_id": finding.rule_id,
            "severity": finding.severity.value,
            "confidence": finding.confidence.value,
            "title": finding.title,
            "description": finding.description,
            "remediation": finding.remediation,
            "resource_type": finding.resource_type,
            "resource_name": finding.resource_name,
            "file_name": finding.file_name,
            "line_number": finding.line_number,
            "evidence": finding.evidence,
        }

    @staticmethod
    def _file_to_dict(file_record) -> dict:
        return {
            "id": file_record.id,
            "original_filename": file_record.original_filename,
            "stored_filename": file_record.stored_filename,
            "file_type": file_record.file_type.value,
            "size_bytes": file_record.size_bytes,
            "content_hash": file_record.content_hash,
            "created_at": file_record.created_at.isoformat() + "Z",
        }

    @staticmethod
    def _parse_error_to_dict(error) -> dict:
        return {
            "id": error.id,
            "filename": error.filename,
            "error_code": error.error_code,
            "message": error.message,
            "line_number": error.line_number,
        }
