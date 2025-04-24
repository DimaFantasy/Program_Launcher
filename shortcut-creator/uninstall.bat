@echo off
setlocal

echo Removing Program Launcher context menu...

rem Set paths
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

rem Try to find Python executable
set "PYTHON_CMD="

rem Check common installation locations
if exist "C:\Users\user\AppData\Local\Programs\Python\Python313\python.exe" (
    set "PYTHON_CMD=C:\Users\user\AppData\Local\Programs\Python\Python313\python.exe"
    goto python_found
)

if exist "C:\Program Files\Python313\python.exe" (
    set "PYTHON_CMD=C:\Program Files\Python313\python.exe"
    goto python_found
)

if exist "C:\Python313\python.exe" (
    set "PYTHON_CMD=C:\Python313\python.exe"
    goto python_found
)

rem Try to find Python in PATH
set "PYTHON_CMD=python"
where %PYTHON_CMD% >nul 2>&1
if %ERRORLEVEL% EQU 0 goto python_found

set "PYTHON_CMD=python3"
where %PYTHON_CMD% >nul 2>&1
if %ERRORLEVEL% EQU 0 goto python_found

set "PYTHON_CMD=py"
where %PYTHON_CMD% >nul 2>&1
if %ERRORLEVEL% EQU 0 goto python_found

echo Python not found in standard locations.
echo Please enter the full path to python.exe:
set /p PYTHON_CMD="> "

if not exist "%PYTHON_CMD%" (
    echo Specified file does not exist: %PYTHON_CMD%
    pause
    exit /b 1
)

:python_found
echo Python found: %PYTHON_CMD%
echo Running setup.py uninstall...

"%PYTHON_CMD%" setup.py uninstall

echo.
echo Uninstallation completed.
echo.
echo IMPORTANT: You need to restart Windows Explorer for changes to take effect:
echo 1. Open Task Manager (Ctrl+Shift+Esc)
echo 2. Find "Windows Explorer" in the processes list
echo 3. Right-click on it and select "Restart"
echo.
echo After restarting Explorer, context menu entries should be completely removed.

pause