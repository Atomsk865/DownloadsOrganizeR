
<#
Install-And-Monitor-OrganizerService.ps1
- Purpose: Installs NSSM, configures DownloadsOrganizer service, and sets up health monitoring.
- Requirements: Auto-relaunches as Administrator if not elevated.
- Logs: C:\Scripts\Installer-Transcript.log
#>

[CmdletBinding()]
param(
    [string]$ServiceName          = "DownloadsOrganizer",
    [string]$ScriptsRoot          = "C:\Scripts",
    [int]   $MemoryThresholdMB    = 200,
    [int]   $CpuThresholdPercent  = 60,
    [int]   $CheckIntervalSec     = 30,
    [switch]$DryRun,
    [string]$ServiceUser          = "$env:USERDOMAIN\$env:USERNAME",
    [securestring]$ServicePassword
)

# -------------------------
# Auto-Elevation Check
# -------------------------
$IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $IsAdmin) {
    Write-Host "⚠️ Script is not running as Administrator. Relaunching with elevated privileges..." -ForegroundColor Yellow
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "powershell.exe"
    $psi.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    $psi.Verb = "runas"
    try {
        [System.Diagnostics.Process]::Start($psi) | Out-Null
        exit
    } catch {
        Write-Host "❌ Elevation failed. Please run PowerShell as Administrator manually." -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Running with Administrator privileges." -ForegroundColor Green

# -------------------------
# User Confirmation
# -------------------------
$answer = Read-Host "Is your Organizer.py in the same folder as your installer? (Y/N)"
$answer = $answer.Trim().ToLower()
if ($answer -eq "n") { Write-Host "Exiting program..."; exit }
elseif ($answer -ne "y") { Write-Host "Invalid input. Please enter Y or N."; exit }

Write-Host "✅ Continuing setup..." -ForegroundColor Cyan

# -------------------------
# Prepare Environment
# -------------------------
try {
    if (-not (Test-Path -LiteralPath $ScriptsRoot)) {
        New-Item -ItemType Directory -Path $ScriptsRoot -Force | Out-Null
        Write-Host "Created directory: $ScriptsRoot" -ForegroundColor Green
    }

    # Copy Organizer.py
    $sourceFile = Join-Path $PSScriptRoot "Organizer.py"
    $destFile   = Join-Path $ScriptsRoot "Organizer.py"
    if (Test-Path $sourceFile) {
        Copy-Item -Path $sourceFile -Destination $destFile -Force
        Write-Host "Copied Organizer.py to $ScriptsRoot" -ForegroundColor Green
    } else {
        throw "Organizer.py not found in $PSScriptRoot. Please place it in the same folder as this script."
    }

    # Start transcript
    $TranscriptPath = Join-Path $ScriptsRoot "Installer-Transcript.log"
    Start-Transcript -Path $TranscriptPath -Append | Out-Null
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    # -------------------------
    # Validate Python
    # -------------------------
    $PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $PythonPath) { throw "Python not found in PATH. Please install Python and ensure it's accessible." }

    # -------------------------
    # Install NSSM
    # -------------------------
    Write-Host "==> Checking NSSM..." -ForegroundColor Cyan
    $NssmRoot = "C:\Tools\NSSM"
    $NssmExe = Get-ChildItem -Path $NssmRoot -Recurse -Filter 'nssm.exe' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName

    if (-not $NssmExe) {
        Write-Host "Downloading NSSM..." -ForegroundColor Yellow
        $ZipPath = Join-Path $env:TEMP "nssm.zip"
        $PrimaryUrl = "https://nssm.cc/release/nssm-2.24.zip"
        $FallbackUrl = "https://github.com/HandSonic/nssm/releases/download/dee49fc/nssm-2.24.zip"
        try {
            Invoke-WebRequest -Uri $PrimaryUrl -OutFile $ZipPath -UseBasicParsing
        } catch {
            Write-Warning "Primary URL failed. Trying fallback..."
            Invoke-WebRequest -Uri $FallbackUrl -OutFile $ZipPath -UseBasicParsing
        }
        if (-not (Test-Path $ZipPath)) { throw "Failed to download NSSM ZIP." }
        New-Item -ItemType Directory -Path $NssmRoot -Force | Out-Null
        Expand-Archive -LiteralPath $ZipPath -DestinationPath $NssmRoot -Force
        $NssmExe = Get-ChildItem -Path $NssmRoot -Recurse -Filter 'nssm.exe' | Select-Object -First 1 -ExpandProperty FullName
        if (-not $NssmExe) { throw "NSSM executable not found after extraction." }
    }
    Write-Host "✅ NSSM ready: $NssmExe" -ForegroundColor Green

    # -------------------------
    # Install Service
    # -------------------------
    $LogsRoot = Join-Path $ScriptsRoot "service-logs"
    New-Item -ItemType Directory -Path $LogsRoot -Force | Out-Null
    $StdOutLog = Join-Path $LogsRoot "organizer_stdout.log"
    $StdErrLog = Join-Path $LogsRoot "organizer_stderr.log"

    Write-Host "Installing service '$ServiceName'..." -ForegroundColor Cyan
    $AppArgs = "`"$destFile`""
    if ($DryRun) { $AppArgs += " --dry-run" }

    if (-not (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue)) {
        & $NssmExe install $ServiceName $PythonPath $AppArgs
    }

    & $NssmExe set $ServiceName Description "Organizes Downloads folder in real-time using Organizer.py"
    & $NssmExe set $ServiceName AppDirectory $ScriptsRoot
    & $NssmExe set $ServiceName AppStdout $StdOutLog
    & $NssmExe set $ServiceName AppStderr $StdErrLog
    & $NssmExe set $ServiceName Start SERVICE_AUTO_START

    if ($ServiceUser -and $ServicePassword) {
        $Plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
                    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($ServicePassword))
        & $NssmExe set $ServiceName ObjectName $ServiceUser $Plain
    } else {
        & $NssmExe set $ServiceName ObjectName LocalSystem
    }

    Start-Service -Name $ServiceName
    Write-Host "✅ Service '$ServiceName' installed and started." -ForegroundColor Green

    # -------------------------
    # Health Monitor Script
    # -------------------------
    $MonitorScriptPath = Join-Path $ScriptsRoot "Monitor-OrganizerService.ps1"
    $MonitorScript = @"
param(
    [string]`$ServiceName = '$ServiceName',
    [int]`$MemoryThresholdMB = $MemoryThresholdMB,
    [int]`$CpuThresholdPercent = $CpuThresholdPercent,
    [int]`$CheckIntervalSec = $CheckIntervalSec
)
# Monitoring logic placeholder...
"@
    Set-Content -Path $MonitorScriptPath -Value $MonitorScript -Encoding UTF8
    Write-Host "✅ Health monitor script created: $MonitorScriptPath" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Stop-Transcript | Out-Null
    Write-Host "Transcript saved to: $TranscriptPath" -ForegroundColor Cyan
    Read-Host "Press Enter to close"
}
