@echo off
setlocal ENABLEDELAYEDEXPANSION

set "INSTALL_DIR=%~dp0"
if "%INSTALL_DIR:~-1%"=="\" set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"

set "PYTHON_DIR=%INSTALL_DIR%\python"
set "ZIP_PATH=%INSTALL_DIR%\python-3.14.3.zip"

:: Detect OS Architecture
set "ARCH=win32"
if /i "%PROCESSOR_ARCHITECTURE%"=="AMD64" set "ARCH=amd64"
if /i "%PROCESSOR_ARCHITEW6432%"=="AMD64" set "ARCH=amd64"

set "PYTHON_URL=https://www.python.org/ftp/python/3.14.3/python-3.14.3-embed-%ARCH%.zip"

echo Downloading Python 3.14.3 embeddable package...
if not exist "%PYTHON_DIR%" (
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%ZIP_PATH%'"
    echo Extracting Python environment...
    powershell -Command "Expand-Archive -Path '%ZIP_PATH%' -DestinationPath '%PYTHON_DIR%' -Force"
    del "%ZIP_PATH%"
) else (
    echo Python directory already exists. Skipping download...
)

echo Setting up Scheduled Task for Auto-Run on system startup...
set "PYTHONW_PATH=%PYTHON_DIR%\pythonw.exe"
set "SCRIPT_PATH=%INSTALL_DIR%\ddns_updater.py"
set "TASK_NAME=AutoDDNS_Updater"

schtasks /create /tn "%TASK_NAME%" /tr "\"%PYTHONW_PATH%\" \"%SCRIPT_PATH%\"" /sc ONSTART /ru "SYSTEM" /rl HIGHEST /f

echo Starting the Scheduled Task '%TASK_NAME%'...
schtasks /run /tn "%TASK_NAME%"

echo Setup is complete!
echo Please edit config.json with your Namecheap DDNS domain, host, and password if you haven't already.
echo The script is now running in the background and will run automatically at the next system startup.
pause
