"""Open RDP port rule."""

from app.domain.models.enums import Severity
from app.domain.rules.base import is_open_cidr, make_finding, port_matches


class SgRdpOpenRule:
    rule_id = "SG_RDP_OPEN"

    def evaluate(self, scan_id, resources, raw_files):
        findings = []
        for resource in resources:
            if resource.resource_type != "aws_security_group":
                continue
            for rule in resource.properties.get("ingress_rules", []):
                if port_matches(rule, 3389) and is_open_cidr(rule.get("cidr_blocks")):
                    findings.append(
                        make_finding(
                            scan_id=scan_id,
                            rule_id=self.rule_id,
                            severity=Severity.HIGH,
                            title="RDP Port 3389 Open to the World",
                            description=f"Security group '{resource.resource_name}' allows RDP from 0.0.0.0/0",
                            remediation="Restrict ingress on port 3389 to trusted CIDR blocks",
                            resource_type=resource.resource_type,
                            resource_name=resource.resource_name,
                            file_name=resource.source_file,
                            evidence=str(rule),
                        )
                    )
        return findings
