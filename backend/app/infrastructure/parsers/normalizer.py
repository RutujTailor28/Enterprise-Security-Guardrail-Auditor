"""Resource normalizer — links related resources and flattens ingress rules."""

from app.domain.models.resource import NormalizedResource


def normalize_resources(resources: list[NormalizedResource]) -> list[NormalizedResource]:
    buckets = {r.resource_name: r for r in resources if r.resource_type == "aws_s3_bucket"}
    access_blocks = {}
    for r in resources:
        if r.resource_type == "aws_s3_bucket_public_access_block":
            bucket_key = r.properties.get("bucket", r.resource_name)
            if isinstance(bucket_key, str):
                bucket_key = bucket_key.split(".")[-1].replace('"', "")
            access_blocks[bucket_key] = r
            access_blocks[r.resource_name] = r
    for name, bucket in buckets.items():
        if name in access_blocks:
            bucket.related_resources.append(access_blocks[name].id)
            bucket.properties["public_access_block"] = access_blocks[name].properties
        _normalize_s3_bucket_properties(bucket)

    normalized: list[NormalizedResource] = []
    for resource in resources:
        if resource.resource_type == "aws_security_group":
            ingress = resource.properties.get("ingress") or resource.properties.get("ingress_rules")
            if not ingress:
                ingress = resource.properties.get("SecurityGroupIngress")
            if ingress and isinstance(ingress, list):
                resource.properties["ingress_rules"] = _flatten_ingress(ingress)
        normalized.append(resource)
    return normalized


def _normalize_s3_bucket_properties(bucket: NormalizedResource) -> None:
    """Map CloudFormation S3 property names to Terraform-style fields used by detectors."""
    if "acl" not in bucket.properties:
        access_control = bucket.properties.get("AccessControl")
        if access_control:
            bucket.properties["acl"] = str(access_control).replace("PublicRead", "public-read").replace(
                "PublicReadWrite", "public-read-write"
            ).replace("Private", "private").lower()

    block: dict = {}
    for key, value in bucket.properties.items():
        if key.startswith("PublicAccessBlockConfiguration."):
            block_key = key.split(".", 1)[1]
            block[block_key] = value
    if block:
        bucket.properties["public_access_block"] = block

    versioning_status = bucket.properties.get("VersioningConfiguration.Status")
    if versioning_status is not None and "versioning" not in bucket.properties:
        bucket.properties["versioning"] = {"enabled": str(versioning_status).lower() == "enabled"}

    target_bucket = bucket.properties.get("LoggingConfiguration.DestinationBucketName")
    if target_bucket and "logging" not in bucket.properties:
        bucket.properties["logging"] = {
            "target_bucket": target_bucket,
            "target_prefix": bucket.properties.get("LoggingConfiguration.LogFilePrefix", ""),
        }


def _flatten_ingress(ingress: list) -> list[dict]:
    rules: list[dict] = []
    for rule in ingress:
        if not isinstance(rule, dict):
            continue
        rules.append(
            {
                "from_port": (
                    rule.get("from_port")
                    if rule.get("from_port") is not None
                    else rule.get("FromPort")
                ),
                "to_port": (
                    rule.get("to_port")
                    if rule.get("to_port") is not None
                    else rule.get("ToPort")
                ),
                "protocol": rule.get("protocol") or rule.get("IpProtocol"),
                "cidr_blocks": rule.get("cidr_blocks")
                or rule.get("cidr_ipv4")
                or _extract_cidrs(rule),
            }
        )
    return rules


def _extract_cidrs(rule: dict) -> list:
    cidrs = []
    for key in ("cidr_blocks", "cidr_ipv4", "CidrIp", "CidrIpv4"):
        val = rule.get(key)
        if val:
            if isinstance(val, list):
                cidrs.extend(val)
            else:
                cidrs.append(val)
    ip_ranges = rule.get("IpRanges") or rule.get("ip_ranges")
    if isinstance(ip_ranges, list):
        for item in ip_ranges:
            if isinstance(item, dict) and item.get("CidrIp"):
                cidrs.append(item["CidrIp"])
    return cidrs
