"""API dependencies."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.scan_service import ScanService
from app.config import Settings, get_settings
from app.infrastructure.database.session import get_db


def get_settings_dep() -> Settings:
    return get_settings()


def get_scan_service(
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> ScanService:
    return ScanService(session, settings)
