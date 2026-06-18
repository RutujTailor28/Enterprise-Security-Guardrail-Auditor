"""IAM wildcard permissions rule."""

from app.domain.models.enums import Severity
from app.domain.rules.base import make_finding


class IamWildcardRule:
    rule_id = "IAM_WILDCARD"

    def evaluate(self, scan_id, resources, raw_files):
        findings = []
        policy_types = ("aws_iam_policy", "aws_iam_role_policy", "aws_iam_user_policy")
        for resource in resources:
            if resource.resource_type not in policy_types:
                continue
            policy_doc = resource.properties.get("policy") or resource.properties.get("PolicyDocument")
            if self._has_wildcard(policy_doc):
                findings.append(
                    make_finding(
                        scan_id=scan_id,
                        rule_id=self.rule_id,
                        severity=Severity.CRITICAL,
                        title="Wildcard IAM Permissions",
                        description=f"IAM policy '{resource.resource_name}' contains wildcard permissions",
                        remediation="Scope IAM actions and resources to least privilege",
                        resource_type=resource.resource_type,
                        resource_name=resource.resource_name,
                        file_name=resource.source_file,
                        evidence=str(policy_doc)[:500],
                    )
                )
        return findings

    def _has_wildcard(self, doc) -> bool:
        if doc is None:
            return False
        if isinstance(doc, str) and "*" in doc:
            return True
        statements = []
        if isinstance(doc, dict):
            statements = doc.get("Statement", [])
            if isinstance(statements, dict):
                statements = [statements]
        for stmt in statements:
            if not isinstance(stmt, dict):
                continue
            actions = stmt.get("Action", [])
            resources = stmt.get("Resource", [])
            if actions == "*" or actions == ["*"]:
                return True
            if isinstance(actions, list) and "*" in actions:
                return True
            if resources == "*" or resources == ["*"]:
                return True
            if isinstance(resources, list) and "*" in resources:
                return True
        return False
