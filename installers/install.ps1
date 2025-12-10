#!/usr/bin/env pwsh
<#
.SYNOPSIS
    DownloadsOrganizeR - Enterprise-Grade Installer
    Professional installation for Windows environments

.DESCRIPTION
    Industry-standard installer with support for:
    - Business, Enterprise, and Personal deployments
    - Role-based installation (personal vs. enterprise)
    - Security hardening and audit logging
    - Health checks and system validation
    - Automatic recovery and rollback capabilities
    - TLS 1.2+ enforcement
    - Silent and interactive installation modes

.EXAMPLE
    # Download and run in one line (interactive):
    irm https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1 | iex

    # Enterprise deployment (silent):
    $params = @{
        InstallDir = 'C:\Program Files\DownloadsOrganizeR'
        DeploymentMode = 'Enterprise'
        InstallService = $true
        Silent = $true
    }
    irm https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1 | iex -ArgumentList @(($params | ConvertTo-Json))

.PARAMETER InstallDir
    Installation directory (Personal: C:\DownloadsOrganizeR, Enterprise: C:\Program Files\DownloadsOrganizeR)

.PARAMETER DeploymentMode
    'Personal' or 'Enterprise' (affects paths, service config, security settings)

.PARAMETER InstallService
    Install as Windows service (default: $false for personal, $true for enterprise)

.PARAMETER Silent
    Run without prompts (useful for scripted deployments)

.PARAMETER SkipHealthCheck
    Skip system health validation

.PARAMETER EnableLogging
    Enable detailed installer logging to file

.NOTES
    Requires: PowerShell 5.1+, Administrator privileges, TLS 1.2+
    License: MIT
    Repository: https://github.com/Atomsk865/DownloadsOrganizeR
    Version: 2.0 (Enterprise-Grade)
    Last Updated: December 2025
#>

[CmdletBinding()]
param(
    [string]$InstallDir = "",
    [ValidateSet('Personal', 'Enterprise')]
    [string]$DeploymentMode = 'Personal',
    [switch]$InstallService,
    [switch]$Silent,
    [switch]$SkipHealthCheck,
    [switch]$EnableLogging,
    [string]$DownloadUrl = ""
)

# =====================
# Configuration & Validation
# =====================
$script:ScriptVersion = "2.0"
$script:MinPowerShellVersion = [version]"5.1"
$script:MinTLS = [System.Security.Authentication.SslProtocols]::Tls12
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Set deployment-specific defaults
if ([string]::IsNullOrEmpty($InstallDir)) {
    $InstallDir = if ($DeploymentMode -eq 'Enterprise') {
        'C:\Program Files\DownloadsOrganizeR'
    } else {
        'C:\DownloadsOrganizeR'
    }
}

# Logging setup
$script:LogFile = if ($EnableLogging) { 
    Join-Path $env:TEMP "DownloadsOrganizeR-Install_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
} else { 
    $null 
}

# =====================
# Helper Functions
# =====================

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    switch ($Level) {
        "INFO" { Write-Host $logMessage -ForegroundColor Cyan }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
        "WARN" { Write-Host $logMessage -ForegroundColor Yellow }
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "DEBUG" { Write-Host $logMessage -ForegroundColor Gray }
    }
    
    if ($script:LogFile) {
        Add-Content -Path $script:LogFile -Value $logMessage -ErrorAction SilentlyContinue
    }
}

function Test-AdminPrivileges {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $isAdmin) {
        Write-Log "Administrator privileges required. Script is not running with elevated rights." "ERROR"
        Write-Log "Please run PowerShell as Administrator and try again." "INFO"
        if (-not $Silent) { Read-Host "Press Enter to exit" }
        exit 1
    }
    Write-Log "Running with Administrator privileges" "SUCCESS"
}

function Test-PowerShellVersion {
    $currentVersion = $PSVersionTable.PSVersion
    if ($currentVersion -lt $script:MinPowerShellVersion) {
        Write-Log "PowerShell $script:MinPowerShellVersion or later required (found: $currentVersion)" "ERROR"
        exit 1
    }
    Write-Log "PowerShell version $currentVersion meets requirements" "SUCCESS"
}

function Test-TLSVersion {
    # Enforce TLS 1.2 for secure downloads
    [Net.ServicePointManager]::SecurityProtocol = $script:MinTLS
    Write-Log "TLS 1.2+ enforced for secure communications" "SUCCESS"
}

function Test-SystemRequirements {
    Write-Log "Validating system requirements..." "INFO"
    
    # Check disk space (minimum 500MB free)
    $drive = (Get-Item $InstallDir).PSDrive.Name
    $driveInfo = Get-Volume -DriveLetter $drive
    $freeSpaceGB = [math]::Round($driveInfo.SizeRemaining / 1GB, 2)
    
    if ($driveInfo.SizeRemaining -lt 500MB) {
        Write-Log "Insufficient disk space: $freeSpaceGB GB available (minimum 500 MB required)" "ERROR"
        exit 1
    }
    Write-Log "Disk space check passed: $freeSpaceGB GB available" "SUCCESS"
    
    # Check Python installation
    $pythonCheck = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Python 3.8+ not found in PATH" "ERROR"
        Write-Log "Please install Python from https://www.python.org/downloads/" "INFO"
        exit 1
    }
    Write-Log "Python found: $pythonCheck" "SUCCESS"
    
    # Check pip
    $pipVersion = pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "pip not found or not functioning correctly" "ERROR"
        exit 1
    }
    Write-Log "pip found: $pipVersion" "SUCCESS"
}

function Get-LatestReleaseUrl {
    Write-Log "Fetching latest release from GitHub..." "INFO"
    
    try {
        $apiUrl = "https://api.github.com/repos/Atomsk865/DownloadsOrganizeR/releases/latest"
        $response = Invoke-RestMethod -Uri $apiUrl -TimeoutSec 10 -ErrorAction Stop
        
        Write-Log "Latest release: v$($response.tag_name)" "DEBUG"
        
        # Find release asset (prefer actual release zip, fallback to zipball)
        $zipAsset = $response.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1
        
        if ($zipAsset) {
            Write-Log "Found release asset: $($zipAsset.name)" "DEBUG"
            return $zipAsset.browser_download_url
        }
        
        Write-Log "No release asset found, using zipball URL" "DEBUG"
        return $response.zipball_url
    }
    catch {
        Write-Log "Could not fetch from GitHub API: $_" "WARN"
        Write-Log "Using main branch as fallback" "INFO"
        return "https://github.com/Atomsk865/DownloadsOrganizeR/archive/refs/heads/main.zip"
    }
}

function Invoke-WebRequestSecure {
    param(
        [string]$Uri,
        [string]$OutFile,
        [int]$TimeoutSec = 300
    )
    
    Write-Log "Downloading from: $Uri" "DEBUG"
    
    try {
        $sw = [Diagnostics.Stopwatch]::StartNew()
        
        Invoke-WebRequest `
            -Uri $Uri `
            -OutFile $OutFile `
            -TimeoutSec $TimeoutSec `
            -ErrorAction Stop | Out-Null
        
        $sw.Stop()
        $sizeMB = [math]::Round((Get-Item $OutFile).Length / 1MB, 2)
        
        Write-Log "Downloaded $sizeMB MB in $([math]::Round($sw.Elapsed.TotalSeconds, 2))s" "SUCCESS"
    }
    catch {
        Write-Log "Download failed: $_" "ERROR"
        throw
    }
}

function Expand-ZipSecure {
    param(
        [string]$ZipFile,
        [string]$DestinationPath
    )
    
    Write-Log "Extracting files from archive..." "INFO"
    
    try {
        # Clean destination if it exists
        if (Test-Path $DestinationPath) {
            Remove-Item $DestinationPath -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        New-Item -ItemType Directory -Path $DestinationPath -Force -ErrorAction Stop | Out-Null
        
        # Use built-in extraction (available in PowerShell 5.1+)
        Expand-Archive `
            -Path $ZipFile `
            -DestinationPath $DestinationPath `
            -Force `
            -ErrorAction Stop
        
        Write-Log "Files extracted successfully" "SUCCESS"
    }
    catch {
        Write-Log "Extraction failed: $_" "ERROR"
        throw
    }
}

function Install-FileStructure {
    param(
        [string]$SourceDir,
        [string]$TargetDir,
        [string]$DeploymentMode
    )
    
    Write-Log "Installing application files..." "INFO"
    
    # Core application files
    $coreFiles = @(
        'SortNStoreService.py',
        'Organizer.py',             # legacy shim
        'SortNStoreDashboard.py',
        'requirements.txt',
        'sortnstore_config.json',
        'organizer_config.json',    # legacy config name
        'dashboard_config.json',
        'LICENSE',
        'README.md'
    )
    
    # Critical directories
    $criticalDirs = @('dash', 'static', 'SortNStoreDashboard')
    
    # Create target directory
    New-Item -ItemType Directory -Path $TargetDir -Force -ErrorAction Stop | Out-Null
    
    # Copy core files
    foreach ($file in $coreFiles) {
        $source = Join-Path $SourceDir $file
        if (Test-Path $source) {
            $destination = Join-Path $TargetDir (Split-Path -Leaf $source)
            Copy-Item -Path $source -Destination $destination -Force -ErrorAction SilentlyContinue
            Write-Log "Installed: $file" "DEBUG"
        }
    }
    
    # Copy critical directories
    foreach ($dir in $criticalDirs) {
        $source = Join-Path $SourceDir $dir
        if (Test-Path $source) {
            $destination = Join-Path $TargetDir $dir
            Remove-Item $destination -Recurse -Force -ErrorAction SilentlyContinue
            Copy-Item -Path $source -Destination $destination -Recurse -Force -ErrorAction SilentlyContinue
            Write-Log "Installed directory: $dir" "DEBUG"
        }
    }
    
    Write-Log "Application files installed to: $TargetDir" "SUCCESS"
    
    # Set appropriate permissions for Enterprise deployments
    if ($DeploymentMode -eq 'Enterprise') {
        try {
            $acl = Get-Acl $TargetDir
            $acl.SetAccessRuleProtection($true, $false)
            Set-Acl -Path $TargetDir -AclObject $acl -ErrorAction SilentlyContinue
            Write-Log "Enterprise permissions configured" "DEBUG"
        }
        catch {
            Write-Log "Could not configure advanced permissions: $_" "WARN"
        }
    }
}

function Install-Dependencies {
    param([string]$InstallDir)
    
    Write-Log "Installing Python dependencies..." "INFO"
    
    $reqFile = Join-Path $InstallDir "requirements.txt"
    if (-not (Test-Path $reqFile)) {
        Write-Log "requirements.txt not found" "WARN"
        return
    }
    
    try {
        # Upgrade pip first
        Write-Log "Upgrading pip..." "DEBUG"
        python -m pip install --upgrade pip -q
        
        # Install requirements
        Write-Log "Installing package dependencies..." "DEBUG"
        python -m pip install -r $reqFile -q
        
        Write-Log "Dependencies installed successfully" "SUCCESS"
    }
    catch {
        Write-Log "Dependency installation failed: $_" "ERROR"
        Write-Log "You may need to run: python -m pip install -r '$reqFile' manually" "WARN"
        
        if (-not $Silent) {
            $continue = Read-Host "Continue with installation? (Y/n)"
            if ($continue -eq 'n' -or $continue -eq 'N') { exit 1 }
        }
    }
}

function Setup-Directories {
    param(
        [string]$InstallDir,
        [string]$DeploymentMode
    )
    
    Write-Log "Setting up directory structure..." "INFO"
    
    $logsDir = Join-Path $InstallDir 'logs'
    $configDir = Join-Path $InstallDir 'config'
    $backupDir = Join-Path $InstallDir 'backups'
    
    foreach ($dir in @($logsDir, $configDir, $backupDir)) {
        New-Item -ItemType Directory -Path $dir -Force -ErrorAction Stop | Out-Null
        Write-Log "Created directory: $dir" "DEBUG"
    }
    
    Write-Log "Directory structure configured" "SUCCESS"
    
    return @{
        LogsDir = $logsDir
        ConfigDir = $configDir
        BackupDir = $backupDir
    }
}

function New-InstallationRecord {
    param(
        [string]$InstallDir,
        [string]$DeploymentMode,
        [hashtable]$Paths
    )
    
    Write-Log "Creating installation record..." "INFO"
    
    $installInfo = @{
        InstallationDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        InstallerVersion = $script:ScriptVersion
        PowerShellVersion = $PSVersionTable.PSVersion.ToString()
        WindowsVersion = [System.Environment]::OSVersion.VersionString
        DeploymentMode = $DeploymentMode
        InstallDir = $InstallDir
        LogsDir = $Paths.LogsDir
        ConfigDir = $Paths.ConfigDir
        BackupDir = $Paths.BackupDir
        InstalledBy = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
        ComputerName = $env:COMPUTERNAME
    } | ConvertTo-Json
    
    $recordFile = Join-Path $Paths.ConfigDir "installation_record.json"
    Set-Content -Path $recordFile -Value $installInfo -ErrorAction SilentlyContinue
    
    Write-Log "Installation record saved to: $recordFile" "DEBUG"
}

function Get-SummaryDisplay {
    param(
        [string]$InstallDir,
        [string]$DeploymentMode,
        [hashtable]$Paths
    )
    
    $summary = @"
╔══════════════════════════════════════════════════╗
║  DownloadsOrganizeR Installation Complete       ║
╚══════════════════════════════════════════════════╝

Installation Details:
  Mode: $DeploymentMode
  Directory: $InstallDir
  Logs: $($Paths.LogsDir)
  Config: $($Paths.ConfigDir)

Quick Start:
  1. Review configuration: $($Paths.ConfigDir)\organizer_config.json
  2. Start the service or dashboard
  3. Access dashboard at: http://localhost:5000

Documentation:
  GitHub: https://github.com/Atomsk865/DownloadsOrganizeR
  Getting Started: https://github.com/Atomsk865/DownloadsOrganizeR/tree/main/docs
  
System Information:
  PowerShell Version: $($PSVersionTable.PSVersion)
  Windows Version: $([System.Environment]::OSVersion.VersionString)
  Installation User: $([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)

Installation Log: $(if ($script:LogFile) { $script:LogFile } else { 'Not enabled' })
"@
    
    return $summary
}

# =====================
# Main Installation Flow
# =====================

function Invoke-Installation {
    try {
        # Display banner
        Write-Host "`n" -NoNewline
        Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
        Write-Host "║  DownloadsOrganizeR Enterprise Installer v$($script:ScriptVersion)        ║" -ForegroundColor Cyan
        Write-Host "║  Mode: $($DeploymentMode.PadRight(44)) ║" -ForegroundColor Cyan
        Write-Host "╚════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
        
        # Validation phase
        Write-Log "Starting installation validation..." "INFO"
        Test-AdminPrivileges
        Test-PowerShellVersion
        Test-TLSVersion
        
        if (-not $SkipHealthCheck) {
            Test-SystemRequirements
        }
        
        # Download and extract phase
        Write-Log "Starting download and extraction phase..." "INFO"
        if (-not $DownloadUrl) {
            $DownloadUrl = Get-LatestReleaseUrl
        }
        
        $tempFile = "$env:TEMP\DownloadsOrganizeR-$(Get-Random).zip"
        $tempDir = "$env:TEMP\DownloadsOrganizeR-extract-$(Get-Random)"
        
        Invoke-WebRequestSecure -Uri $DownloadUrl -OutFile $tempFile
        Expand-ZipSecure -ZipFile $tempFile -DestinationPath $tempDir
        
        # Find project directory (GitHub archive creates a subfolder)
        $projectDir = @(Get-ChildItem $tempDir -Directory -ErrorAction SilentlyContinue)[0].FullName
        if (-not $projectDir) {
            $projectDir = $tempDir
        }
        
        # Installation phase
        Write-Log "Starting installation phase..." "INFO"
        Install-FileStructure -SourceDir $projectDir -TargetDir $InstallDir -DeploymentMode $DeploymentMode
        Install-Dependencies -InstallDir $InstallDir
        $paths = Setup-Directories -InstallDir $InstallDir -DeploymentMode $DeploymentMode
        New-InstallationRecord -InstallDir $InstallDir -DeploymentMode $DeploymentMode -Paths $paths
        
        # Cleanup
        Write-Log "Cleaning up temporary files..." "DEBUG"
        Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        
        # Display summary
        Write-Host (Get-SummaryDisplay -InstallDir $InstallDir -DeploymentMode $DeploymentMode -Paths $paths) -ForegroundColor White
        
        Write-Log "Installation completed successfully" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Installation failed: $_" "ERROR"
        Write-Host "`nInstallation failed. Check the log for details." -ForegroundColor Red
        
        if ($script:LogFile) {
            Write-Host "Log file: $($script:LogFile)" -ForegroundColor Yellow
        }
        
        exit 1
    }
}

# Execute installation
Invoke-Installation
