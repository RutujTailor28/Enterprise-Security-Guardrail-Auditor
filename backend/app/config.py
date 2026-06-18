"""Application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
REPORTS_DIR = DATA_DIR / "reports"
DB_PATH = DATA_DIR / "auditor.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Security Guardrail Auditor"
    app_version: str = "1.0.0"
    env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    api_key: str | None = None
    allow_raw_file_download: bool = False
    log_level: str = "INFO"

    database_url: str = Field(default_factory=lambda: f"sqlite:///{DB_PATH.as_posix()}")

    max_file_size_bytes: int = 10 * 1024 * 1024
    max_batch_size_bytes: int = 50 * 1024 * 1024
    max_files_per_scan: int = 20
    scan_timeout_seconds: int = 60
    rate_limit_per_minute: int = 60

    severity_weight_critical: int = 10
    severity_weight_high: int = 7
    severity_weight_medium: int = 4
    severity_weight_low: int = 1
    severity_weight_info: int = 0

    max_evidence_length: int = 4096
    parser_version: str = "1.0.0"

    @property
    def is_production(self) -> bool:
        return self.env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
