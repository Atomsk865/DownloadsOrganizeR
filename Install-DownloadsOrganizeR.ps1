<#
.SYNOPSIS
    Complete installation script for DownloadsOrganizeR
.DESCRIPTION
    Installs DownloadsOrganizeR with all dependencies, creates Windows service,
    health monitor, and desktop shortcuts. Handles Python installation if needed.
.NOTES
    Requires Administrator privileges
    Version: 1.0
    Author: DownloadsOrganizeR Team
#>

#Requires -RunAsAdministrator

[CmdletBinding()]
param(
    [Parameter()]
    [string]$InstallPath = "",
    
    [Parameter()]
    [switch]$SkipPythonCheck = $false,
    
    [Parameter()]
    [switch]$Unattended = $false
)

# Configuration
$REQUIRED_PYTHON_VERSION = "3.8"
$REPO_URL = "https://github.com/Atomsk865/DownloadsOrganizeR"
$REPO_BRANCH = "main"
$SERVICE_NAME = "DownloadsOrganizer"
$DASHBOARD_PORT = 5000

# Color output functions
function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Step {
    param([string]$Message)
    Write-Host "`n=== $Message ===`n" -ForegroundColor Magenta
}

# Banner
function Show-Banner {
    Write-Host @"

================================================================
                                                                
          DownloadsOrganizeR - Installation Wizard             
                                                                
     Automated setup for file organization service              
                                                                
================================================================

"@ -ForegroundColor Cyan
}

# Check if running as Administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Get or prompt for installation directory
function Get-InstallDirectory {
    if ($InstallPath -and (Test-Path $InstallPath -IsValid)) {
        return $InstallPath
    }
    
    if ($Unattended) {
        return "C:\Program Files\DownloadsOrganizeR"
    }
    
    Write-Info "Choose installation directory:"
    Write-Host "  1. C:\Program Files\DownloadsOrganizeR (Recommended - Industry Standard)"
    Write-Host "  2. C:\DownloadsOrganizeR (Legacy/Simple)"
    Write-Host "  3. Custom path"
    Write-Host ""
    Write-Host "Note: Option 1 uses proper Windows folder structure:"
    Write-Host "  - Program Files for application files"
    Write-Host "  - ProgramData for configuration and logs"
    
    $choice = Read-Host "Enter choice (1-3) [1]"
    
    switch ($choice) {
        "2" { return "C:\DownloadsOrganizeR" }
        "3" { 
            $custom = Read-Host "Enter full path"
            if (Test-Path $custom -IsValid) { return $custom }
            Write-Warning "Invalid path, using default"
            return "C:\Program Files\DownloadsOrganizeR"
        }
        default { return "C:\Program Files\DownloadsOrganizeR" }
    }
}

# Check Python version
function Get-PythonVersion {
    try {
        $versionOutput = & python --version 2>&1
        if ($versionOutput -match "Python (\d+\.\d+\.\d+)") {
            return $matches[1]
        }
    } catch {
        return $null
    }
    return $null
}

# Compare version strings
function Compare-Version {
    param([string]$Version1, [string]$Version2)
    $v1 = [version]$Version1
    $v2 = [version]$Version2
    return $v1.CompareTo($v2)
}

# Install Python
function Install-Python {
    param([string]$MinVersion = "3.8")
    
    Write-Step "Python Installation"
    
    $pythonVersion = Get-PythonVersion
    
    if ($pythonVersion) {
        $comparison = Compare-Version -Version1 $pythonVersion -Version2 $MinVersion
        if ($comparison -ge 0) {
            Write-Success "Python $pythonVersion is already installed (minimum: $MinVersion)"
            return $true
        }
        Write-Warning "Python $pythonVersion found, but version $MinVersion or higher required"
    } else {
        Write-Info "Python not found in PATH"
    }
    
    if ($Unattended) {
        Write-Error "Python installation required but running in unattended mode"
        return $false
    }
    
    Write-Info "Download and install Python from: https://www.python.org/downloads/"
    Write-Info "Make sure to check 'Add Python to PATH' during installation"
    
    $install = Read-Host "Open Python download page? (Y/n)"
    if ($install -ne 'n' -and $install -ne 'N') {
        Start-Process "https://www.python.org/downloads/"
    }
    
    Write-Warning "Please install Python $MinVersion or higher and run this script again"
    return $false
}

# Download repository
function Get-Repository {
    param([string]$DestPath)
    
    Write-Step "Downloading DownloadsOrganizeR"
    
    # Check if git is available
    $gitAvailable = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
    
    if ($gitAvailable) {
        Write-Info "Cloning repository using Git..."
        try {
            if (Test-Path $DestPath) {
                # Check if it's actually a git repository
                $isGitRepo = Test-Path (Join-Path $DestPath ".git")
                
                if ($isGitRepo) {
                    Write-Info "Destination exists, pulling latest changes..."
                    Push-Location $DestPath
                    & git fetch origin
                    & git checkout $REPO_BRANCH
                    & git pull origin $REPO_BRANCH
                    Pop-Location
                } else {
                    Write-Warning "Destination exists but is not a git repository. Removing and re-cloning..."
                    Remove-Item $DestPath -Recurse -Force -ErrorAction Stop
                    & git clone --branch $REPO_BRANCH $REPO_URL $DestPath
                }
            } else {
                & git clone --branch $REPO_BRANCH $REPO_URL $DestPath
            }
            
            # Create installation marker file for dynamic path detection
            $markerFile = Join-Path $DestPath ".install_path"
            $dataDir = Get-DataDirectory -InstallDir $DestPath
            
            # Write installation and data paths as JSON
            @{
                install_dir = $DestPath
                data_dir = $dataDir
                config_dir = (Join-Path $dataDir "config")
                log_dir = (Join-Path $dataDir "logs")
            } | ConvertTo-Json | Out-File -FilePath $markerFile -Encoding utf8
            
            Write-Success "Repository downloaded successfully"
            return $true
        } catch {
            Write-Warning "Git clone failed: $_"
        }
    }
    
    # Fallback to ZIP download
    Write-Info "Downloading repository as ZIP..."
    $zipPath = "$env:TEMP\DownloadsOrganizeR.zip"
    $zipUrl = "$REPO_URL/archive/refs/heads/$REPO_BRANCH.zip"
    
    try {
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
        
        # Extract ZIP
        Write-Info "Extracting files..."
        if (Test-Path $DestPath) {
            Remove-Item -Path $DestPath -Recurse -Force -ErrorAction SilentlyContinue
        }
        Expand-Archive -Path $zipPath -DestinationPath "$env:TEMP\DownloadsOrganizeR_Extract" -Force
        
        # Move extracted folder to destination
        $extractedFolder = Get-ChildItem "$env:TEMP\DownloadsOrganizeR_Extract" | Select-Object -First 1
        Move-Item -Path $extractedFolder.FullName -Destination $DestPath -Force
        
        # Cleanup
        Remove-Item $zipPath -Force
        Remove-Item "$env:TEMP\DownloadsOrganizeR_Extract" -Recurse -Force
        
        # Create installation marker file for dynamic path detection
        $markerFile = Join-Path $DestPath ".install_path"
        $DestPath | Out-File -FilePath $markerFile -Encoding utf8 -NoNewline
        
        Write-Success "Repository downloaded successfully"
        return $true
    } catch {
        Write-Error "Failed to download repository: $_"
        return $false
    }
}

# Install Python requirements
function Install-Requirements {
    param([string]$InstallDir)
    
    Write-Step "Installing Python Dependencies"
    
    $reqFile = Join-Path $InstallDir "requirements.txt"
    if (-not (Test-Path $reqFile)) {
        Write-Error "requirements.txt not found at $reqFile"
        return $false
    }
    
    Write-Info "Installing packages from requirements.txt..."
    try {
        & python -m pip install --upgrade pip
        & python -m pip install -r $reqFile
        Write-Success "All dependencies installed"
        return $true
    } catch {
        Write-Error "Failed to install requirements: $_"
        return $false
    }
}

# Install NSSM (Non-Sucking Service Manager)
function Install-NSSM {
    param([string]$InstallDir)
    
    Write-Step "Installing Service Manager (NSSM)"
    
    $nssmPath = Join-Path $InstallDir "nssm.exe"
    
    if (Test-Path $nssmPath) {
        Write-Success "NSSM already installed"
        return $nssmPath
    }
    
    Write-Info "Downloading NSSM..."
    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $zipPath = "$env:TEMP\nssm.zip"
    
    try {
        Invoke-WebRequest -Uri $nssmUrl -OutFile $zipPath -UseBasicParsing
        Expand-Archive -Path $zipPath -DestinationPath "$env:TEMP\nssm" -Force
        
        # Copy appropriate version (64-bit or 32-bit)
        $arch = if ([Environment]::Is64BitOperatingSystem) { "win64" } else { "win32" }
        $nssmExe = Get-ChildItem -Path "$env:TEMP\nssm" -Filter "nssm.exe" -Recurse | 
                   Where-Object { $_.FullName -like "*\$arch\*" } | 
                   Select-Object -First 1
        
        if ($nssmExe) {
            Copy-Item $nssmExe.FullName -Destination $nssmPath -Force
            Remove-Item $zipPath -Force
            Remove-Item "$env:TEMP\nssm" -Recurse -Force
            Write-Success "NSSM installed successfully"
            return $nssmPath
        } else {
            Write-Error "Could not find NSSM executable in download"
            return $null
        }
    } catch {
        Write-Error "Failed to install NSSM: $_"
        return $null
    }
}

# Get appropriate data directory based on installation location
function Get-DataDirectory {
    param([string]$InstallDir)
    
    # If installed in Program Files, use ProgramData (proper Windows convention)
    if ($InstallDir -like "*Program Files*") {
        return "C:\ProgramData\DownloadsOrganizeR"
    }
    
    # Otherwise use traditional approach (installation directory)
    return $InstallDir
}

# Create and install Windows service
function Install-OrganizerService {
    param(
        [string]$InstallDir,
        [string]$NssmPath
    )
    
    Write-Step "Installing Windows Service"
    
    # Stop and remove existing service
    $existingService = Get-Service -Name $SERVICE_NAME -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Info "Removing existing service..."
        & $NssmPath stop $SERVICE_NAME
        & $NssmPath remove $SERVICE_NAME confirm
        Start-Sleep -Seconds 2
    }
    
    # Determine data directory (config and logs)
    $dataDir = Get-DataDirectory -InstallDir $InstallDir
    $configDir = Join-Path $dataDir "config"
    $logDir = Join-Path $dataDir "logs"
    
    # Create directories
    if (-not (Test-Path $dataDir)) {
        Write-Info "Creating data directory: $dataDir"
        New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
    }
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    # Create/update organizer config with watch folders
    $configFile = Join-Path $configDir "organizer_config.json"
    if (-not (Test-Path $configFile)) {
        Write-Info "Creating organizer configuration..."
        $downloadsFolder = [System.IO.Path]::Combine("C:\Users", $env:USERNAME, "Downloads")
        $config = @{
            watch_folders = @($downloadsFolder)
            dashboard_user = "admin"
            password_change_required = $true
            auth_method = "basic"
            auth_fallback_enabled = $true
            routes = @{
                Images = @("jpg", "jpeg", "png", "gif", "bmp", "tiff", "svg", "webp", "heic")
                Music = @("mp3", "wav", "flac", "aac", "ogg", "wma", "m4a")
                Videos = @("mp4", "mkv", "avi", "mov", "wmv", "flv", "webm")
                Documents = @("pdf", "doc", "docx", "txt", "rtf", "odt", "xls", "xlsx", "ppt", "pptx", "csv")
                Archives = @("zip", "rar", "7z", "tar", "gz", "bz2")
                Executables = @("exe", "msi", "bat", "cmd", "ps1")
                Shortcuts = @("lnk", "url")
                Scripts = @("py", "js", "html", "css", "json", "xml", "sh", "ts", "php")
                Fonts = @("ttf", "otf", "woff", "woff2")
            }
            memory_threshold_mb = 200
            cpu_threshold_percent = 60
        }
        $config | ConvertTo-Json | Out-File -FilePath $configFile -Encoding UTF8
    }
    
    # Get Python executable path
    $pythonExe = (Get-Command python).Source
    $organizerScript = Join-Path $InstallDir "Organizer.py"
    
    Write-Info "Creating service '$SERVICE_NAME'..."
    
    # Create a batch file wrapper to handle quoting properly
    # This wrapper will be called by NSSM instead of Python directly
    $wrapperBat = Join-Path $InstallDir "run-organizer.bat"
    $batContent = @"
@echo off
REM Batch wrapper to run Organizer.py with proper quoting
cd /d "$InstallDir"
REM Set environment variables for config/data/log locations
set ORGANIZER_CONFIG_DIR=$configDir
set ORGANIZER_DATA_DIR=$dataDir
set ORGANIZER_LOG_DIR=$logDir
"$pythonExe" "$organizerScript"
"@
    $batContent | Out-File -FilePath $wrapperBat -Encoding ASCII -Force
    
    # Install service with the batch wrapper (no spaces in bat filename path issues)
    & $NssmPath install $SERVICE_NAME $wrapperBat
    
    # Verify installation by checking service exists
    $service = Get-Service -Name $SERVICE_NAME -ErrorAction SilentlyContinue
    if (-not $service) {
        Write-Error "Failed to install service"
        return $false
    }
    
    & $NssmPath set $SERVICE_NAME AppDirectory $InstallDir
    & $NssmPath set $SERVICE_NAME DisplayName "Downloads Organizer Service"
    & $NssmPath set $SERVICE_NAME Description "Automatically organizes downloaded files into categorized folders"
    & $NssmPath set $SERVICE_NAME Start SERVICE_AUTO_START
    
    # Set environment variables for the service to find data directories
    # IMPORTANT: Set all in one command - multiple set commands overwrite each other
    $envVars = "ORGANIZER_DATA_DIR=$dataDir`nORGANIZER_CONFIG_DIR=$configDir`nORGANIZER_LOG_DIR=$logDir"
    & $NssmPath set $SERVICE_NAME AppEnvironmentExtra $envVars
    
    # Configure logging
    & $NssmPath set $SERVICE_NAME AppStdout (Join-Path $logDir "organizer_stdout.log")
    & $NssmPath set $SERVICE_NAME AppStderr (Join-Path $logDir "organizer_stderr.log")
    & $NssmPath set $SERVICE_NAME AppRotateFiles 1
    & $NssmPath set $SERVICE_NAME AppRotateBytes 1048576
    
    Write-Success "Service installed successfully"
    
    # Start service
    Write-Info "Starting service..."
    try {
        & $NssmPath start $SERVICE_NAME
        Start-Sleep -Seconds 3
        
        $service = Get-Service -Name $SERVICE_NAME
        if ($service.Status -eq 'Running') {
            Write-Success "Service is running"
            return $true
        } else {
            Write-Warning "Service installed but not running. Status: $($service.Status)"
            return $false
        }
    } catch {
        Write-Error "Failed to start service: $_"
        return $false
    }
}

# Create health monitor script
function Install-HealthMonitor {
    param([string]$InstallDir)
    
    Write-Step "Installing Health Monitor"
    
    $monitorScript = @'
# Health Monitor for DownloadsOrganizer Service
# Runs every 5 minutes via Task Scheduler

$serviceName = "DownloadsOrganizer"
$logPath = "{INSTALL_DIR}\service-logs\health-monitor.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $logPath -Append
}

try {
    $service = Get-Service -Name $serviceName -ErrorAction Stop
    
    if ($service.Status -ne 'Running') {
        Write-Log "Service is $($service.Status), attempting restart..."
        Start-Service -Name $serviceName
        Start-Sleep -Seconds 5
        
        $service = Get-Service -Name $serviceName
        if ($service.Status -eq 'Running') {
            Write-Log "Service restarted successfully"
        } else {
            Write-Log "ERROR: Failed to restart service"
        }
    }
} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
}
'@
    
    $monitorScript = $monitorScript -replace '{INSTALL_DIR}', $InstallDir
    $monitorPath = Join-Path $InstallDir "Monitor-OrganizerService.ps1"
    
    $monitorScript | Out-File -FilePath $monitorPath -Encoding UTF8 -Force
    Write-Success "Health monitor script created"
    
    # Create scheduled task
    Write-Info "Creating scheduled task for health monitoring..."
    
    $taskName = "DownloadsOrganizer-HealthMonitor"
    
    # Remove existing task
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    
    # Create new task with 5-minute repeating trigger (repeats for 1 day each time it starts)
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$monitorPath`""
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
    
    Write-Success "Health monitor scheduled task created"
    return $true
}

# Create desktop shortcut for dashboard
function New-DashboardShortcut {
    param([string]$InstallDir)
    
    Write-Step "Creating Desktop Shortcut"
    
    # Create launcher script - use batch file to ensure proper env vars
    $launcherBat = Join-Path $InstallDir "Launch-Dashboard.bat"
    $batLauncher = @"
@echo off
REM Dashboard Launcher - Start OrganizerDashboard.py
cd /d "$InstallDir"
set ORGANIZER_CONFIG_DIR=$configDir
set ORGANIZER_DATA_DIR=$dataDir
set ORGANIZER_LOG_DIR=$logDir
python OrganizerDashboard.py
"@
    $batLauncher | Out-File -FilePath $launcherBat -Encoding ASCII -Force
    
    # Create launcher PowerShell wrapper that calls the batch file
    $launcherScript = @'
# Dashboard Launcher Script
$dashboardBat = "{INSTALL_DIR}\Launch-Dashboard.bat"
$dashboardUrl = "http://localhost:{PORT}"

Write-Host "Launching dashboard..." -ForegroundColor Cyan

# Start the dashboard via batch file  
Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$dashboardBat`"" -WindowStyle Hidden

# Wait for dashboard to start
$timeout = 15
$elapsed = 0
while ($elapsed -lt $timeout) {
    Start-Sleep -Seconds 1
    $elapsed++
    try {
        $response = Invoke-WebRequest -Uri $dashboardUrl -TimeoutSec 1 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200 -or $elapsed -ge 3) {
            Write-Host "Dashboard is starting at $dashboardUrl" -ForegroundColor Green
            break
        }
    } catch {
        # Still waiting for dashboard to respond
    }
}

# Open browser
Write-Host "Opening dashboard in browser..." -ForegroundColor Cyan
Start-Process $dashboardUrl
Start-Sleep -Seconds 2
'@
    
    $launcherScript = $launcherScript -replace '{INSTALL_DIR}', $InstallDir
    $launcherScript = $launcherScript -replace '{PORT}', $DASHBOARD_PORT
    $launcherPath = Join-Path $InstallDir "Launch-Dashboard.ps1"
    
    $launcherScript | Out-File -FilePath $launcherPath -Encoding UTF8 -Force
    
    # Create VBS wrapper to hide console and launch dashboard
    # Call batch file directly for better reliability
    $vbsWrapper = @"
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
strInstallDir = "$InstallDir"
strBatchFile = objFSO.BuildPath(strInstallDir, "Launch-Dashboard.bat")
objShell.Run Chr(34) & strBatchFile & Chr(34), 0, False
"@
    
    $vbsPath = Join-Path $InstallDir "Launch-Dashboard.vbs"
    $vbsWrapper | Out-File -FilePath $vbsPath -Encoding ASCII -Force
    
    # Create desktop shortcut
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktopPath "DownloadsOrganizeR Dashboard.lnk"
    
    $WshShell = New-Object -ComObject WScript.Shell
    $shortcut = $WshShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "wscript.exe"
    $shortcut.Arguments = "`"$vbsPath`""
    $shortcut.WorkingDirectory = $InstallDir
    $shortcut.Description = "Launch DownloadsOrganizeR Dashboard"
    $shortcut.IconLocation = "shell32.dll,13"
    $shortcut.Save()
    
    Write-Success "Desktop shortcut created: $shortcutPath"
    return $true
}

# Create uninstaller
function New-Uninstaller {
    param([string]$InstallDir, [string]$NssmPath)
    
    $uninstallScript = @'
# DownloadsOrganizeR Uninstaller
#Requires -RunAsAdministrator

Write-Host "DownloadsOrganizeR Uninstaller" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

$confirm = Read-Host "Are you sure you want to uninstall? (yes/no)"
if ($confirm -ne 'yes') {
    Write-Host "Uninstall cancelled" -ForegroundColor Yellow
    exit
}

$serviceName = "DownloadsOrganizer"
$taskName = "DownloadsOrganizer-HealthMonitor"
$installDir = "{INSTALL_DIR}"
$nssmPath = "{NSSM_PATH}"

# Stop and remove service
Write-Host "Removing service..." -ForegroundColor Yellow
if (Get-Service -Name $serviceName -ErrorAction SilentlyContinue) {
    & $nssmPath stop $serviceName
    & $nssmPath remove $serviceName confirm
    Write-Host "Service removed" -ForegroundColor Green
}

# Remove scheduled task
Write-Host "Removing scheduled task..." -ForegroundColor Yellow
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "Scheduled task removed" -ForegroundColor Green

# Remove desktop shortcut
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "DownloadsOrganizeR Dashboard.lnk"
if (Test-Path $shortcutPath) {
    Remove-Item $shortcutPath -Force
    Write-Host "Desktop shortcut removed" -ForegroundColor Green
}

# Ask about removing installation directory
$removeFiles = Read-Host "`nRemove all program files from $installDir ? (yes/no)"
if ($removeFiles -eq 'yes') {
    Write-Host "Removing installation directory..." -ForegroundColor Yellow
    Remove-Item $installDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Installation directory removed" -ForegroundColor Green
}

Write-Host "`nUninstall complete!" -ForegroundColor Green
Read-Host "Press Enter to exit"
'@
    
    $uninstallScript = $uninstallScript -replace '{INSTALL_DIR}', $InstallDir
    $uninstallScript = $uninstallScript -replace '{NSSM_PATH}', $NssmPath
    $uninstallPath = Join-Path $InstallDir "Uninstall.ps1"
    
    $uninstallScript | Out-File -FilePath $uninstallPath -Encoding UTF8 -Force
    Write-Success "Uninstaller created: $uninstallPath"
}

# Main installation flow
function Start-Installation {
    Show-Banner
    
    # Check administrator
    if (-not (Test-Administrator)) {
        Write-Error "This script must be run as Administrator"
        Write-Info "Right-click PowerShell and select 'Run as Administrator'"
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Get installation directory
    $installDir = Get-InstallDirectory
    Write-Info "Installation directory: $installDir"
    
    # Create installation directory
    if (-not (Test-Path $installDir)) {
        Write-Info "Creating installation directory..."
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    }
    
    # Check Python
    if (-not $SkipPythonCheck) {
        if (-not (Install-Python -MinVersion $REQUIRED_PYTHON_VERSION)) {
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
    
    # Download repository
    if (-not (Get-Repository -DestPath $installDir)) {
        Write-Error "Failed to download repository"
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Install Python requirements
    if (-not (Install-Requirements -InstallDir $installDir)) {
        Write-Error "Failed to install requirements"
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Install NSSM
    $nssmPath = Install-NSSM -InstallDir $installDir
    if (-not $nssmPath) {
        Write-Error "Failed to install NSSM"
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Install service
    if (-not (Install-OrganizerService -InstallDir $installDir -NssmPath $nssmPath)) {
        Write-Warning "Service installation encountered issues"
    }
    
    # Install health monitor
    Install-HealthMonitor -InstallDir $installDir | Out-Null
    
    # Create dashboard shortcut
    New-DashboardShortcut -InstallDir $installDir | Out-Null
    
    # Create uninstaller
    New-Uninstaller -InstallDir $installDir -NssmPath $nssmPath
    
    # Final summary
    Write-Step "Installation Complete!"
    
    Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                    Installation Summary                        ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  ✓ Installation directory: $installDir
║  ✓ Windows service installed and running                      ║
║  ✓ Health monitor active (checks every 5 minutes)             ║
║  ✓ Desktop shortcut created                                   ║
║                                                                ║
║  Dashboard URL: http://localhost:$DASHBOARD_PORT                           ║
║                                                                ║
║  To launch dashboard: Click desktop shortcut or visit URL     ║
║  To uninstall: Run Uninstall.ps1 as Administrator             ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green
    
    if (-not $Unattended) {
        $launch = Read-Host "Launch dashboard now? (Y/n)"
        if ($launch -ne 'n' -and $launch -ne 'N') {
            $launcherPath = Join-Path $installDir "Launch-Dashboard.ps1"
            Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$launcherPath`""
        }
    }
    
    Write-Host "`nThank you for installing DownloadsOrganizeR!" -ForegroundColor Cyan
}

# Execute installation
try {
    Start-Installation
} catch {
    Write-Error "Installation failed: $_"
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
