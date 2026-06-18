"""Initial database schema."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scans",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("label", sa.String(120), nullable=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=True),
        sa.Column("normalized_score", sa.Integer(), nullable=True),
        sa.Column("raw_risk_score", sa.Integer(), nullable=True),
        sa.Column("critical_count", sa.Integer(), server_default="0"),
        sa.Column("high_count", sa.Integer(), server_default="0"),
        sa.Column("medium_count", sa.Integer(), server_default="0"),
        sa.Column("low_count", sa.Integer(), server_default="0"),
        sa.Column("info_count", sa.Integer(), server_default="0"),
        sa.Column("resource_count", sa.Integer(), server_default="0"),
        sa.Column("file_count", sa.Integer(), server_default="0"),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("parser_version", sa.String(20), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_scans_created_at", "scans", ["created_at"])
    op.create_index("idx_scans_completed_at", "scans", ["completed_at"])
    op.create_index("idx_scans_status", "scans", ["status"])
    op.create_index("idx_scans_risk_score", "scans", ["risk_score"])

    op.create_table(
        "uploaded_files",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scan_id", sa.String(36), sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("stored_filename", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(20), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("stored_path", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_uploaded_files_scan_id", "uploaded_files", ["scan_id"])

    op.create_table(
        "findings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scan_id", sa.String(36), sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rule_id", sa.String(50), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(10), nullable=False),
        sa.Column("confidence", sa.String(10), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("remediation", sa.Text(), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_name", sa.String(255), nullable=True),
        sa.Column("file_name", sa.String(255), nullable=True),
        sa.Column("line_number", sa.Integer(), nullable=True),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("scan_id", "fingerprint", name="uq_findings_scan_fingerprint"),
    )
    op.create_index("idx_findings_scan_id", "findings", ["scan_id"])
    op.create_index("idx_findings_severity", "findings", ["severity"])
    op.create_index("idx_findings_rule_id", "findings", ["rule_id"])

    op.create_table(
        "parse_errors",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scan_id", sa.String(36), sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("error_code", sa.String(50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_parse_errors_scan_id", "parse_errors", ["scan_id"])

    op.create_table(
        "reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scan_id", sa.String(36), sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "scan_rules",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("severity_default", sa.String(10), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("1")),
    )


def downgrade() -> None:
    op.drop_table("scan_rules")
    op.drop_table("reports")
    op.drop_table("parse_errors")
    op.drop_table("findings")
    op.drop_table("uploaded_files")
    op.drop_table("scans")
