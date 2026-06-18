"""Database session management."""

import logging
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import DATA_DIR, REPORTS_DIR, UPLOADS_DIR, get_settings

logger = logging.getLogger(__name__)

_engine = None
_SessionLocal = None


def ensure_data_dirs() -> None:
    for path in (DATA_DIR, UPLOADS_DIR, REPORTS_DIR):
        Path(path).mkdir(parents=True, exist_ok=True)


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        ensure_data_dirs()
        _engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )

        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_db_connection() -> bool:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error("Database connection check failed: %s", exc)
        return False


def run_migrations() -> None:
    from alembic.config import Config

    from alembic import command

    backend_root = Path(__file__).resolve().parents[2]
    alembic_cfg = Config(str(backend_root / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(backend_root / "alembic"))
    command.upgrade(alembic_cfg, "head")
