$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host 'MAL Plex Provider installer' -ForegroundColor Cyan
Write-Host "Install folder: $root"

$exe = Join-Path $root 'MALPlexProvider.exe'
$distExe = Join-Path $root 'dist\MALPlexProvider.exe'

if (-not (Test-Path $exe) -and -not (Test-Path $distExe)) {
    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if (-not $py) {
        throw 'Python launcher was not found. Install 64-bit Python 3.12 or newer and enable Add Python to PATH, or use the prebuilt Windows release.'
    }

    if (-not (Test-Path '.venv\Scripts\python.exe')) {
        Write-Host 'Creating Python environment...'
        & py.exe -3 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Could not create Python environment.' }
    }

    Write-Host 'Installing/updating dependencies...'
    & '.venv\Scripts\python.exe' -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw 'Could not update pip.' }
    & '.venv\Scripts\python.exe' -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Could not install dependencies.' }
}

& (Join-Path $PSScriptRoot 'register-startup.ps1')

Write-Host 'Starting provider...'
Start-ScheduledTask -TaskName 'MAL Plex Metadata Provider'
Start-Sleep -Seconds 2

try {
    $health = Invoke-RestMethod -Uri 'http://127.0.0.1:4567/health' -TimeoutSec 10
    Write-Host 'Provider is running.' -ForegroundColor Green
} catch {
    Write-Warning 'The startup task was created, but the health check did not answer yet.'
    Write-Host 'Check logs\provider.log for details.'
}

Write-Host ''
Write-Host 'Plex provider URL:' -ForegroundColor Yellow
Write-Host 'http://127.0.0.1:4567/tv'
