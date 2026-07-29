@echo off
setlocal
cd /d "%~dp0"

if exist "MALPlexProvider.exe" (
  "MALPlexProvider.exe"
  goto :end
)

if exist "dist\MALPlexProvider.exe" (
  "dist\MALPlexProvider.exe"
  goto :end
)

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" "app.py"
  goto :end
)

echo Provider runtime not found.
echo Run INSTALL_AND_START.bat, or download the prebuilt Windows release.
pause
exit /b 1

:end
if errorlevel 1 pause
