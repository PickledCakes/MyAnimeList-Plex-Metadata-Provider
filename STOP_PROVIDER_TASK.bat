@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Stop-ScheduledTask -TaskName 'MAL Plex Metadata Provider'; Write-Host 'Provider task stopped.'"
pause
