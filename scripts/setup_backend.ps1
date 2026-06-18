# Backend bootstrap — creates directory tree and installs dependencies.
# Run from repository root: powershell -ExecutionPolicy Bypass -File scripts/setup_backend.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"

Write-Host "Creating backend directory structure..."

$dirs = @(
    "app/api/middleware",
    "app/api/routes",
    "app/api/schemas",
    "app/application/dto",
    "app/domain/models",
    "app/domain/ports",
    "app/domain/rules",
    "app/domain/services",
    "app/infrastructure/database",
    "app/infrastructure/parsers",
    "app/infrastructure/repositories",
    "app/infrastructure/storage",
    "app/infrastructure/workers",
    "alembic/versions",
    "data/uploads",
    "data/reports",
    "tests/unit/parsers",
    "tests/unit/rules",
    "tests/integration",
    "tests/fixtures/terraform",
    "tests/fixtures/cloudformation",
    "tests/fixtures/invalid"
)

foreach ($dir in $dirs) {
    $path = Join-Path $Backend $dir
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}

Write-Host "Installing Python dependencies..."
Set-Location $Backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "Running Alembic migrations..."
alembic upgrade head

Write-Host "Running tests..."
python -m pytest tests/ -q

Write-Host "Backend setup complete."
Write-Host "Start API: cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
