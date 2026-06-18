# API Reference

**Base URL:** `http://127.0.0.1:8000/api/v1`  
**Content-Type:** `application/json` (unless noted)  
**Authentication:** Optional `X-API-Key` header when `API_KEY` env is set

## Response envelope

Successful JSON responses:

```json
{
  "data": { },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-06-17T12:00:00Z"
  }
}
```

Paginated list responses:

```json
{
  "data": [ ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 42,
    "total_pages": 3,
    "request_id": "uuid",
    "timestamp": "2026-06-17T12:00:00Z"
  }
}
```

Error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": []
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-06-17T12:00:00Z"
  }
}
```

### Error codes

| Code | HTTP | Description |
|------|------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `NOT_FOUND` | 404 | Resource not found |
| `PAYLOAD_TOO_LARGE` | 413 | File or batch too large |
| `UNSUPPORTED_MEDIA_TYPE` | 415 | Invalid file extension |
| `PARSE_ERROR` | 422 | IaC parse failure |
| `SCAN_IN_PROGRESS` | 409 | Report requested before scan completes |
| `RATE_LIMITED` | 429 | Too many requests |
| `SCAN_TIMEOUT` | 504 | Scan exceeded time limit |

---

## Health

### `GET /health`

Liveness probe.

**Response 200**

```json
{ "data": { "status": "ok" }, "meta": { ... } }
```

### `GET /health/ready`

Readiness probe (database connectivity).

**Response 200** — `{ "data": { "status": "ready" } }`  
**Response 503** — `{ "data": { "status": "unavailable" } }`

---

## Scans

### `POST /scans`

Create an async security scan.

**Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `files` | file[] | Yes | `.tf`, `.tfvars`, `.json`, `.yaml`, `.yml`, `.template` |
| `label` | string | No | Human-readable scan name (max 120 chars) |

**Limits:** 10 MB/file · 50 MB/batch · 20 files max

**Response 202**

```json
{
  "data": {
    "id": "uuid",
    "label": "Production audit",
    "status": "pending",
    "status_url": "/api/v1/scans/{id}",
    "file_count": 2,
    "created_at": "2026-06-17T12:00:00Z"
  }
}
```

Poll `GET /scans/{id}` until status is terminal.

### `GET /scans`

List scans (paginated).

| Query | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |
| `status` | string | — | Filter: `pending`, `running`, `completed`, etc. |
| `sort` | string | `-created_at` | `created_at`, `-created_at`, `risk_score`, `-risk_score` |

**Response 200** — paginated list of scan summaries:

```json
{
  "id": "uuid",
  "label": "Production audit",
  "status": "completed",
  "risk_score": 78,
  "risk_grade": "Good",
  "severity_counts": { "critical": 1, "high": 0, "medium": 2, "low": 0, "info": 0 },
  "file_count": 2,
  "created_at": "2026-06-17T12:00:00Z"
}
```

### `GET /scans/{scan_id}`

Get scan details.

| Query | Description |
|-------|-------------|
| `include` | Comma-separated: `findings`, `files`, `parse_errors` |

**Response 200**

```json
{
  "data": {
    "id": "uuid",
    "label": "Production audit",
    "status": "completed",
    "risk_score": 78,
    "risk_grade": "Good",
    "raw_risk_score": 22,
    "normalized_score": 80,
    "severity_counts": { ... },
    "file_count": 2,
    "resource_count": 15,
    "duration_ms": 1250,
    "parser_version": "1.0.0",
    "error_message": null,
    "created_at": "2026-06-17T12:00:00Z",
    "completed_at": "2026-06-17T12:00:02Z"
  }
}
```

### `POST /scans/{scan_id}/cancel`

Cancel a running scan.

**Response 200** — updated scan object  
**Response 400** — scan already terminal

### `DELETE /scans/{scan_id}`

Delete scan and all associated data.

**Response 204** — no body

---

## Findings

### `GET /scans/{scan_id}/findings`

Paginated findings for a scan.

| Query | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |
| `severity` | string | — | `critical`, `high`, `medium`, `low`, `info` |
| `rule_id` | string | — | Filter by rule |
| `q` | string | — | Search title or resource name |

**Response 200**

```json
{
  "data": [
    {
      "id": "uuid",
      "rule_id": "S3_PUBLIC",
      "severity": "critical",
      "confidence": "high",
      "title": "Public S3 Bucket Detected",
      "description": "...",
      "remediation": "...",
      "resource_type": "aws_s3_bucket",
      "resource_name": "logs",
      "file_name": "main.tf",
      "line_number": 12,
      "evidence": "{...}"
    }
  ],
  "meta": { "page": 1, "page_size": 20, "total": 5, "total_pages": 1 }
}
```

---

## Files

### `GET /scans/{scan_id}/files`

List uploaded files for a scan.

### `GET /scans/{scan_id}/files/{file_id}`

Download original uploaded file.

**Note:** Disabled by default (`ALLOW_RAW_FILE_DOWNLOAD=false`). May contain unredacted secrets.

**Response 200** — `text/plain` attachment

---

## Reports

### `GET /scans/{scan_id}/report.pdf`

Download PDF security report.

Includes: scan summary, risk score, findings, recommendations, generated date.

**Response 200** — `application/pdf`  
**Response 409** — scan still in progress

### `GET /scans/{scan_id}/findings.csv`

Export findings as CSV (formula-injection safe).

**Response 200** — `text/csv`

### `GET /scans/{scan_id}/reports`

Report metadata and download URLs.

```json
{
  "data": {
    "scan_id": "uuid",
    "label": "Production audit",
    "status": "completed",
    "risk_score": 78,
    "risk_grade": "Good",
    "pdf_url": "/api/v1/scans/{id}/report.pdf",
    "csv_url": "/api/v1/scans/{id}/findings.csv"
  }
}
```

---

## Dashboard

### `GET /dashboard/summary`

Aggregate dashboard metrics.

```json
{
  "data": {
    "total_scans": 12,
    "latest_risk_score": 85,
    "latest_risk_grade": "Good",
    "open_critical_findings": 2,
    "findings_by_severity": { "critical": 3, "high": 5, "medium": 8, "low": 2, "info": 0 },
    "findings_by_rule": [{ "rule_id": "S3_PUBLIC", "count": 4 }],
    "last_scan_at": "2026-06-17T12:00:00Z"
  }
}
```

### `GET /dashboard/trends`

Historical trends.

| Query | Default | Description |
|-------|---------|-------------|
| `days` | 30 | Lookback period (1–365) |

```json
{
  "data": {
    "risk_scores": [{ "date": "2026-06-17", "score": 78 }],
    "findings_over_time": [{ "date": "2026-06-17", "critical": 1, "high": 2, "medium": 3 }]
  }
}
```

---

## Rules

### `GET /rules`

List all security rules in the catalog.

```json
{
  "data": [
    {
      "id": "S3_PUBLIC",
      "name": "Public S3 Buckets",
      "severity_default": "critical",
      "description": "Detects public S3 bucket configurations",
      "enabled": true
    }
  ]
}
```

---

## Interactive documentation

When `ENV != production`:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Example workflow (curl)

```bash
# 1. Create scan
RESP=$(curl -s -X POST http://127.0.0.1:8000/api/v1/scans \
  -F "files=@backend/tests/fixtures/dataset/terraform/insecure/public_s3.tf" \
  -F "label=demo")
SCAN_ID=$(echo $RESP | python -c "import sys,json; print(json.load(sys.stdin)['data']['id'])")

# 2. Poll until complete
curl -s http://127.0.0.1:8000/api/v1/scans/$SCAN_ID

# 3. Get findings
curl -s "http://127.0.0.1:8000/api/v1/scans/$SCAN_ID/findings"

# 4. Download PDF
curl -s -o report.pdf http://127.0.0.1:8000/api/v1/scans/$SCAN_ID/report.pdf
```
