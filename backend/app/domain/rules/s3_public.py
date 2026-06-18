"""S3 public bucket rule."""

from app.domain.models.enums import Severity
from app.domain.rules.base import make_finding


class S3PublicRule:
    rule_id = "S3_PUBLIC"

    def evaluate(self, scan_id, resources, raw_files):
        findings = []
        for resource in resources:
            if resource.resource_type != "aws_s3_bucket":
                continue
            acl = str(resource.properties.get("acl", "")).lower()
            block = resource.properties.get("public_access_block", {})
            public_acl = acl in ("public-read", "public-read-write", "authenticated-read")
            has_block = bool(block)
            if public_acl or (not has_block and acl in ("", "public-read")):
                findings.append(
                    make_finding(
                        scan_id=scan_id,
                        rule_id=self.rule_id,
                        severity=Severity.CRITICAL,
                        title="Public S3 Bucket Detected",
                        description=f"Bucket '{resource.resource_name}' has public or missing access controls",
                        remediation="Set acl = 'private' and enable aws_s3_bucket_public_access_block",
                        resource_type=resource.resource_type,
                        resource_name=resource.resource_name,
                        file_name=resource.source_file,
                        evidence=str({"acl": acl}),
                    )
                )
        return findings
