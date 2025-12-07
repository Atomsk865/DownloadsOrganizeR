@echo off
REM Launch DownloadsOrganizeR System Tray Application
REM This script starts the system tray app with proper Python environment

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if PyQt6 is installed
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo PyQt6 not found. Installing...
    pip install PyQt6
    if errorlevel 1 (
        echo Failed to install PyQt6
        pause
        exit /b 1
    )
)

REM Start the tray application
start pythonw OrganizerTrayApp.py

REM Exit immediately (tray app runs in background)
exit
