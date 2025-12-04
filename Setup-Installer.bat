@echo off
setlocal ENABLEDELAYEDEXPANSION

:: DownloadsOrganizeR Setup Helper (Batch)
:: Provides a user-friendly menu to install the Windows service, run the dashboard, or uninstall.

title DownloadsOrganizeR Setup Helper
color 0A

:: Check for PowerShell
where powershell >nul 2>&1
if errorlevel 1 (
    echo PowerShell not found in PATH. Please install PowerShell 5.1+ and retry.
    pause
    exit /b 1
)

:: Detect repository directory (directory containing this batch file)
set "REPO_DIR=%~dp0"
pushd "%REPO_DIR%"

:mainmenu
cls
echo ================================================
echo   DownloadsOrganizeR - Setup and Management
echo ================================================
echo.
echo 1) Install Windows Service (Recommended)
echo 2) Run Dashboard (Local)
echo 3) Uninstall Windows Service
echo 4) Open Documentation (README)
echo 5) Exit
echo.
set /p choice=Select an option [1-5]: 

if "%choice%"=="1" goto install_service
if "%choice%"=="2" goto run_dashboard
if "%choice%"=="3" goto uninstall_service
if "%choice%"=="4" goto open_readme
if "%choice%"=="5" goto end
goto mainmenu

:install_service
cls
echo Installing DownloadsOrganizeR Windows service...
echo.
echo This will:
echo  - Install NSSM (if needed)
echo  - Copy Organizer.py to C:\Scripts
echo  - Create the 'DownloadsOrganizer' Windows service
echo  - Configure service logs in C:\Scripts\service-logs\
echo.

:: Prompt to continue
set /p CONTINUE=Proceed with installation? (Y/N): 
if /I not "%CONTINUE%"=="Y" goto mainmenu

:: Run PowerShell installer elevated if not already
:: Note: The installer handles elevation internally; we simply call it.
powershell -NoProfile -ExecutionPolicy Bypass -File "%REPO_DIR%Install-And-Monitor-OrganizerService.ps1"
if errorlevel 1 (
    echo.
    echo Installer reported an error. Check output above and try again.
    pause
    goto mainmenu
)
echo.
echo Service installation attempt completed.
pause
goto mainmenu

:run_dashboard
cls
echo Starting OrganizerDashboard locally...
echo.
set /p DASH_USER=Dashboard username [default: admin]: 
if "%DASH_USER%"=="" set DASH_USER=admin
set /p DASH_PASS=Dashboard password [default: change_this_password]: 
if "%DASH_PASS%"=="" set DASH_PASS=change_this_password

:: Ensure Python and pip are available
where python >nul 2>&1
if errorlevel 1 (
    echo Python not found in PATH. Please install Python 3.10+ and retry.
    pause
    goto mainmenu
)

:: Install dependencies
echo Installing Python dependencies...
python -m pip install -r "%REPO_DIR%requirements.txt"
if errorlevel 1 (
    echo Failed to install dependencies. Please resolve pip errors and retry.
    pause
    goto mainmenu
)

:: Launch dashboard with env vars
set "DASHBOARD_USER=%DASH_USER%"
set "DASHBOARD_PASS=%DASH_PASS%"
echo.
echo Launching dashboard on http://localhost:5000
echo (Close the window or press Ctrl+C in the new console to stop)
start "OrganizerDashboard" cmd /c "python "%REPO_DIR%OrganizerDashboard.py""
pause
goto mainmenu

:uninstall_service
cls
echo Uninstalling DownloadsOrganizer service...
echo.
echo Note: This will remove the Windows service. Files under C:\Scripts will remain.
echo You can manually delete C:\Scripts if desired.
echo.
set /p CONFIRM=Proceed with uninstall? (Y/N): 
if /I not "%CONFIRM%"=="Y" goto mainmenu

:: Attempt to remove via NSSM
powershell -NoProfile -ExecutionPolicy Bypass -Command "nssm remove DownloadsOrganizer confirm"
echo.
echo If NSSM isn't in PATH, you may need to run uninstall manually from the installer directory.
pause
goto mainmenu

:open_readme
cls
echo Opening README...
start "README" "%REPO_DIR%readme.md"
goto mainmenu

:end
popd
echo Goodbye!
endlocal
exit /b 0
