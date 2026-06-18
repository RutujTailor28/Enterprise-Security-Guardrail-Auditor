"""Open RDP port detector."""

from app.domain.engine.detection_helpers import get_ingress_rules, is_open_cidr, port_in_range
from app.domain.engine.models import Detection, ScanContext

RULE_ID = "SG_RDP_OPEN"
RDP_PORT = 3389


def detect(context: ScanContext) -> list[Detection]:
    detections: list[Detection] = []
    for resource in context.resources_of_type("aws_security_group"):
        for rule in get_ingress_rules(resource):
            cidrs = rule.get("cidr_blocks") or rule.get("CidrIp")
            if port_in_range(rule, RDP_PORT) and is_open_cidr(cidrs):
                detections.append(
                    Detection(
                        rule_id=RULE_ID,
                        title="RDP Port 3389 Open to the World",
                        description=(
                            f"Security group '{resource.resource_name}' allows RDP (3389) "
                            "from 0.0.0.0/0"
                        ),
                        remediation="Restrict ingress on port 3389 to trusted CIDR blocks only",
                        resource_type=resource.resource_type,
                        resource_name=resource.resource_name,
                        file_name=resource.source_file,
                        evidence=str(rule),
                    )
                )
    return detections
