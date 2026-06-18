"""Missing encryption rule."""

from app.domain.models.enums import Severity
from app.domain.rules.base import make_finding

ENCRYPTED_TYPES = {
    "aws_s3_bucket": ("server_side_encryption_configuration",),
    "aws_db_instance": ("storage_encrypted",),
    "aws_ebs_volume": ("encrypted",),
    "aws_dynamodb_table": ("server_side_encryption",),
}


class MissingEncryptionRule:
    rule_id = "MISSING_ENCRYPTION"

    def evaluate(self, scan_id, resources, raw_files):
        findings = []
        for resource in resources:
            keys = ENCRYPTED_TYPES.get(resource.resource_type)
            if not keys:
                continue
            if not any(resource.properties.get(k) for k in keys):
                findings.append(
                    make_finding(
                        scan_id=scan_id,
                        rule_id=self.rule_id,
                        severity=Severity.HIGH,
                        title="Missing Encryption at Rest",
                        description=f"Resource '{resource.resource_name}' does not enable encryption",
                        remediation="Enable encryption at rest for this resource type",
                        resource_type=resource.resource_type,
                        resource_name=resource.resource_name,
                        file_name=resource.source_file,
                    )
                )
        return findings
