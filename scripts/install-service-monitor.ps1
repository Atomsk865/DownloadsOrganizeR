<#
.SYNOPSIS
    CLI helper script to install DownloadsOrganizeR as a Windows service or user-mode background process.

.DESCRIPTION
    This script automates the installation of DownloadsOrganizeR by:
    - Copying minimal runtime files (Organizer.py, organizer_config.json, requirements.txt)
    - Creating a Python virtual environment and installing dependencies
    - Optionally registering a Windows service using NSSM (requires Administrator)
    - Optionally creating a Scheduled Task to monitor/autostart the service or user-mode process

.PARAMETER InstallPath
    Target directory for installation. Default: C:\DownloadsOrganizeR

.PARAMETER SourcePath
    Path to the repository root containing Organizer.py, organizer_config.json, and requirements.txt.
    Default: current directory ($PWD)

.PARAMETER InstallService
    Install as a Windows service using NSSM (requires Administrator privileges).

.PARAMETER InstallUserMode
    Install for user-mode background execution (no service, no admin required).

.PARAMETER NssmPath
    Path to nssm.exe. Required if -InstallService is specified. Default: C:\nssm\nssm.exe

.PARAMETER CreateScheduledTask
    Create a Scheduled Task that monitors and restarts the service/process if not running (5-minute interval).

.PARAMETER ServiceName
    Name of the Windows service. Default: DownloadsOrganizer

.PARAMETER Help
    Display this help message.

.EXAMPLE
    # Install as a service (requires admin and NSSM)
    powershell -ExecutionPolicy Bypass -File .\scripts\install-service-monitor.ps1 -InstallPath 'C:\DownloadsOrganizeR' -InstallService -NssmPath 'C:\nssm\nssm.exe'

.EXAMPLE
    # Install user-mode with scheduled task autostart
    powershell -ExecutionPolicy Bypass -File .\scripts\install-service-monitor.ps1 -InstallPath "$env:USERPROFILE\Downloads\DownloadsOrganizeR" -InstallUserMode -CreateScheduledTask

.NOTES
    Author: DownloadsOrganizeR
    Requires: Python 3.7+, NSSM (for service mode)
#>

[CmdletBinding()]
param(
    [string]$InstallPath = "C:\DownloadsOrganizeR",
    [string]$SourcePath = $PWD,
    [switch]$InstallService,
    [switch]$InstallUserMode,
    [string]$NssmPath = "C:\nssm\nssm.exe",
    [switch]$CreateScheduledTask,
    [string]$ServiceName = "DownloadsOrganizer",
    [switch]$Help
)

# -------------------------
# Help
# -------------------------
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Detailed
    exit 0
}

# -------------------------
# Validation
# -------------------------
if (-not $InstallService -and -not $InstallUserMode) {
    Write-Host "ERROR: You must specify either -InstallService or -InstallUserMode." -ForegroundColor Red
    Write-Host "Use -Help for usage information." -ForegroundColor Yellow
    exit 1
}

if ($InstallService -and $InstallUserMode) {
    Write-Host "ERROR: Cannot specify both -InstallService and -InstallUserMode. Choose one." -ForegroundColor Red
    exit 1
}

if ($InstallService) {
    $IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $IsAdmin) {
        Write-Host "ERROR: -InstallService requires Administrator privileges. Please run from an elevated PowerShell prompt." -ForegroundColor Red
        exit 1
    }
    if (-not (Test-Path $NssmPath)) {
        Write-Host "ERROR: NSSM not found at '$NssmPath'. Please provide a valid -NssmPath or install NSSM from https://nssm.cc/" -ForegroundColor Red
        exit 1
    }
}

# Check source files exist
$RequiredFiles = @("Organizer.py", "organizer_config.json", "requirements.txt")
foreach ($file in $RequiredFiles) {
    $filePath = Join-Path $SourcePath $file
    if (-not (Test-Path $filePath)) {
        Write-Host "ERROR: Required file '$file' not found in source path '$SourcePath'." -ForegroundColor Red
        exit 1
    }
}

# Check Python is available
$PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) {
    Write-Host "ERROR: Python not found in PATH. Please install Python 3.7+ and ensure it's accessible." -ForegroundColor Red
    exit 1
}
Write-Host "Found Python: $PythonPath" -ForegroundColor Green

# -------------------------
# Create Install Directory
# -------------------------
Write-Host "`n==> Creating install directory: $InstallPath" -ForegroundColor Cyan
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
}

# -------------------------
# Copy Files
# -------------------------
Write-Host "==> Copying runtime files..." -ForegroundColor Cyan
foreach ($file in $RequiredFiles) {
    $src = Join-Path $SourcePath $file
    $dst = Join-Path $InstallPath $file
    Copy-Item -Path $src -Destination $dst -Force
    Write-Host "  Copied: $file" -ForegroundColor Gray
}

# Create service-logs directory
$LogsDir = Join-Path $InstallPath "service-logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
    Write-Host "  Created: service-logs\" -ForegroundColor Gray
}

# -------------------------
# Create Virtual Environment
# -------------------------
$VenvPath = Join-Path $InstallPath ".venv"
Write-Host "`n==> Creating Python virtual environment at $VenvPath..." -ForegroundColor Cyan

if (-not (Test-Path $VenvPath)) {
    & python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
}
Write-Host "  Virtual environment ready." -ForegroundColor Gray

# Install requirements
$VenvPip = Join-Path $VenvPath "Scripts\pip.exe"
$RequirementsFile = Join-Path $InstallPath "requirements.txt"
Write-Host "==> Installing Python dependencies..." -ForegroundColor Cyan
& $VenvPip install -r $RequirementsFile --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install requirements." -ForegroundColor Red
    exit 1
}
Write-Host "  Dependencies installed." -ForegroundColor Gray

# -------------------------
# Service Mode Installation
# -------------------------
if ($InstallService) {
    Write-Host "`n==> Installing Windows service '$ServiceName' using NSSM..." -ForegroundColor Cyan
    
    $VenvPython = Join-Path $VenvPath "Scripts\python.exe"
    $OrganizerScript = Join-Path $InstallPath "Organizer.py"
    $StdOutLog = Join-Path $LogsDir "organizer_stdout.log"
    $StdErrLog = Join-Path $LogsDir "organizer_stderr.log"

    # Check if service already exists
    $existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Host "  Service '$ServiceName' already exists. Stopping and removing..." -ForegroundColor Yellow
        & $NssmPath stop $ServiceName 2>$null
        & $NssmPath remove $ServiceName confirm 2>$null
    }

    # Install service
    & $NssmPath install $ServiceName $VenvPython "`"$OrganizerScript`""
    & $NssmPath set $ServiceName AppDirectory $InstallPath
    & $NssmPath set $ServiceName AppStdout $StdOutLog
    & $NssmPath set $ServiceName AppStderr $StdErrLog
    & $NssmPath set $ServiceName Description "DownloadsOrganizeR - Automatically organizes Downloads folder by file type"
    & $NssmPath set $ServiceName Start SERVICE_AUTO_START

    # Start service
    & $NssmPath start $ServiceName
    Write-Host "  Service '$ServiceName' installed and started." -ForegroundColor Green
}

# -------------------------
# User Mode Installation
# -------------------------
if ($InstallUserMode) {
    Write-Host "`n==> User-mode installation complete." -ForegroundColor Cyan
    $VenvPythonW = Join-Path $VenvPath "Scripts\pythonw.exe"
    $OrganizerScript = Join-Path $InstallPath "Organizer.py"
    
    Write-Host "  To run in background (no console window):" -ForegroundColor Gray
    Write-Host "    Start-Process -FilePath `"$VenvPythonW`" -ArgumentList `"$OrganizerScript`" -WindowStyle Hidden" -ForegroundColor White
    Write-Host ""
    Write-Host "  To stop:" -ForegroundColor Gray
    Write-Host "    Get-Process -Name pythonw | Stop-Process" -ForegroundColor White
}

# -------------------------
# Scheduled Task (Optional)
# -------------------------
if ($CreateScheduledTask) {
    Write-Host "`n==> Creating Scheduled Task for monitoring..." -ForegroundColor Cyan
    
    $TaskName = "DownloadsOrganizeR_Monitor"
    $VenvPython = Join-Path $VenvPath "Scripts\python.exe"
    $VenvPythonW = Join-Path $VenvPath "Scripts\pythonw.exe"
    $OrganizerScript = Join-Path $InstallPath "Organizer.py"

    # Remove existing task if present
    $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "  Removed existing task '$TaskName'." -ForegroundColor Yellow
    }

    if ($InstallService) {
        # For service mode: create a task that checks and restarts the service
        $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -Command `"if ((Get-Service -Name '$ServiceName' -ErrorAction SilentlyContinue).Status -ne 'Running') { Start-Service -Name '$ServiceName' }`""
    } else {
        # For user mode: create a task that checks if process is running before starting
        $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -Command `"if (-not (Get-Process -Name pythonw -ErrorAction SilentlyContinue | Where-Object { `$_.CommandLine -like '*Organizer.py*' })) { Start-Process -FilePath '$VenvPythonW' -ArgumentList '`"$OrganizerScript`"' -WindowStyle Hidden }`""
    }

    $Trigger = New-ScheduledTaskTrigger -AtLogon
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

    # Add repetition for monitoring (every 5 minutes)
    $Trigger.Repetition = (New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)).Repetition

    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description "Monitors and restarts DownloadsOrganizeR if not running" | Out-Null
    
    Write-Host "  Scheduled Task '$TaskName' created (runs at logon, checks every 5 minutes)." -ForegroundColor Green
}

# -------------------------
# Summary
# -------------------------
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Install Path: $InstallPath"
Write-Host "Venv Path:    $VenvPath"
Write-Host "Logs Dir:     $LogsDir"
if ($InstallService) {
    Write-Host "Service:      $ServiceName (running)"
}
if ($CreateScheduledTask) {
    Write-Host "Sched. Task:  DownloadsOrganizeR_Monitor"
}
Write-Host ""
