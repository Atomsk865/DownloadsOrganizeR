@echo off
REM DownloadsOrganizeR Quick Installer
REM Run this file as Administrator to install

echo.
echo ============================================================
echo     DownloadsOrganizeR - Quick Install
echo ============================================================
echo.
echo This will install DownloadsOrganizeR on your system.
echo.
echo Requirements:
echo   - Administrator privileges (right-click and "Run as Administrator")
echo   - Internet connection
echo   - Windows 10/11 or Windows Server 2016+
echo.
echo Installation will:
echo   - Check/Install Python 3.8+
echo   - Download latest version from GitHub
echo   - Install Windows service
echo   - Create desktop shortcut
echo   - Set up automatic health monitoring
echo.
pause
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Running PowerShell installer...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-DownloadsOrganizeR.ps1"

echo.
echo Installation script completed.
echo.
pause
