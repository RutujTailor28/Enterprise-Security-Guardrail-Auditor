"""Report API integration tests."""

import time


def _poll_scan(client, scan_id: str, timeout: float = 10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = client.get(f"/api/v1/scans/{scan_id}")
        assert response.status_code == 200
        status = response.json()["data"]["status"]
        if status in ("completed", "completed_with_errors", "failed", "cancelled"):
            return response.json()["data"]
        time.sleep(0.2)
    raise TimeoutError(f"Scan {scan_id} did not complete")


def test_download_pdf_report(client, fixtures_dir):
    tf_path = fixtures_dir / "terraform" / "public_s3.tf"
    with tf_path.open("rb") as handle:
        response = client.post(
            "/api/v1/scans",
            files=[("files", ("public_s3.tf", handle, "text/plain"))],
            data={"label": "report-test"},
        )
    assert response.status_code == 202
    scan_id = response.json()["data"]["id"]
    _poll_scan(client, scan_id)

    pdf_response = client.get(f"/api/v1/scans/{scan_id}/report.pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
    assert pdf_response.content.startswith(b"%PDF")
    assert len(pdf_response.content) > 1000

    csv_response = client.get(f"/api/v1/scans/{scan_id}/findings.csv")
    assert csv_response.status_code == 200
    assert "text/csv" in csv_response.headers["content-type"]
    assert b"rule_id" in csv_response.content
