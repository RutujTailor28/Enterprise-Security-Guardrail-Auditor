"""Missing backups rule."""

from app.domain.models.enums import Severity
from app.domain.rules.base import make_finding


class MissingBackupsRule:
    rule_id = "MISSING_BACKUP"

    def evaluate(self, scan_id, resources, raw_files):
        findings = []
        for resource in resources:
            if resource.resource_type == "aws_db_instance":
                retention = resource.properties.get("backup_retention_period", 0)
                try:
                    retention_val = int(retention)
                except (TypeError, ValueError):
                    retention_val = 0
                if retention_val <= 0:
                    findings.append(
                        make_finding(
                            scan_id=scan_id,
                            rule_id=self.rule_id,
                            severity=Severity.MEDIUM,
                            title="RDS Backup Retention Not Configured",
                            description=f"RDS '{resource.resource_name}' has no backup retention",
                            remediation="Set backup_retention_period to at least 7 days",
                            resource_type=resource.resource_type,
                            resource_name=resource.resource_name,
                            file_name=resource.source_file,
                        )
                    )
            if resource.resource_type == "aws_s3_bucket":
                versioning = resource.properties.get("versioning")
                enabled = False
                if isinstance(versioning, dict):
                    enabled = versioning.get("enabled") is True
                if not enabled:
                    findings.append(
                        make_finding(
                            scan_id=scan_id,
                            rule_id=self.rule_id,
                            severity=Severity.MEDIUM,
                            title="S3 Versioning Disabled",
                            description=f"S3 bucket '{resource.resource_name}' does not have versioning enabled",
                            remediation="Enable versioning on the S3 bucket for backup protection",
                            resource_type=resource.resource_type,
                            resource_name=resource.resource_name,
                            file_name=resource.source_file,
                        )
                    )
        return findings
