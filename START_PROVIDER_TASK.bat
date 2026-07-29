@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Start-ScheduledTask -TaskName 'MAL Plex Metadata Provider'; Write-Host 'Start requested.'"
pause
