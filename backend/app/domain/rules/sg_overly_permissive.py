"""Overly permissive security group rule."""

from app.domain.models.enums import Severity
from app.domain.rules.base import is_open_cidr, make_finding


class SgOverlyPermissiveRule:
    rule_id = "SG_OVERLY_PERMISSIVE"

    def evaluate(self, scan_id, resources, raw_files):
        findings = []
        for resource in resources:
            if resource.resource_type != "aws_security_group":
                continue
            for rule in resource.properties.get("ingress_rules", []):
                protocol = str(rule.get("protocol") or rule.get("IpProtocol", "")).lower()
                from_port = rule.get("from_port") or rule.get("FromPort")
                to_port = rule.get("to_port") or rule.get("ToPort")
                all_ports = protocol in ("-1", "all") or (
                    str(from_port) == "0" and str(to_port) == "65535"
                )
                if all_ports and is_open_cidr(rule.get("cidr_blocks")):
                    findings.append(
                        make_finding(
                            scan_id=scan_id,
                            rule_id=self.rule_id,
                            severity=Severity.HIGH,
                            title="Overly Permissive Security Group",
                            description=(
                            f"Security group '{resource.resource_name}' allows "
                            "all traffic from the internet"
                        ),
                            remediation="Restrict ingress to required ports and trusted CIDR ranges",
                            resource_type=resource.resource_type,
                            resource_name=resource.resource_name,
                            file_name=resource.source_file,
                            evidence=str(rule),
                        )
                    )
        return findings
