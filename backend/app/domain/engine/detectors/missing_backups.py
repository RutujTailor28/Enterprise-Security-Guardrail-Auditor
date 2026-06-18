"""Missing backup detector."""

from app.domain.engine.models import Detection, ScanContext

RULE_ID = "MISSING_BACKUP"


def _rds_backup_insufficient(properties: dict) -> bool:
    retention = properties.get("backup_retention_period")
    if retention is None:
        retention = properties.get("BackupRetentionPeriod", 0)
    try:
        return int(retention) <= 0
    except (TypeError, ValueError):
        return True


def _s3_versioning_disabled(properties: dict) -> bool:
    versioning = properties.get("versioning")
    if not versioning:
        return True
    if isinstance(versioning, list):
        for item in versioning:
            if isinstance(item, dict):
                enabled = item.get("enabled")
                if enabled is True or str(enabled).lower() == "true":
                    return False
        return True
    if isinstance(versioning, dict):
        enabled = versioning.get("enabled")
        return enabled is not True and str(enabled).lower() != "true"
    return True


def detect(context: ScanContext) -> list[Detection]:
    detections: list[Detection] = []
    for resource in context.resources_of_type("aws_db_instance", "aws_rds_cluster"):
        if _rds_backup_insufficient(resource.properties):
            detections.append(
                Detection(
                    rule_id=RULE_ID,
                    title="RDS Backup Retention Not Configured",
                    description=f"RDS '{resource.resource_name}' has insufficient backup retention",
                    remediation="Set backup_retention_period to at least 7 days",
                    resource_type=resource.resource_type,
                    resource_name=resource.resource_name,
                    file_name=resource.source_file,
                    evidence=str(
                        {"backup_retention_period": resource.properties.get("backup_retention_period")}
                    ),
                )
            )

    for resource in context.resources_of_type("aws_s3_bucket"):
        if _s3_versioning_disabled(resource.properties):
            detections.append(
                Detection(
                    rule_id=RULE_ID,
                    title="S3 Versioning Disabled",
                    description=f"S3 bucket '{resource.resource_name}' does not have versioning enabled",
                    remediation="Enable versioning on the bucket for data recovery protection",
                    resource_type=resource.resource_type,
                    resource_name=resource.resource_name,
                    file_name=resource.source_file,
                )
            )
    return detections
