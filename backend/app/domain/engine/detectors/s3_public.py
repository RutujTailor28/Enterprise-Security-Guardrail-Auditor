"""Public S3 bucket detector."""

from app.domain.engine.detection_helpers import (
    is_public_s3_acl,
    s3_has_public_access_block,
    s3_policy_is_public,
)
from app.domain.engine.models import Detection, ScanContext

RULE_ID = "S3_PUBLIC"


def detect(context: ScanContext) -> list[Detection]:
    detections: list[Detection] = []
    for resource in context.resources_of_type("aws_s3_bucket"):
        acl = str(resource.properties.get("acl", "")).lower()
        public_acl = is_public_s3_acl(acl)
        has_block = s3_has_public_access_block(resource.properties)
        public_policy = s3_policy_is_public(resource.properties)

        if public_acl or public_policy:
            detections.append(
                Detection(
                    rule_id=RULE_ID,
                    title="Public S3 Bucket Detected",
                    description=(
                        f"S3 bucket '{resource.resource_name}' is publicly accessible "
                        "or lacks public access blocks"
                    ),
                    remediation=(
                        "Set acl = 'private', block public access, and restrict bucket policies"
                    ),
                    resource_type=resource.resource_type,
                    resource_name=resource.resource_name,
                    file_name=resource.source_file,
                    evidence=str(
                        {
                            "acl": acl,
                            "public_policy": public_policy,
                            "has_public_access_block": has_block,
                        }
                    ),
                )
            )
        elif not has_block and acl not in ("private", ""):
            detections.append(
                Detection(
                    rule_id=RULE_ID,
                    title="Public S3 Bucket Detected",
                    description=(
                        f"S3 bucket '{resource.resource_name}' lacks public access blocks"
                    ),
                    remediation=(
                        "Set acl = 'private', block public access, and restrict bucket policies"
                    ),
                    resource_type=resource.resource_type,
                    resource_name=resource.resource_name,
                    file_name=resource.source_file,
                    evidence=str({"acl": acl, "has_public_access_block": has_block}),
                )
            )
    return detections
