@echo off
cd /d "%~dp0"
if not exist "logs\provider.log" (
  echo No provider log exists yet.
  pause
  exit /b 0
)
notepad "logs\provider.log"
