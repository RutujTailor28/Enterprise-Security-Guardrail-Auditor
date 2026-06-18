"""Missing logging rule."""

from app.domain.models.enums import Severity
from app.domain.rules.base import make_finding


class MissingLoggingRule:
    rule_id = "MISSING_LOGGING"

    def evaluate(self, scan_id, resources, raw_files):
        findings = []
        for resource in resources:
            if resource.resource_type == "aws_s3_bucket":
                logging = resource.properties.get("logging")
                if not logging:
                    findings.append(
                        make_finding(
                            scan_id=scan_id,
                            rule_id=self.rule_id,
                            severity=Severity.MEDIUM,
                            title="S3 Access Logging Disabled",
                            description=f"S3 bucket '{resource.resource_name}' has no access logging",
                            remediation="Configure logging block on the S3 bucket",
                            resource_type=resource.resource_type,
                            resource_name=resource.resource_name,
                            file_name=resource.source_file,
                        )
                    )
            if resource.resource_type == "aws_cloudtrail" and not resource.properties:
                findings.append(
                    make_finding(
                        scan_id=scan_id,
                        rule_id=self.rule_id,
                        severity=Severity.MEDIUM,
                        title="CloudTrail Not Configured",
                        description="No CloudTrail trail resources found in scan scope",
                        remediation="Enable AWS CloudTrail for audit logging",
                    )
                )
        return findings
