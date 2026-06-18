"""Terraform HCL parser."""

import hashlib
import json

import hcl2

from app.domain.models.enums import Resolution
from app.domain.models.parse_result import ParseResult
from app.domain.models.resource import NormalizedResource
from app.domain.services.file_safety import TERRAFORM_EXTENSIONS


def _strip_quotes(value):
    if isinstance(value, str):
        return value.strip('"')
    if isinstance(value, list):
        return [_strip_quotes(v) for v in value]
    if isinstance(value, dict):
        return {_strip_quotes(k): _strip_quotes(v) for k, v in value.items()}
    return value


class TerraformParser:
    def can_parse(self, filename: str) -> bool:
        lower = filename.lower()
        if lower.endswith(".tf.json"):
            return True
        return any(lower.endswith(ext) for ext in TERRAFORM_EXTENSIONS if ext != ".tf.json")

    def parse(self, content: str, filename: str) -> ParseResult:
        content = content.replace("\r\n", "\n")
        try:
            if filename.lower().endswith(".tf.json"):
                data = json.loads(content)
            else:
                data = hcl2.loads(content)
            data = _strip_quotes(data)
        except Exception as exc:
            return ParseResult(errors=[str(exc)])

        resources: list[NormalizedResource] = []
        resource_blocks = data.get("resource", [])
        if isinstance(resource_blocks, dict):
            resource_blocks = [resource_blocks]

        for block in resource_blocks:
            if not isinstance(block, dict):
                continue
            for resource_type, instances in block.items():
                resource_type = str(resource_type).strip('"')
                provider = resource_type.split("_")[0] if "_" in resource_type else "unknown"
                if not isinstance(instances, dict):
                    continue
                for name, props in instances.items():
                    name = str(name).strip('"')
                    if not isinstance(props, dict):
                        continue
                    props.pop("__is_block__", None)
                    resource_id = hashlib.sha256(
                        f"{filename}:{resource_type}:{name}".encode()
                    ).hexdigest()[:16]
                    resources.append(
                        NormalizedResource(
                            id=resource_id,
                            source_file=filename,
                            provider=provider,
                            resource_type=resource_type,
                            resource_name=name,
                            properties=self._flatten(props),
                            resolution=Resolution.RESOLVED,
                            raw_block=content[:2000],
                        )
                    )
        return ParseResult(resources=resources)

    def _flatten(self, props: dict, prefix: str = "") -> dict:
        flat: dict = {}
        for key, value in props.items():
            key = str(key).strip('"')
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                value.pop("__is_block__", None)
                flat.update(self._flatten(value, full_key))
            elif isinstance(value, list):
                flat[full_key] = [_strip_quotes(item) for item in value]
            else:
                flat[full_key] = _strip_quotes(value)
        return flat
