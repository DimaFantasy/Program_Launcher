@echo off
rem This script automates the installation of Shortcut Creator application
chcp 866 >nul

rem Check for administrator rights
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Administrator rights required for context menu installation.
    echo Please run install.bat as administrator.
    echo Right-click on install.bat and select "Run as administrator".
    pause
    exit /b 1
)

rem Change to the installer directory
cd /d "%~dp0"

rem Check for Python
where python >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python not found. Please install Python 3.6 or higher.
    echo Download Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing Shortcut Creator...

rem Install dependencies and register context menu using Python
python setup.py install