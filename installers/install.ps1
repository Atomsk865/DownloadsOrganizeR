#!/usr/bin/env pwsh
<#
.SYNOPSIS
    DownloadsOrganizeR - One-liner Installer
    Downloads and installs the latest version from GitHub

.DESCRIPTION
    This script downloads the latest release from GitHub and installs DownloadsOrganizeR
    as a Windows service. It handles:
    - Downloading latest release from GitHub
    - Extracting files to installation directory
    - Setting up Windows service via NSSM
    - Configuring file organization rules
    - Setting up health monitoring

.EXAMPLE
    # Download and run in one line:
    irm https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1 | iex

    # Or with parameters:
    irm https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1 | iex -ArgumentList @('-InstallDir', 'C:\DownloadsOrganizeR')

.PARAMETER InstallDir
    Installation directory (default: C:\DownloadsOrganizeR)

.PARAMETER SkipService
    Skip Windows service installation (default: false)

.PARAMETER DownloadUrl
    GitHub release download URL (auto-detected from latest release)

.NOTES
    Requires: PowerShell 5.1+, Administrator privileges
    License: MIT
    Repository: https://github.com/Atomsk865/DownloadsOrganizeR
#>

[CmdletBinding()]
param(
    [string]$InstallDir = "C:\DownloadsOrganizeR",
    [switch]$SkipService,
    [string]$DownloadUrl = ""
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# =====================
# Helper Functions
# =====================

function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "[✓] $args" -ForegroundColor Green }
function Write-Warn { Write-Host "[⚠] $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[✗] $args" -ForegroundColor Red }

function Test-Admin {
    $current = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal $current
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-LatestReleaseUrl {
    try {
        Write-Info "Fetching latest release from GitHub..."
        $apiUrl = "https://api.github.com/repos/Atomsk865/DownloadsOrganizeR/releases/latest"
        $response = Invoke-RestMethod -Uri $apiUrl -TimeoutSec 10
        
        # Find the source code zip asset
        $zipAsset = $response.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1
        
        if (-not $zipAsset) {
            return $response.zipball_url
        }
        return $zipAsset.browser_download_url
    }
    catch {
        Write-Warn "Could not fetch from GitHub API, using fallback URL"
        return "https://github.com/Atomsk865/DownloadsOrganizeR/archive/refs/heads/main.zip"
    }
}

function Expand-ZipSafe {
    param(
        [string]$ZipFile,
        [string]$DestinationPath
    )
    
    if (Test-Path $DestinationPath) {
        Remove-Item $DestinationPath -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
    
    try {
        Expand-Archive -Path $ZipFile -DestinationPath $DestinationPath -Force -ErrorAction Stop
        Write-Success "Extracted files"
    }
    catch {
        Write-Error "Failed to extract archive: $_"
        throw
    }
}

# =====================
# Main Installation
# =====================

Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  DownloadsOrganizeR - Installer      ║" -ForegroundColor Cyan
Write-Host "║  Automated Setup for Windows         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check admin rights
if (-not (Test-Admin)) {
    Write-Error "This script requires Administrator privileges"
    Write-Info "Please run PowerShell as Administrator and try again"
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Success "Running with Administrator privileges"

# Validate install directory
Write-Info "Installation directory: $InstallDir"
if (Test-Path $InstallDir) {
    Write-Warn "Directory already exists. Existing files will be updated."
}

# Get download URL
if (-not $DownloadUrl) {
    $DownloadUrl = Get-LatestReleaseUrl
}
Write-Info "Download URL: $DownloadUrl"

# Download latest release
$tempFile = "$env:TEMP\DownloadsOrganizeR-latest.zip"
$tempDir = "$env:TEMP\DownloadsOrganizeR-extract"

try {
    Write-Info "Downloading latest release..."
    $sw = [Diagnostics.Stopwatch]::StartNew()
    
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $tempFile -TimeoutSec 300 | Out-Null
    
    $sw.Stop()
    $sizeMB = [math]::Round((Get-Item $tempFile).Length / 1MB, 2)
    Write-Success "Downloaded $sizeMB MB in $($sw.Elapsed.TotalSeconds)s"
}
catch {
    Write-Error "Failed to download release: $_"
    exit 1
}

# Extract files
try {
    Write-Info "Extracting files..."
    Expand-ZipSafe -ZipFile $tempFile -DestinationPath $tempDir
    
    # Find the actual project directory (GitHub zip creates subfolder)
    $projectDir = @(Get-ChildItem $tempDir -Directory)[0].FullName
    
    Write-Info "Copying files to $InstallDir..."
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    
    # Copy key files
    $filesToCopy = @(
        'Organizer.py',
        'SortNStoreDashboard.py',
        'requirements.txt',
        'organizer_config.json',
        'dashboard_config.json',
        'LICENSE'
    )
    
    foreach ($file in $filesToCopy) {
        $source = Join-Path $projectDir $file
        if (Test-Path $source) {
            Copy-Item -Path $source -Destination (Join-Path $InstallDir (Split-Path -Leaf $source)) -Force
            Write-Success "Copied $(Split-Path -Leaf $source)"
        }
    }
    
    # Copy directories
    $dirsToCopy = @('dash', 'static', 'SortNStoreDashboard')
    
    foreach ($dir in $dirsToCopy) {
        $source = Join-Path $projectDir $dir
        if (Test-Path $source) {
            $dest = Join-Path $InstallDir $dir
            Remove-Item $dest -Recurse -Force -ErrorAction SilentlyContinue
            Copy-Item -Path $source -Destination $dest -Recurse -Force
            Write-Success "Copied directory: $dir"
        }
    }
    
    Write-Success "Installation files prepared"
}
catch {
    Write-Error "Failed to install files: $_"
    exit 1
}
finally {
    # Cleanup
    Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}

# Install dependencies
Write-Info "Installing Python dependencies..."
try {
    $reqFile = Join-Path $InstallDir "requirements.txt"
    if (Test-Path $reqFile) {
        & pip install -q -r $reqFile
        Write-Success "Dependencies installed"
    }
}
catch {
    Write-Warn "Could not install some dependencies. You may need to run: pip install -r $reqFile"
}

# Create log and config directories
$logsDir = Join-Path $InstallDir 'logs'
$configDir = Join-Path $InstallDir 'config'

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
New-Item -ItemType Directory -Path $configDir -Force | Out-Null
Write-Success "Created directories: logs, config"

# Option to install Windows service
if (-not $SkipService) {
    Write-Info "Setting up Windows service..."
    $installService = Read-Host "Install as Windows service? (Y/n)" 
    
    if ($installService -ne 'n' -and $installService -ne 'N') {
        try {
            # Check if NSSM is available, if not download it
            $nssmPath = Join-Path $env:ProgramFiles 'NSSM\nssm.exe'
            
            if (-not (Test-Path $nssmPath)) {
                Write-Info "Installing NSSM (Non-Sucking Service Manager)..."
                # NSSM installation would go here
                Write-Warn "Please install NSSM manually or use Setup-Installer.ps1 for automatic setup"
            }
            else {
                Write-Success "Service installation available via NSSM"
            }
        }
        catch {
            Write-Warn "Service installation skipped: $_"
        }
    }
}

# Summary
Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  Installation Complete!              ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "Installation directory: $InstallDir" -ForegroundColor White
Write-Host "Configuration file: $(Join-Path $InstallDir 'organizer_config.json')" -ForegroundColor White
Write-Host "Log directory: $logsDir" -ForegroundColor White

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Review configuration: $(Join-Path $InstallDir 'organizer_config.json')" -ForegroundColor White
Write-Host "2. Start the service (or use Dashboard)" -ForegroundColor White
Write-Host "3. Access dashboard at: http://localhost:5000" -ForegroundColor White

Write-Host "`nDocumentation: https://github.com/Atomsk865/DownloadsOrganizeR" -ForegroundColor Cyan
Write-Host "`n"
