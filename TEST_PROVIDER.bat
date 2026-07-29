@echo off
setlocal
set URL=http://127.0.0.1:4567/tv
echo Testing %URL%
powershell -NoProfile -Command "try { (Invoke-RestMethod -Uri '%URL%' -TimeoutSec 10) | ConvertTo-Json -Depth 8 } catch { Write-Error $_; exit 1 }"
pause
