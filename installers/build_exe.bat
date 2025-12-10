@echo off
REM DownloadsOrganizeR - EXE Builder
REM This script builds a standalone Windows EXE with all dependencies bundled

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo DownloadsOrganizeR - Standalone EXE Builder
echo ============================================================================
echo.

REM Check Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: Python not found. Please install Python 3.9+ and add to PATH.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found!
python --version

REM Install/upgrade PyInstaller
echo.
echo Installing PyInstaller...
pip install --upgrade pyinstaller >nul 2>&1

if %errorLevel% neq 0 (
    echo Error: Failed to install PyInstaller
    pause
    exit /b 1
)

echo PyInstaller installed!

REM Run the build
echo.
echo Starting build process...
echo This may take 3-5 minutes...
echo.

python build_exe.py %*

if %errorLevel% neq 0 (
    echo.
    echo Build failed! Check error messages above.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Build completed successfully!
echo ============================================================================
echo.
echo Output location: dist\DownloadsOrganizeR\
echo.
echo Next steps:
echo 1. Navigate to dist\DownloadsOrganizeR
echo 2. Run DownloadsOrganizeR.exe
echo 3. Dashboard opens at http://localhost:5000
echo.
echo To distribute:
echo - Copy the entire 'dist\DownloadsOrganizeR' folder
echo - Run Install.bat on target machine (as Administrator for service install)
echo.
pause
