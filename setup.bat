@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul || (
  echo Python launcher was not found.
  echo Install Python 3.12 or newer from https://www.python.org/downloads/windows/
  echo During installation, enable "Add python.exe to PATH".
  pause
  exit /b 1
)
py -3 -m venv .venv || exit /b 1
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed.
  pause
  exit /b 1
)
echo.
echo Setup complete. Run START_PROVIDER.bat next.
pause
