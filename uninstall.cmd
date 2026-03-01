@echo off
setlocal

set "TASK_NAME=AutoDDNS_Updater"

echo Checking for existing scheduled task: %TASK_NAME%...
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo Task found. Unregistering task...
    schtasks /delete /tn "%TASK_NAME%" /f
    echo Task '%TASK_NAME%' has been successfully unregistered.
) else (
    echo Task '%TASK_NAME%' not found. Nothing to unregister.
)

set "INSTALL_DIR=%~dp0"
if "%INSTALL_DIR:~-1%"=="\" set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"
set "SCRIPT_PATH=%INSTALL_DIR%\ddns_updater.py"

echo Checking for running Python processes related to the DDNS Updater...
powershell -Command "$ScriptPath = '%SCRIPT_PATH%'; $processes = Get-WmiObject Win32_Process -Filter \"name='pythonw.exe' or name='python.exe'\" | Where-Object { $_.CommandLine -match [regex]::Escape($ScriptPath) }; if ($processes) { foreach ($process in $processes) { Write-Host \"Stopping process with ID: $($process.ProcessId)\"; Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue }; Write-Host \"All related processes have been stopped.\" } else { Write-Host \"No running DDNS Updater processes found.\" }"

echo Uninstall complete.
pause
