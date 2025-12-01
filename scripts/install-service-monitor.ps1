<#
.SYNOPSIS
    Install DownloadsOrganizeR as a Windows service (NSSM) or user-mode background process.

.DESCRIPTION
    This helper script automates:
    - Copying runtime files (Organizer.py, organizer_config.json, requirements.txt) to a target InstallPath.
    - Creating a Python virtual environment and installing dependencies.
    - (Service mode) Registering the service with NSSM, configuring log paths, and starting the service.
    - (User mode) Optionally creating a Scheduled Task to auto-start the organizer on logon.
    - Optionally creating a Scheduled Task to monitor the service and restart it if not running.

.PARAMETER InstallPath
    Target directory where DownloadsOrganizeR files will be installed.
    Default: C:\DownloadsOrganizeR

.PARAMETER SourcePath
    Source directory containing Organizer.py, organizer_config.json, requirements.txt.
    Defaults to the directory containing this script's parent (repository root).

.PARAMETER InstallService
    Install as a Windows service using NSSM. Requires Administrator privileges.

.PARAMETER NssmPath
    Path to nssm.exe. Required when using -InstallService.
    Example: C:\nssm\nssm.exe

.PARAMETER InstallUserMode
    Install in user-mode (no service). Runs as a background process for the current user.

.PARAMETER CreateScheduledTask
    Create a Scheduled Task. In service mode, monitors and restarts the service.
    In user mode, auto-starts the organizer on logon.

.PARAMETER ServiceName
    Name of the Windows service. Default: DownloadsOrganizer

.PARAMETER Help
    Show this help message.

.EXAMPLE
    # Install as a service (requires Administrator and NSSM)
    powershell -ExecutionPolicy Bypass -File .\scripts\install-service-monitor.ps1 -InstallPath 'C:\DownloadsOrganizeR' -InstallService -NssmPath 'C:\nssm\nssm.exe'

.EXAMPLE
    # Install user-mode with auto-start on logon
    powershell -ExecutionPolicy Bypass -File .\scripts\install-service-monitor.ps1 -InstallPath "$env:USERPROFILE\Downloads\DownloadsOrganizeR" -InstallUserMode -CreateScheduledTask

.EXAMPLE
    # Show help
    powershell -ExecutionPolicy Bypass -File .\scripts\install-service-monitor.ps1 -Help
#>

[CmdletBinding()]
param(
    [string]$InstallPath = "C:\DownloadsOrganizeR",
    [string]$SourcePath,
    [switch]$InstallService,
    [string]$NssmPath,
    [switch]$InstallUserMode,
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
    Write-Host "Use -Help to see usage examples." -ForegroundColor Yellow
    exit 1
}

if ($InstallService -and $InstallUserMode) {
    Write-Host "ERROR: Cannot use both -InstallService and -InstallUserMode. Choose one." -ForegroundColor Red
    exit 1
}

if ($InstallService -and (-not $NssmPath -or -not (Test-Path $NssmPath))) {
    Write-Host "ERROR: -InstallService requires a valid -NssmPath pointing to nssm.exe." -ForegroundColor Red
    Write-Host "Download NSSM from https://nssm.cc/ and specify the path." -ForegroundColor Yellow
    exit 1
}

# Administrator check for service mode
if ($InstallService) {
    $IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $IsAdmin) {
        Write-Host "ERROR: -InstallService requires Administrator privileges. Please run this script from an elevated PowerShell prompt." -ForegroundColor Red
        exit 1
    }
}

# Determine source path
if (-not $SourcePath) {
    # Default to parent of scripts folder (repo root)
    $SourcePath = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}

# Validate source files exist
$requiredFiles = @("Organizer.py", "organizer_config.json", "requirements.txt")
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $SourcePath $file
    if (-not (Test-Path $filePath)) {
        Write-Host "ERROR: Required file '$file' not found in source path: $SourcePath" -ForegroundColor Red
        exit 1
    }
}

# Validate Python is available
$PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) {
    Write-Host "ERROR: Python not found in PATH. Please install Python and ensure it's accessible." -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DownloadsOrganizeR Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Source Path:  $SourcePath"
Write-Host "Install Path: $InstallPath"
Write-Host "Mode:         $(if ($InstallService) { 'Windows Service' } else { 'User Mode' })"
Write-Host ""

# -------------------------
# Create Install Directory
# -------------------------
try {
    if (-not (Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        Write-Host "[OK] Created install directory: $InstallPath" -ForegroundColor Green
    } else {
        Write-Host "[OK] Install directory exists: $InstallPath" -ForegroundColor Green
    }

    # Create service-logs directory
    $LogsPath = Join-Path $InstallPath "service-logs"
    if (-not (Test-Path $LogsPath)) {
        New-Item -ItemType Directory -Path $LogsPath -Force | Out-Null
        Write-Host "[OK] Created logs directory: $LogsPath" -ForegroundColor Green
    }

    # -------------------------
    # Copy Files
    # -------------------------
    Write-Host ""
    Write-Host "Copying files..." -ForegroundColor Cyan
    foreach ($file in $requiredFiles) {
        $src = Join-Path $SourcePath $file
        $dst = Join-Path $InstallPath $file
        Copy-Item -Path $src -Destination $dst -Force
        Write-Host "[OK] Copied $file" -ForegroundColor Green
    }

    # -------------------------
    # Create Virtual Environment
    # -------------------------
    Write-Host ""
    Write-Host "Setting up Python virtual environment..." -ForegroundColor Cyan
    $VenvPath = Join-Path $InstallPath ".venv"
    if (-not (Test-Path $VenvPath)) {
        & python -m venv $VenvPath
        if ($LASTEXITCODE -ne 0) { throw "Failed to create virtual environment." }
        Write-Host "[OK] Created virtual environment: $VenvPath" -ForegroundColor Green
    } else {
        Write-Host "[OK] Virtual environment already exists: $VenvPath" -ForegroundColor Green
    }

    # Install requirements
    $PipPath = Join-Path $VenvPath "Scripts\pip.exe"
    $ReqPath = Join-Path $InstallPath "requirements.txt"
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    & $PipPath install -r $ReqPath --quiet
    if ($LASTEXITCODE -ne 0) { throw "Failed to install requirements." }
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green

    $VenvPython = Join-Path $VenvPath "Scripts\python.exe"
    $VenvPythonW = Join-Path $VenvPath "Scripts\pythonw.exe"
    $OrganizerPath = Join-Path $InstallPath "Organizer.py"

    # -------------------------
    # Service Mode Installation
    # -------------------------
    if ($InstallService) {
        Write-Host ""
        Write-Host "Installing Windows service with NSSM..." -ForegroundColor Cyan

        $StdOutLog = Join-Path $LogsPath "organizer_stdout.log"
        $StdErrLog = Join-Path $LogsPath "organizer_stderr.log"

        # Check if service already exists
        $existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($existingService) {
            Write-Host "[WARN] Service '$ServiceName' already exists. Stopping and removing..." -ForegroundColor Yellow
            & $NssmPath stop $ServiceName 2>$null
            & $NssmPath remove $ServiceName confirm
        }

        # Install service
        & $NssmPath install $ServiceName $VenvPython "`"$OrganizerPath`""
        if ($LASTEXITCODE -ne 0) { throw "Failed to install service with NSSM." }

        & $NssmPath set $ServiceName AppDirectory $InstallPath
        & $NssmPath set $ServiceName AppStdout $StdOutLog
        & $NssmPath set $ServiceName AppStderr $StdErrLog
        & $NssmPath set $ServiceName Description "Organizes Downloads folder in real-time using DownloadsOrganizeR"
        & $NssmPath set $ServiceName Start SERVICE_AUTO_START

        # Start service
        & $NssmPath start $ServiceName
        Write-Host "[OK] Service '$ServiceName' installed and started" -ForegroundColor Green

        # -------------------------
        # Service Monitor Scheduled Task
        # -------------------------
        if ($CreateScheduledTask) {
            Write-Host ""
            Write-Host "Creating service monitor Scheduled Task..." -ForegroundColor Cyan
            $TaskName = "${ServiceName}_Monitor"

            # Remove existing task if present
            $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($existingTask) {
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            }

            # Create a simple monitor script in the install path
            $MonitorScript = @"
`$service = Get-Service -Name '$ServiceName' -ErrorAction SilentlyContinue
if (`$service -and `$service.Status -ne 'Running') {
    Start-Service -Name '$ServiceName'
    Add-Content -Path '$LogsPath\monitor.log' -Value "[`$(Get-Date)] Service was not running. Restarted."
}
"@
            $MonitorScriptPath = Join-Path $InstallPath "Monitor-Service.ps1"
            Set-Content -Path $MonitorScriptPath -Value $MonitorScript -Encoding UTF8

            # Create scheduled task
            $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$MonitorScriptPath`""
            $Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
            $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
            Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Monitors $ServiceName and restarts if not running" -RunLevel Highest | Out-Null

            Write-Host "[OK] Scheduled Task '$TaskName' created (runs every 5 minutes)" -ForegroundColor Green
        }
    }

    # -------------------------
    # User Mode Installation
    # -------------------------
    if ($InstallUserMode) {
        Write-Host ""
        Write-Host "User-mode installation complete." -ForegroundColor Cyan
        Write-Host "To start the organizer in the background, run:" -ForegroundColor Yellow
        Write-Host "  Start-Process -FilePath `"$VenvPythonW`" -ArgumentList `"$OrganizerPath`" -WindowStyle Hidden" -ForegroundColor White

        if ($CreateScheduledTask) {
            Write-Host ""
            Write-Host "Creating auto-start Scheduled Task..." -ForegroundColor Cyan
            $TaskName = "${ServiceName}_UserMode"

            # Remove existing task if present
            $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($existingTask) {
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            }

            # Create scheduled task for logon
            $Action = New-ScheduledTaskAction -Execute $VenvPythonW -Argument "`"$OrganizerPath`""
            $Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
            $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
            Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Starts DownloadsOrganizeR on user logon" | Out-Null

            Write-Host "[OK] Scheduled Task '$TaskName' created (starts on logon)" -ForegroundColor Green
        }

        # Start the organizer now
        Write-Host ""
        Write-Host "Starting organizer now..." -ForegroundColor Cyan
        Start-Process -FilePath $VenvPythonW -ArgumentList "`"$OrganizerPath`"" -WindowStyle Hidden
        Write-Host "[OK] Organizer started in background" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Installation completed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green

    if ($InstallService) {
        Write-Host ""
        Write-Host "Service Status:" -ForegroundColor Cyan
        Get-Service -Name $ServiceName | Format-Table Name, Status, StartType -AutoSize
        Write-Host "Log files: $LogsPath" -ForegroundColor Yellow
    }

} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Installation failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
