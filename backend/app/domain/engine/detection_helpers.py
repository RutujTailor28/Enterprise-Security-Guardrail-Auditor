"""Shared detection helper utilities."""

import json
import re
from typing import Any


def is_open_cidr(cidr: Any) -> bool:
    if cidr is None:
        return False
    if isinstance(cidr, list):
        return any(is_open_cidr(c) for c in cidr)
    return str(cidr).strip() in ("0.0.0.0/0", "::/0")


def port_in_range(rule: dict, target_port: int) -> bool:
    from_port = (
        rule.get("from_port")
        if rule.get("from_port") is not None
        else rule.get("FromPort")
    )
    to_port = (
        rule.get("to_port") if rule.get("to_port") is not None else rule.get("ToPort")
    )
    if from_port is None and to_port is None:
        return False
    try:
        start = int(from_port) if from_port is not None else int(to_port)
        end = int(to_port) if to_port is not None else int(from_port)
    except (TypeError, ValueError):
        return False
    return start <= target_port <= end


def is_all_ports_rule(rule: dict) -> bool:
    protocol = str(rule.get("protocol") or rule.get("IpProtocol", "")).lower()
    from_port = (
        rule.get("from_port")
        if rule.get("from_port") is not None
        else rule.get("FromPort")
    )
    to_port = (
        rule.get("to_port") if rule.get("to_port") is not None else rule.get("ToPort")
    )
    if protocol in ("-1", "all"):
        return True
    try:
        return int(from_port) == 0 and int(to_port) == 65535
    except (TypeError, ValueError):
        return False


def get_ingress_rules(resource) -> list[dict]:
    rules = resource.properties.get("ingress_rules")
    if rules:
        return rules if isinstance(rules, list) else []
    ingress = resource.properties.get("ingress")
    if isinstance(ingress, list):
        return ingress
    return []


def property_has_encryption(properties: dict) -> bool:
    encryption_keys = (
        "server_side_encryption_configuration",
        "storage_encrypted",
        "encrypted",
        "server_side_encryption",
        "sse_specification",
        "kms_key_id",
    )
    for key, value in properties.items():
        lower_key = key.lower()
        if any(token in lower_key for token in ("encrypt", "kms", "sse")):
            if value not in (None, False, "", [], {}):
                return True
        if key in encryption_keys and value not in (None, False, "", [], {}):
            return True
    return False


def policy_has_wildcard(doc: Any) -> bool:
    if doc is None:
        return False
    if isinstance(doc, str):
        if re.search(r'(?:Action|Resource|NotAction|NotResource)\s*=\s*"\*"', doc):
            return True
        if re.search(r'"(?:Action|Resource|NotAction|NotResource)"\s*:\s*"\*"', doc):
            return True
        try:
            doc = json.loads(doc)
        except json.JSONDecodeError:
            return False
    if not isinstance(doc, dict):
        return False
    statements = doc.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]
    for stmt in statements:
        if not isinstance(stmt, dict):
            continue
        for field in ("Action", "Resource", "NotAction", "NotResource"):
            value = stmt.get(field)
            if value == "*" or value == ["*"]:
                return True
            if isinstance(value, list) and "*" in value:
                return True
    return False


def is_public_s3_acl(acl: str) -> bool:
    return acl.lower() in ("public-read", "public-read-write", "authenticated-read")


def s3_has_public_access_block(properties: dict) -> bool:
    block = properties.get("public_access_block", {})
    if not isinstance(block, dict) or not block:
        return False
    flags = (
        block.get("block_public_acls") or block.get("BlockPublicAcls"),
        block.get("block_public_policy") or block.get("BlockPublicPolicy"),
        block.get("ignore_public_acls") or block.get("IgnorePublicAcls"),
        block.get("restrict_public_buckets") or block.get("RestrictPublicBuckets"),
    )
    return any(flags)


def s3_policy_is_public(properties: dict) -> bool:
    policy = properties.get("policy") or properties.get("Policy")
    if not policy:
        return False
    policy_text = policy if isinstance(policy, str) else json.dumps(policy)
    return '"Principal":"*"' in policy_text.replace(" ", "") or '"Principal": "*"' in policy_text


def line_number_for_match(content: str, match: re.Match) -> int:
    return content[: match.start()].count("\n") + 1
