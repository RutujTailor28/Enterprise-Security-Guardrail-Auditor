# Enterprise Security Guardrail Auditor

API-first platform for scanning **Terraform** and **CloudFormation** infrastructure-as-code for AWS security misconfigurations. Upload IaC files, receive a risk score with letter grade, review findings on a dashboard, and export PDF/CSV reports.

[![Tests](https://img.shields.io/badge/tests-75%20passing-brightgreen)](/backend/tests)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](/backend)
[![React](https://img.shields.io/badge/react-18-61dafb)](/frontend)

## Features

- **Upload & scan** — Terraform (`.tf`, `.tfvars`, `.tf.json`) and CloudFormation (`.json`, `.yaml`, `.yml`)
- **10 security rules** — S3 public access, open SSH/RDP, IAM wildcards, missing encryption, public DBs, logging, backups, hardcoded secrets, permissive security groups
- **Risk scoring** — Penalty-based security score (0–100) with grades: Excellent, Good, Warning, Critical
- **Dashboard** — Severity charts, risk trends, top rules (Recharts)
- **Scan history** — Paginated list with filters and status tracking
- **Findings detail** — Expandable findings with remediation guidance
- **Reports** — PDF (summary, findings, recommendations) and CSV export
- **Test dataset** — 22 secure/insecure IaC samples with automated validation

## Quick start

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File scripts/setup_backend.ps1
powershell -ExecutionPolicy Bypass -File scripts/setup_frontend.ps1
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1
```

Open http://127.0.0.1:5173

See [INSTALLATION.md](INSTALLATION.md) for full setup on Windows, macOS, and Linux.

## Tech stack

| Layer | Technology |
|-------|------------|
| API | FastAPI, Pydantic, Uvicorn |
| ORM / DB | SQLAlchemy, SQLite (WAL), Alembic |
| Parsing | python-hcl2, PyYAML |
| Reports | ReportLab (PDF) |
| UI | React 18, TypeScript, Vite, Tailwind CSS |
| Charts | Recharts |
| Tests | pytest (75 tests) |

## Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION.md](INSTALLATION.md) | Prerequisites, setup, troubleshooting |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System overview and design |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Full v2.0 approved architecture |
| [docs/API.md](docs/API.md) | REST API reference |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Implementation roadmap |
| [prompts.md](prompts.md) | AI development audit log |
| [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) | Final submission verification |

## API endpoints (summary)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Liveness |
| `POST` | `/api/v1/scans` | Create scan (202) |
| `GET` | `/api/v1/scans` | List scans |
| `GET` | `/api/v1/scans/{id}` | Scan detail |
| `GET` | `/api/v1/scans/{id}/findings` | Paginated findings |
| `GET` | `/api/v1/scans/{id}/report.pdf` | PDF report |
| `GET` | `/api/v1/dashboard/summary` | Dashboard metrics |
| `GET` | `/api/v1/rules` | Rule catalog |

Full reference: [docs/API.md](docs/API.md) · Swagger (dev): http://127.0.0.1:8000/docs

## Running tests

```bash
cd backend && python -m pytest tests/ -v
cd frontend && npm run build
```

## Repository structure

```
security-guardrail-auditor/
├── README.md                 # This file
├── INSTALLATION.md           # Setup guide
├── ARCHITECTURE.md           # Architecture summary
├── SUBMISSION_CHECKLIST.md   # Challenge verification
├── prompts.md                # AI audit log (Entries 1–11)
├── rules.md                  # Project rules
├── backend/                  # FastAPI application
│   ├── app/                  # Source code (clean architecture)
│   ├── tests/                # 75 automated tests
│   │   └── fixtures/dataset/ # 22 IaC test samples + manifest
│   ├── alembic/              # Database migrations
│   └── requirements.txt
├── frontend/                 # React + Vite UI
│   └── src/
│       ├── api/              # API client
│       ├── features/         # Pages (dashboard, upload, scans, reports)
│       ├── components/       # Shared UI (charts, tables, badges)
│       └── hooks/            # Data fetching hooks
├── docs/                     # Extended documentation
│   ├── ARCHITECTURE.md       # Full v2.0 architecture
│   ├── API.md                # API reference
│   └── ROADMAP.md            # Development plan
└── scripts/                  # Setup and dev scripts
    ├── setup_backend.ps1
    ├── setup_backend.sh
    ├── setup_frontend.ps1
    └── dev.ps1
```

## Security

- Optional API key authentication (`API_KEY` env + `X-API-Key` header)
- File upload validation (extension whitelist, size limits, UTF-8, path sanitization)
- Secret redaction in findings evidence
- Rate limiting (60 req/min/IP)
- Security headers (CSP, X-Frame-Options, HSTS in production)
- Raw file download disabled by default

## License

Submitted as an educational / challenge project. All rights reserved by the author.

## Author

Enterprise Security Guardrail Auditor — 2026
