"""Full scan API integration tests."""

import time
from pathlib import Path


def _poll_scan(client, scan_id: str, timeout: float = 10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = client.get(f"/api/v1/scans/{scan_id}?include=findings")
        assert response.status_code == 200
        status = response.json()["data"]["status"]
        if status in ("completed", "completed_with_errors", "failed", "cancelled"):
            return response.json()["data"]
        time.sleep(0.2)
    raise TimeoutError(f"Scan {scan_id} did not complete")


def test_create_scan_public_s3(client, fixtures_dir):
    tf_path = fixtures_dir / "terraform" / "public_s3.tf"
    with tf_path.open("rb") as handle:
        response = client.post(
            "/api/v1/scans",
            files=[("files", ("public_s3.tf", handle, "text/plain"))],
            data={"label": "s3-test"},
        )
    assert response.status_code == 202
    scan_id = response.json()["data"]["id"]
    result = _poll_scan(client, scan_id)
    assert result["status"] == "completed"
    assert result["raw_risk_score"] >= 10
    assert result["risk_score"] <= 90
    assert result["risk_grade"] in ("Excellent", "Good", "Warning", "Critical")
    rule_ids = {f["rule_id"] for f in result.get("findings", [])}
    assert "S3_PUBLIC" in rule_ids


def test_create_scan_open_ssh(client, fixtures_dir):
    tf_path = fixtures_dir / "terraform" / "open_ssh.tf"
    with tf_path.open("rb") as handle:
        response = client.post(
            "/api/v1/scans",
            files=[("files", ("open_ssh.tf", handle, "text/plain"))],
        )
    assert response.status_code == 202
    scan_id = response.json()["data"]["id"]
    result = _poll_scan(client, scan_id)
    rule_ids = {f["rule_id"] for f in result.get("findings", [])}
    assert "SG_SSH_OPEN" in rule_ids


def test_list_rules(client):
    response = client.get("/api/v1/rules")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 10
