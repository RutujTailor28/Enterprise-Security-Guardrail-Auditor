"""Missing logging detector."""

from app.domain.engine.models import Detection, ScanContext

RULE_ID = "MISSING_LOGGING"


def _has_s3_logging(properties: dict) -> bool:
    logging = properties.get("logging")
    if not logging:
        return False
    if isinstance(logging, dict):
        return bool(logging.get("target_bucket") or logging.get("TargetBucket"))
    return True


def detect(context: ScanContext) -> list[Detection]:
    detections: list[Detection] = []
    for resource in context.resources_of_type("aws_s3_bucket"):
        if not _has_s3_logging(resource.properties):
            detections.append(
                Detection(
                    rule_id=RULE_ID,
                    title="S3 Access Logging Disabled",
                    description=(
                        f"S3 bucket '{resource.resource_name}' has no access logging configured"
                    ),
                    remediation="Add a logging block with target_bucket and target_prefix",
                    resource_type=resource.resource_type,
                    resource_name=resource.resource_name,
                    file_name=resource.source_file,
                )
            )
    return detections
