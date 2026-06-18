"""SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class ScanModel(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    normalized_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    critical_count: Mapped[int] = mapped_column(Integer, default=0)
    high_count: Mapped[int] = mapped_column(Integer, default=0)
    medium_count: Mapped[int] = mapped_column(Integer, default=0)
    low_count: Mapped[int] = mapped_column(Integer, default=0)
    info_count: Mapped[int] = mapped_column(Integer, default=0)
    resource_count: Mapped[int] = mapped_column(Integer, default=0)
    file_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parser_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    uploaded_files: Mapped[list["UploadedFileModel"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )
    findings: Mapped[list["FindingModel"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )
    parse_errors: Mapped[list["ParseErrorModel"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )
    report: Mapped["ReportModel | None"] = relationship(
        back_populates="scan", cascade="all, delete-orphan", uselist=False
    )


class UploadedFileModel(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    stored_path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    scan: Mapped["ScanModel"] = relationship(back_populates="uploaded_files")


class FindingModel(Base):
    __tablename__ = "findings"
    __table_args__ = (
        UniqueConstraint("scan_id", "fingerprint", name="uq_findings_scan_fingerprint"),
        Index("idx_findings_scan_id", "scan_id"),
        Index("idx_findings_severity", "severity"),
        Index("idx_findings_rule_id", "rule_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False
    )
    rule_id: Mapped[str] = mapped_column(String(50), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(10), nullable=False)
    confidence: Mapped[str] = mapped_column(String(10), nullable=False, default="high")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    remediation: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resource_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    scan: Mapped["ScanModel"] = relationship(back_populates="findings")


class ParseErrorModel(Base):
    __tablename__ = "parse_errors"
    __table_args__ = (Index("idx_parse_errors_scan_id", "scan_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    error_code: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    scan: Mapped["ScanModel"] = relationship(back_populates="parse_errors")


class ReportModel(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    scan: Mapped["ScanModel"] = relationship(back_populates="report")


class ScanRuleModel(Base):
    __tablename__ = "scan_rules"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    severity_default: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
