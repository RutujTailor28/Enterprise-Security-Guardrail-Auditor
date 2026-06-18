"""Health endpoint tests."""

def test_health_returns_ok(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "ok"
    assert "request_id" in body["meta"]
    assert response.headers.get("X-Request-ID")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
