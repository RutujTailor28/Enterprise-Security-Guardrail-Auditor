#!/usr/bin/env bash
# Backend bootstrap — run from repository root: bash scripts/setup_backend.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"

echo "Creating backend directory structure..."
DIRS=(
  app/api/middleware app/api/routes app/api/schemas
  app/application/dto app/domain/models app/domain/ports
  app/domain/rules app/domain/services
  app/infrastructure/database app/infrastructure/parsers
  app/infrastructure/repositories app/infrastructure/storage
  app/infrastructure/workers
  alembic/versions data/uploads data/reports
  tests/unit/parsers tests/unit/rules tests/integration
  tests/fixtures/terraform tests/fixtures/cloudformation tests/fixtures/invalid
)
for dir in "${DIRS[@]}"; do
  mkdir -p "$BACKEND/$dir"
done

echo "Installing Python dependencies..."
cd "$BACKEND"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Running Alembic migrations..."
alembic upgrade head

echo "Running tests..."
python -m pytest tests/ -q

echo "Backend setup complete."
echo "Start API: cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
