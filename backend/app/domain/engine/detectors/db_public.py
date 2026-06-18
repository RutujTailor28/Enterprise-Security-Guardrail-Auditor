"""Public database detector."""

from app.domain.engine.models import Detection, ScanContext

RULE_ID = "DB_PUBLIC"


def _is_truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes")


def detect(context: ScanContext) -> list[Detection]:
    detections: list[Detection] = []
    for resource in context.resources_of_type("aws_db_instance", "aws_rds_cluster"):
        publicly_accessible = resource.properties.get("publicly_accessible")
        if publicly_accessible is None:
            publicly_accessible = resource.properties.get("PubliclyAccessible")
        if _is_truthy(publicly_accessible):
            detections.append(
                Detection(
                    rule_id=RULE_ID,
                    title="Publicly Accessible Database",
                    description=(
                        f"Database '{resource.resource_name}' has publicly_accessible enabled"
                    ),
                    remediation="Set publicly_accessible = false and restrict security groups",
                    resource_type=resource.resource_type,
                    resource_name=resource.resource_name,
                    file_name=resource.source_file,
                    evidence=str({"publicly_accessible": resource.properties.get("publicly_accessible")}),
                )
            )
    return detections
