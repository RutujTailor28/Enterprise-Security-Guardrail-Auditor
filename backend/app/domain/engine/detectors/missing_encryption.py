"""Missing encryption detector."""

from app.domain.engine.detection_helpers import property_has_encryption
from app.domain.engine.models import Detection, ScanContext

RULE_ID = "MISSING_ENCRYPTION"

ENCRYPTED_RESOURCE_TYPES = frozenset(
    {
        "aws_s3_bucket",
        "aws_db_instance",
        "aws_ebs_volume",
        "aws_dynamodb_table",
        "aws_rds_cluster",
        "aws_efs_file_system",
    }
)


def detect(context: ScanContext) -> list[Detection]:
    detections: list[Detection] = []
    for resource in context.resources:
        if resource.resource_type not in ENCRYPTED_RESOURCE_TYPES:
            continue
        if property_has_encryption(resource.properties):
            continue
        detections.append(
            Detection(
                rule_id=RULE_ID,
                title="Missing Encryption at Rest",
                description=(
                    f"Resource '{resource.resource_name}' ({resource.resource_type}) "
                    "does not enable encryption at rest"
                ),
                remediation="Enable server-side encryption or storage encryption for this resource",
                resource_type=resource.resource_type,
                resource_name=resource.resource_name,
                file_name=resource.source_file,
            )
        )
    return detections
