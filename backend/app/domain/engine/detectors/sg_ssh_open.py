"""Open SSH port detector."""

from app.domain.engine.detection_helpers import get_ingress_rules, is_open_cidr, port_in_range
from app.domain.engine.models import Detection, ScanContext

RULE_ID = "SG_SSH_OPEN"
SSH_PORT = 22


def detect(context: ScanContext) -> list[Detection]:
    detections: list[Detection] = []
    for resource in context.resources_of_type("aws_security_group"):
        for rule in get_ingress_rules(resource):
            cidrs = rule.get("cidr_blocks") or rule.get("CidrIp")
            if port_in_range(rule, SSH_PORT) and is_open_cidr(cidrs):
                detections.append(
                    Detection(
                        rule_id=RULE_ID,
                        title="SSH Port 22 Open to the World",
                        description=(
                            f"Security group '{resource.resource_name}' allows SSH (22) "
                            "from 0.0.0.0/0"
                        ),
                        remediation="Restrict ingress on port 22 to trusted CIDR blocks only",
                        resource_type=resource.resource_type,
                        resource_name=resource.resource_name,
                        file_name=resource.source_file,
                        evidence=str(rule),
                    )
                )
    return detections
