@echo off
echo Installing Program Launcher context menu...

set PYTHON_FOUND=no

REM Try python command
python --version >nul 2>&1
if not errorlevel 1 (
    echo Python found as 'python'
    set PYTHON_FOUND=yes
    python setup.py install
    if errorlevel 1 (
        echo WARNING: Context menu installation failed. Try running as administrator.
    ) else (
        echo.
        echo Context menu installation completed successfully.
        echo.
        echo IMPORTANT: You need to restart Windows Explorer to see the changes:
        echo 1. Open Task Manager (Ctrl+Shift+Esc)
        echo 2. Find "Windows Explorer" in the processes list
        echo 3. Right-click on it and select "Restart"
        echo.
        echo After restarting Explorer, right-click on any folder or inside any folder
        echo to see the "Create Program Launcher shortcut" menu option.
    )
    goto :end
)

REM Try python3 command
python3 --version >nul 2>&1
if not errorlevel 1 (
    echo Python found as 'python3'
    set PYTHON_FOUND=yes
    python3 setup.py install
    if errorlevel 1 (
        echo WARNING: Context menu installation failed. Try running as administrator.
    ) else (
        echo.
        echo Context menu installation completed successfully.
        echo.
        echo IMPORTANT: You need to restart Windows Explorer to see the changes:
        echo 1. Open Task Manager (Ctrl+Shift+Esc)
        echo 2. Find "Windows Explorer" in the processes list
        echo 3. Right-click on it and select "Restart"
        echo.
        echo After restarting Explorer, right-click on any folder or inside any folder
        echo to see the "Create Program Launcher shortcut" menu option.
    )
    goto :end
)

REM Try py command
py --version >nul 2>&1
if not errorlevel 1 (
    echo Python found as 'py'
    set PYTHON_FOUND=yes
    py setup.py install
    if errorlevel 1 (
        echo WARNING: Context menu installation failed. Try running as administrator.
    ) else (
        echo.
        echo Context menu installation completed successfully.
        echo.
        echo IMPORTANT: You need to restart Windows Explorer to see the changes:
        echo 1. Open Task Manager (Ctrl+Shift+Esc)
        echo 2. Find "Windows Explorer" in the processes list
        echo 3. Right-click on it and select "Restart"
        echo.
        echo After restarting Explorer, right-click on any folder or inside any folder
        echo to see the "Create Program Launcher shortcut" menu option.
    )
    goto :end
)

if "%PYTHON_FOUND%"=="no" (
    echo Python not found. Please install Python 3.x and try again.
)

:end
pause