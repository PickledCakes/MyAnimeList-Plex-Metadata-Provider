@echo off
setlocal
cd /d "%~dp0"
if not exist "logs" mkdir "logs"

if exist "MALPlexProvider.exe" (
  "MALPlexProvider.exe" >> "logs\provider.log" 2>&1
  exit /b %errorlevel%
)

if exist "dist\MALPlexProvider.exe" (
  "dist\MALPlexProvider.exe" >> "logs\provider.log" 2>&1
  exit /b %errorlevel%
)

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" "app.py" >> "logs\provider.log" 2>&1
  exit /b %errorlevel%
)

echo [%date% %time%] Provider runtime not found. >> "logs\provider.log"
exit /b 1
