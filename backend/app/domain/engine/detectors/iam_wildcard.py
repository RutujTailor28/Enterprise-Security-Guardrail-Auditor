"""Wildcard IAM permissions detector."""

from app.domain.engine.detection_helpers import policy_has_wildcard
from app.domain.engine.models import Detection, ScanContext

RULE_ID = "IAM_WILDCARD"

IAM_POLICY_TYPES = frozenset(
    {
        "aws_iam_policy",
        "aws_iam_role_policy",
        "aws_iam_user_policy",
        "aws_iam_role",
        "aws_iam_user",
        "aws_iam_group",
    }
)


def _extract_policy_documents(resource) -> list:
    docs = []
    for key in ("policy", "PolicyDocument", "policy_document", "inline_policy"):
        value = resource.properties.get(key)
        if value:
            if isinstance(value, list):
                docs.extend(value)
            else:
                docs.append(value)

    statement = resource.properties.get("PolicyDocument.Statement")
    if statement is not None:
        doc = {"Statement": statement}
        docs.append(doc)

    return docs


def detect(context: ScanContext) -> list[Detection]:
    detections: list[Detection] = []
    for resource in context.resources:
        if resource.resource_type not in IAM_POLICY_TYPES:
            continue
        for doc in _extract_policy_documents(resource):
            if policy_has_wildcard(doc):
                detections.append(
                    Detection(
                        rule_id=RULE_ID,
                        title="Wildcard IAM Permissions",
                        description=(
                            f"IAM resource '{resource.resource_name}' grants wildcard "
                            "actions or resources"
                        ),
                        remediation="Apply least privilege: scope Action and Resource to required ARNs",
                        resource_type=resource.resource_type,
                        resource_name=resource.resource_name,
                        file_name=resource.source_file,
                        evidence=str(doc)[:500],
                    )
                )
                break
    return detections
