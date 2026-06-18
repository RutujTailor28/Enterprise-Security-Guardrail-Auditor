"""Pytest configuration."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["ENV"] = "test"

from app.config import DATA_DIR, get_settings  # noqa: E402
from app.infrastructure.database.base import Base  # noqa: E402
from app.infrastructure.database import models  # noqa: F401, E402
from app.main import create_app  # noqa: E402

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def test_engine(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    get_settings.cache_clear()
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    from app.infrastructure.database.models import ScanRuleModel

    session = sessionmaker(bind=engine)()
    rules = [
        ("S3_PUBLIC", "Public S3 Buckets", "critical", "Detects public S3"),
        ("SG_SSH_OPEN", "Open SSH", "high", "Open SSH"),
        ("SG_RDP_OPEN", "Open RDP", "high", "Open RDP"),
        ("IAM_WILDCARD", "IAM Wildcard", "critical", "Wildcard IAM"),
        ("MISSING_ENCRYPTION", "Missing Encryption", "high", "Encryption"),
        ("DB_PUBLIC", "Public DB", "critical", "Public DB"),
        ("MISSING_LOGGING", "Missing Logging", "medium", "Logging"),
        ("MISSING_BACKUP", "Missing Backup", "medium", "Backup"),
        ("HARDCODED_SECRET", "Hardcoded Secret", "critical", "Secrets"),
        ("SG_OVERLY_PERMISSIVE", "Permissive SG", "high", "Permissive SG"),
    ]
    for rule_id, name, severity, desc in rules:
        session.add(
            ScanRuleModel(
                id=rule_id,
                name=name,
                severity_default=severity,
                description=desc,
                enabled=True,
            )
        )
    session.commit()
    session.close()
    yield engine
    get_settings.cache_clear()


@pytest.fixture
def db_session(test_engine):
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(test_engine, monkeypatch):
    monkeypatch.setattr("app.infrastructure.database.session._engine", test_engine)
    monkeypatch.setattr(
        "app.infrastructure.database.session._SessionLocal",
        sessionmaker(bind=test_engine, autoflush=False, autocommit=False),
    )
    monkeypatch.setattr("app.main.run_migrations", lambda: None)
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR
