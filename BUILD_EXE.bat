@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Run setup.bat first.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m pip install --upgrade pyinstaller
if errorlevel 1 goto :fail
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --name MALPlexProvider --collect-all flask --collect-all waitress app.py
if errorlevel 1 goto :fail
copy /Y config.json dist\config.json >nul
copy /Y settings.json dist\settings.json >nul
copy /Y RUN_PROVIDER.bat dist\RUN_PROVIDER.bat >nul
copy /Y RUN_PROVIDER_BACKGROUND.cmd dist\RUN_PROVIDER_BACKGROUND.cmd >nul
copy /Y EDIT_SETTINGS.bat dist\EDIT_SETTINGS.bat >nul
copy /Y TEST_PROVIDER.bat dist\TEST_PROVIDER.bat >nul
copy /Y REGISTER_STARTUP.bat dist\REGISTER_STARTUP.bat >nul
copy /Y UNREGISTER_STARTUP.bat dist\UNREGISTER_STARTUP.bat >nul
xcopy /E /I /Y scripts dist\scripts >nul

echo.
echo Built: dist\MALPlexProvider.exe
echo settings.json and startup helpers were copied beside it.
pause
exit /b 0
:fail
echo EXE build failed.
pause
exit /b 1
