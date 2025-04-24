@echo off

rem This script automates the installation of Shortcut Creator application

rem Change to the installer directory
cd /d "%~dp0"

echo Checking for Python installation...

rem Try common Python executable names
set PYTHON_FOUND=0

rem Try 'python' command
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found Python with 'python' command
    set PYTHON_CMD=python
    set PYTHON_FOUND=1
    goto PYTHON_FOUND
)

rem Try 'python3' command
python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found Python with 'python3' command
    set PYTHON_CMD=python3
    set PYTHON_FOUND=1
    goto PYTHON_FOUND
)

rem Try 'py' command
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found Python with 'py' command
    set PYTHON_CMD=py
    set PYTHON_FOUND=1
    goto PYTHON_FOUND
)

rem Try looking for Python in standard install locations
if exist "C:\Program Files\Python*\python.exe" (
    for /d %%i in ("C:\Program Files\Python*") do (
        if exist "%%i\python.exe" (
            echo Found Python at %%i\python.exe
            set PYTHON_CMD="%%i\python.exe"
            set PYTHON_FOUND=1
            goto PYTHON_FOUND
        )
    )
)

if exist "C:\Python*\python.exe" (
    for /d %%i in ("C:\Python*") do (
        if exist "%%i\python.exe" (
            echo Found Python at %%i\python.exe
            set PYTHON_CMD="%%i\python.exe"
            set PYTHON_FOUND=1
            goto PYTHON_FOUND
        )
    )
)

if %PYTHON_FOUND% EQU 0 (
    echo Python not found. Please install Python 3.6 or higher.
    echo Download Python from: https://www.python.org/downloads/
    echo Or add your Python installation to the PATH environment variable.
    pause
    exit /b 1
)

:PYTHON_FOUND
echo Installing Shortcut Creator...

rem Install dependencies and register context menu using Python
%PYTHON_CMD% setup.py install

echo Installation complete!
pause