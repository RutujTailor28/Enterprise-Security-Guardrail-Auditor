"""Public database rule."""

from app.domain.models.enums import Severity
from app.domain.rules.base import make_finding


class DbPublicRule:
    rule_id = "DB_PUBLIC"

    def evaluate(self, scan_id, resources, raw_files):
        findings = []
        for resource in resources:
            if resource.resource_type != "aws_db_instance":
                continue
            publicly_accessible = resource.properties.get("publicly_accessible")
            if publicly_accessible is True or str(publicly_accessible).lower() == "true":
                findings.append(
                    make_finding(
                        scan_id=scan_id,
                        rule_id=self.rule_id,
                        severity=Severity.CRITICAL,
                        title="Publicly Accessible Database",
                        description=f"RDS instance '{resource.resource_name}' is publicly accessible",
                        remediation="Set publicly_accessible = false and restrict security groups",
                        resource_type=resource.resource_type,
                        resource_name=resource.resource_name,
                        file_name=resource.source_file,
                        evidence=str({"publicly_accessible": publicly_accessible}),
                    )
                )
        return findings
