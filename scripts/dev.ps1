# Start backend and frontend dev servers with health checks
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

function Test-Command($name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        throw "Required command '$name' was not found on PATH."
    }
}

function Wait-HttpOk($url, $timeoutSec = 60) {
    $deadline = (Get-Date).AddSeconds($timeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
                return $true
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    return $false
}

Test-Command "python"
Test-Command "node"
Test-Command "npm"

if (-not (Test-Path "$root\backend\app\main.py")) {
    throw "Backend not found at $root\backend"
}
if (-not (Test-Path "$root\frontend\package.json")) {
    throw "Frontend not found at $root\frontend"
}

Write-Host "Starting Security Guardrail Auditor..." -ForegroundColor Cyan

$backendLog = Join-Path $env:TEMP "sga-backend.log"
$frontendLog = Join-Path $env:TEMP "sga-frontend.log"

$backend = Start-Process python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload" `
    -WorkingDirectory "$root\backend" -RedirectStandardOutput $backendLog -RedirectStandardError $backendLog -PassThru

if (-not (Test-Path "$root\frontend\node_modules")) {
    Push-Location "$root\frontend"
    npm install
    Pop-Location
}

$frontend = Start-Process npm -ArgumentList "run", "dev", "--", "--host", "127.0.0.1" `
    -WorkingDirectory "$root\frontend" -RedirectStandardOutput $frontendLog -RedirectStandardError $frontendLog -PassThru

if (-not (Wait-HttpOk "http://127.0.0.1:8000/api/v1/health")) {
    Stop-Process -Id $backend.Id, $frontend.Id -Force -ErrorAction SilentlyContinue
    throw "Backend failed to start. See $backendLog"
}
if (-not (Wait-HttpOk "http://127.0.0.1:5173")) {
    Stop-Process -Id $backend.Id, $frontend.Id -Force -ErrorAction SilentlyContinue
    throw "Frontend failed to start. See $frontendLog"
}

Write-Host "Backend:  http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Frontend: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host "Logs: $backendLog , $frontendLog" -ForegroundColor DarkGray
Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow

try {
    while (-not $backend.HasExited -and -not $frontend.HasExited) {
        Start-Sleep -Seconds 2
    }
    if ($backend.HasExited) { throw "Backend process exited unexpectedly." }
    if ($frontend.HasExited) { throw "Frontend process exited unexpectedly." }
} finally {
    Stop-Process -Id $backend.Id, $frontend.Id -Force -ErrorAction SilentlyContinue
}
