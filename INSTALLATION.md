# Installation Guide

Enterprise Security Guardrail Auditor — step-by-step setup for Windows, macOS, and Linux.

## Prerequisites

| Tool | Minimum version | Verify |
|------|-----------------|--------|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | 2.x | `git --version` |

Optional for production:

- Reverse proxy (nginx, Caddy) for TLS and API routing
- `API_KEY` environment variable for authentication

---

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/security-guardrail-auditor.git
cd security-guardrail-auditor
```

Replace `YOUR_USERNAME` with your GitHub username or organization.

---

## 2. Backend setup

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_backend.ps1
```

### macOS / Linux

```bash
bash scripts/setup_backend.sh
```

### Manual backend setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

The backend creates `backend/data/` on first run (SQLite database, uploads). This directory is gitignored.

### Backend environment variables

Create `backend/.env` (optional):

```env
ENV=development
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///./data/auditor.db
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]

# Production: require API key on all endpoints except health
# API_KEY=your-secret-key-here

# Disable raw IaC file download (recommended for production)
ALLOW_RAW_FILE_DOWNLOAD=false
```

---

## 3. Frontend setup

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_frontend.ps1
```

### Manual frontend setup

```bash
cd frontend
npm install
cp .env.example .env
```

### Frontend environment variables

`frontend/.env`:

```env
# Leave empty for local dev (Vite proxies /api to backend)
VITE_API_BASE_URL=

# Required when backend API_KEY is set
# VITE_API_KEY=your-secret-key-here
```

For production builds served separately from the API:

```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_API_KEY=your-secret-key-here
```

---

## 4. Run the application

### Option A — Combined dev script (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1
```

Waits for health checks, then serves:

- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173

### Option B — Two terminals

**Terminal 1 — API**

```bash
cd backend
# activate venv first
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — UI**

```bash
cd frontend
npm run dev
```

Open http://127.0.0.1:5173

---

## 5. Verify installation

### Health check

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Expected: `{"data":{"status":"ok"},...}`

### Run tests

```bash
cd backend
python -m pytest tests/ -v
```

Expected: **75 passed**

### Build frontend

```bash
cd frontend
npm run build
```

Expected: `dist/` folder created without errors.

### Smoke test — upload a sample file

```bash
curl -X POST http://127.0.0.1:8000/api/v1/scans \
  -F "files=@backend/tests/fixtures/dataset/terraform/insecure/public_s3.tf" \
  -F "label=install-test"
```

Poll `GET /api/v1/scans/{id}` until `status` is `completed`. Expect findings including `S3_PUBLIC`.

---

## 6. Production deployment (summary)

1. Set `ENV=production` and `API_KEY` on the backend.
2. Build frontend: `cd frontend && npm run build`.
3. Serve `frontend/dist/` via static hosting or nginx.
4. Proxy `/api` to uvicorn/gunicorn on port 8000.
5. Set `VITE_API_BASE_URL` at build time to your public API URL.
6. Bind API to localhost or private network; expose only through TLS-terminated proxy.
7. Disable Swagger (`/docs` is auto-disabled when `ENV=production`).

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS errors in browser | Use `http://127.0.0.1:5173` or add origin to `CORS_ORIGINS` |
| `401 Unauthorized` | Set matching `VITE_API_KEY` in frontend `.env` |
| `ModuleNotFoundError` | Activate venv; run `pip install -r requirements.txt` |
| Port 8000 in use | Change `PORT` in `.env` or stop conflicting process |
| Frontend cannot reach API in production | Set `VITE_API_BASE_URL`; configure reverse proxy |
| Scan stays `pending` | Check backend logs; ensure BackgroundTasks worker runs |

---

## Uninstall / reset

```bash
# Remove local data
rm -rf backend/data

# Remove virtual environment
rm -rf backend/.venv

# Remove node modules
rm -rf frontend/node_modules frontend/dist
```
