@echo off
cd /d "%~dp0"
where pythonw >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw "%~dp0action_bar.pyw"
    exit /b 0
)
where pyw >nul 2>&1
if %errorlevel%==0 (
    start "" pyw -3 "%~dp0action_bar.pyw"
    exit /b 0
)
echo Python 3 was not found. Install it and tick "Add python.exe to PATH".
pause
