# Install frontend dependencies
$ErrorActionPreference = "Stop"
$frontend = Join-Path (Split-Path -Parent $PSScriptRoot) "frontend"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js is required. Install from https://nodejs.org/"
}

Set-Location $frontend
Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
npm install
Write-Host "Frontend ready. Run: cd frontend && npm run dev" -ForegroundColor Green
