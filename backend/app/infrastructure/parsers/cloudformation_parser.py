"""CloudFormation parser."""

import hashlib
import json

import yaml

from app.domain.models.enums import Resolution
from app.domain.models.parse_result import ParseResult
from app.domain.models.resource import NormalizedResource
from app.domain.services.file_safety import CLOUDFORMATION_EXTENSIONS


class CloudFormationParser:
    def can_parse(self, filename: str) -> bool:
        lower = filename.lower()
        return any(lower.endswith(ext) for ext in CLOUDFORMATION_EXTENSIONS)

    def parse(self, content: str, filename: str) -> ParseResult:
        content = content.replace("\r\n", "\n")
        try:
            if filename.lower().endswith(".json"):
                data = json.loads(content)
            else:
                data = yaml.safe_load(content)
        except Exception as exc:
            return ParseResult(errors=[str(exc)])

        if not isinstance(data, dict):
            return ParseResult(errors=["CloudFormation template must be a mapping"])

        resources_section = data.get("Resources", {})
        resources: list[NormalizedResource] = []
        for name, definition in resources_section.items():
            if not isinstance(definition, dict):
                continue
            cfn_type = definition.get("Type", "")
            props = definition.get("Properties", {}) or {}
            resource_type = self._map_cfn_type(cfn_type)
            resource_id = hashlib.sha256(f"{filename}:{cfn_type}:{name}".encode()).hexdigest()[:16]
            resources.append(
                NormalizedResource(
                    id=resource_id,
                    source_file=filename,
                    provider="aws",
                    resource_type=resource_type,
                    resource_name=name,
                    properties=self._flatten_properties(props),
                    resolution=Resolution.PARTIAL if self._has_intrinsic(props) else Resolution.RESOLVED,
                    raw_block=content[:2000],
                )
            )
        return ParseResult(resources=resources)

    def _map_cfn_type(self, cfn_type: str) -> str:
        mapping = {
            "AWS::S3::Bucket": "aws_s3_bucket",
            "AWS::EC2::SecurityGroup": "aws_security_group",
            "AWS::IAM::Policy": "aws_iam_policy",
            "AWS::IAM::Role": "aws_iam_role",
            "AWS::IAM::ManagedPolicy": "aws_iam_policy",
            "AWS::RDS::DBInstance": "aws_db_instance",
            "AWS::DynamoDB::Table": "aws_dynamodb_table",
            "AWS::EC2::Volume": "aws_ebs_volume",
            "AWS::S3::BucketPolicy": "aws_s3_bucket_policy",
            "AWS::CloudTrail::Trail": "aws_cloudtrail",
        }
        return mapping.get(cfn_type, cfn_type.replace("::", "_").lower())

    def _flatten_properties(self, props: dict, prefix: str = "") -> dict:
        flat: dict = {}
        for key, value in props.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                if len(value) == 1 and list(value.keys())[0].startswith("Fn::"):
                    flat[full_key] = value
                else:
                    flat.update(self._flatten_properties(value, full_key))
            else:
                flat[full_key] = value
        return flat

    def _has_intrinsic(self, value) -> bool:
        if isinstance(value, dict):
            if any(str(k).startswith("Fn::") or k == "Ref" for k in value):
                return True
            return any(self._has_intrinsic(v) for v in value.values())
        if isinstance(value, list):
            return any(self._has_intrinsic(v) for v in value)
        return False
