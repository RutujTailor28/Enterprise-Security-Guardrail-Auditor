"""Overly permissive security group detector."""

from app.domain.engine.detection_helpers import get_ingress_rules, is_all_ports_rule, is_open_cidr
from app.domain.engine.models import Detection, ScanContext

RULE_ID = "SG_OVERLY_PERMISSIVE"


def detect(context: ScanContext) -> list[Detection]:
    detections: list[Detection] = []
    for resource in context.resources_of_type("aws_security_group"):
        for rule in get_ingress_rules(resource):
            cidrs = rule.get("cidr_blocks") or rule.get("CidrIp")
            if is_all_ports_rule(rule) and is_open_cidr(cidrs):
                detections.append(
                    Detection(
                        rule_id=RULE_ID,
                        title="Overly Permissive Security Group",
                        description=(
                            f"Security group '{resource.resource_name}' allows all inbound "
                            "traffic from the internet"
                        ),
                        remediation="Restrict ingress to specific ports and trusted CIDR ranges",
                        resource_type=resource.resource_type,
                        resource_name=resource.resource_name,
                        file_name=resource.source_file,
                        evidence=str(rule),
                    )
                )
    return detections
