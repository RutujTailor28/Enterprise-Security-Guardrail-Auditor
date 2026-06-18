---
marp: true
theme: default
paginate: true
title: Enterprise Security Guardrail Auditor
description: API-first IaC security scanning platform — challenge submission deck
---

# Enterprise Security Guardrail Auditor

**API-first security scanning for Terraform & CloudFormation**

June 2026 · Challenge Submission

---

## The Problem

- Infrastructure-as-code (IaC) misconfigurations are a leading cause of cloud breaches
- Manual review does not scale across teams and environments
- Security teams need **fast, repeatable guardrails** before deployment
- Developers need **actionable findings**, not raw scanner noise

---

## Our Solution

An **API-first platform** that:

1. Accepts Terraform and CloudFormation uploads
2. Parses and normalizes AWS resources
3. Runs **10 security rules** against each scan
4. Produces a **risk score + grade**
5. Surfaces findings on a **dashboard**
6. Exports **PDF and CSV reports**

---

## Key Features

| Feature | Description |
|---------|-------------|
| Upload & scan | `.tf`, `.tfvars`, `.json`, `.yaml`, `.yml` |
| Risk scoring | 0–100 security score with letter grade |
| Dashboard | Severity charts, trends, top rules |
| Scan history | Paginated list with filters |
| Findings detail | Remediation guidance per finding |
| Reports | PDF summary + CSV export |

---

## System Architecture

```
User Browser
    ↓
React + Vite UI
    ↓ REST /api/v1
FastAPI Application
    ├── SQLite (metadata, findings)
    ├── Background Scan Worker
    ├── Parsers (HCL / YAML / JSON)
    └── Detection + Rules + Scoring Engine
```

**Design:** Clean architecture · API-first · Async scans (202 + poll)

---

## Backend Layers

| Layer | Responsibility |
|-------|----------------|
| `api/` | Routes, middleware, schemas |
| `application/` | Scan, dashboard, report services |
| `domain/` | Engine, detectors, scoring, models |
| `infrastructure/` | DB, parsers, storage, PDF/CSV |

Follows **SOLID** principles and **OWASP** security recommendations.

---

## Scan Pipeline

1. **Upload** — validate extension, size, UTF-8, path safety
2. **Parse** — Terraform (HCL) and CloudFormation (YAML/JSON)
3. **Normalize** — unified resource model across formats
4. **Detect** — 10 rule detectors on normalized resources
5. **Score** — penalty-based security score (0–100)
6. **Redact** — strip secrets from evidence before storage
7. **Persist** — findings, counts, and grades in SQLite

---

## Security Rules (10)

| Rule | Detects |
|------|---------|
| `S3_PUBLIC` | Public S3 bucket ACL / missing block |
| `SG_SSH_OPEN` | SSH (22) open to 0.0.0.0/0 |
| `SG_RDP_OPEN` | RDP (3389) open to 0.0.0.0/0 |
| `IAM_WILDCARD` | Wildcard IAM actions/resources |
| `MISSING_ENCRYPTION` | Unencrypted storage at rest |
| `DB_PUBLIC` | Publicly accessible database |
| `MISSING_LOGGING` | S3 without access logging |
| `MISSING_BACKUP` | Missing RDS/S3 backup config |
| `HARDCODED_SECRET` | Credentials in source code |
| `SG_OVERLY_PERMISSIVE` | All ports open from internet |

---

## Risk Scoring

**Penalty weights:** Critical 10 · High 7 · Medium 4 · Low 1 · Info 0

**Security score** = `100 − min(100, total_penalty)`

| Score | Grade |
|-------|-------|
| 90–100 | Excellent |
| 70–89 | Good |
| 50–69 | Warning |
| 0–49 | Critical |

Higher score = better security posture.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI, Pydantic, Uvicorn |
| Database | SQLAlchemy, SQLite (WAL), Alembic |
| Parsing | python-hcl2, PyYAML |
| Reports | ReportLab (PDF), CSV exporter |
| Frontend | React 18, TypeScript, Vite, Tailwind |
| Charts | Recharts |
| Tests | pytest — **75 automated tests** |

---

## API Design

Base URL: `/api/v1`

| Endpoint | Purpose |
|----------|---------|
| `POST /scans` | Create async scan (202) |
| `GET /scans/{id}` | Poll scan status |
| `GET /scans/{id}/findings` | Paginated findings |
| `GET /scans/{id}/report.pdf` | PDF report |
| `GET /dashboard/summary` | Dashboard metrics |
| `GET /rules` | Rule catalog |

Full reference: `docs/API.md` · Swagger: `/docs` (dev)

---

## Frontend (5 Pages)

1. **Dashboard** — risk score card, severity pie chart, trends, top rules
2. **Upload** — drag-and-drop with client-side validation
3. **Scan History** — sortable table, status filters, pagination
4. **Findings Detail** — expandable rows, remediation, export links
5. **Reports** — PDF and CSV download cards

Responsive layout · Lazy-loaded routes · Accessible (ARIA, skip link)

---

## Security Hardening

- Optional **API key** auth (`X-API-Key` header)
- File upload validation (whitelist, size limits, chunked reads)
- **Path traversal** protection on file storage
- **Secret redaction** in findings evidence
- Rate limiting (60 req/min/IP)
- Security headers (CSP, X-Frame-Options, HSTS)
- Raw file download **disabled by default**
- CSV formula-injection protection

---

## Testing & Quality

| Layer | Coverage |
|-------|----------|
| Unit — rules | 20 tests (one per detector + engine) |
| Unit — scoring/PDF | 20+ tests |
| Integration — API | Health, scans, reports |
| Dataset validation | 22 IaC samples (secure + insecure) |

**Result:** 75/75 tests passing · Frontend production build verified

---

## Demo Workflow

```bash
# 1. Start stack
powershell -File scripts/dev.ps1

# 2. Open UI
http://127.0.0.1:5173

# 3. Upload insecure Terraform sample
backend/tests/fixtures/dataset/terraform/insecure/public_s3.tf

# 4. Review findings → download PDF report
```

---

## AI Development Process

All code generated via **Cursor AI** with full audit trail:

- `prompts.md` — 12 entries documenting every prompt and response
- Architecture-first approach (v2.0 approved before coding)
- Iterative phases: backend → frontend → scoring → reports → dataset → security audit → submission

No manual file edits by the developer (per project rules).

---

## Roadmap (Post-MVP)

| Phase | Enhancement |
|-------|-------------|
| CI/CD | GitHub Actions pipeline |
| Scale | Celery/RQ job queue, Redis rate limiting |
| Auth | Per-user RBAC, multi-tenancy |
| Deploy | Docker Compose, cloud deployment |
| Rules | Custom rule packs, policy-as-code |

Documented in `docs/ROADMAP.md`.

---

## Repository & Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview |
| `INSTALLATION.md` | Setup guide |
| `ARCHITECTURE.md` | Design summary |
| `docs/ARCHITECTURE.md` | Full v2.0 architecture |
| `docs/API.md` | REST API reference |
| `docs/PRESENTATION.md` | This deck |
| `SUBMISSION_CHECKLIST.md` | Requirement verification |

---

# Thank You

**Enterprise Security Guardrail Auditor**

Questions?

GitHub: `security-guardrail-auditor`

---

## Appendix: Export to PowerPoint

This deck uses [Marp](https://marp.app/) slide syntax (`---` separators).

### Option A — Marp CLI (recommended)

```bash
npm install -g @marp-team/marp-cli
marp docs/PRESENTATION.md --pptx -o docs/PRESENTATION.pptx
```

### Option B — VS Code

Install the **Marp for VS Code** extension → open this file → Export Slide Deck → PPTX.

### Option C — Pandoc

```bash
pandoc docs/PRESENTATION.md -o docs/PRESENTATION.pptx
```
