@echo off
rem This script automates the uninstallation of Shortcut Creator application
chcp 866 >nul

rem Check for administrator rights
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Administrator rights required for context menu removal.
    echo Please run uninstall.bat as administrator.
    echo Right-click on uninstall.bat and select "Run as administrator".
    pause
    exit /b 1
)

rem Change to the installer directory
cd /d "%~dp0"

echo Uninstalling Shortcut Creator...

rem Run Python script for cleanup
python setup.py uninstall

echo.
echo Uninstallation complete. The context menu has been removed.
echo If menu item is still visible, restart Explorer or reboot your computer.

pause