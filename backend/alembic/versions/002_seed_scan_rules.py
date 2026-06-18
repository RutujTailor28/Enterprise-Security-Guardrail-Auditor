"""Seed scan rules."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RULES = [
    ("S3_PUBLIC", "Public S3 Buckets", "critical", "Detects publicly accessible S3 buckets"),
    ("SG_SSH_OPEN", "Open SSH Port 22", "high", "Detects security groups open to the world on port 22"),
    ("SG_RDP_OPEN", "Open RDP Port 3389", "high", "Detects security groups open to the world on port 3389"),
    ("IAM_WILDCARD", "Wildcard IAM Permissions", "critical", "Detects IAM policies with wildcard actions or resources"),
    ("MISSING_ENCRYPTION", "Missing Encryption", "high", "Detects storage resources without encryption enabled"),
    ("DB_PUBLIC", "Public Databases", "critical", "Detects publicly accessible database instances"),
    ("MISSING_LOGGING", "Missing Logging", "medium", "Detects missing access or audit logging configuration"),
    ("MISSING_BACKUP", "Missing Backups", "medium", "Detects databases or buckets without backup/versioning"),
    ("HARDCODED_SECRET", "Hardcoded Secrets", "critical", "Detects hardcoded credentials in IaC files"),
    ("SG_OVERLY_PERMISSIVE", "Overly Permissive Security Groups", "high", "Detects security groups open to all ports"),
]


def upgrade() -> None:
    table = sa.table(
        "scan_rules",
        sa.column("id", sa.String),
        sa.column("name", sa.String),
        sa.column("severity_default", sa.String),
        sa.column("description", sa.String),
        sa.column("enabled", sa.Boolean),
    )
    op.bulk_insert(
        table,
        [
            {
                "id": rule_id,
                "name": name,
                "severity_default": severity,
                "description": description,
                "enabled": True,
            }
            for rule_id, name, severity, description in RULES
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM scan_rules")
