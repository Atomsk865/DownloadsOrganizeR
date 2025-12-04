
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
Write-Host "⏳ Starting service installation..." -ForegroundColor Cyan

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
        # Copy organizer_config.json if present so the service uses the same config
        $configSource = Join-Path $PSScriptRoot "organizer_config.json"
        $configDest = Join-Path $ScriptsRoot "organizer_config.json"
        if (Test-Path $configSource) {
            Copy-Item -Path $configSource -Destination $configDest -Force
            Write-Host "Copied organizer_config.json to $ScriptsRoot" -ForegroundColor Green
        } else {
            Write-Host "No local organizer_config.json found; continuing with defaults." -ForegroundColor Yellow
        }
        # Copy requirements.txt if present so we can install dependencies in the venv
        $reqSource = Join-Path $PSScriptRoot "requirements.txt"
        $reqDest = Join-Path $ScriptsRoot "requirements.txt"
        if (Test-Path $reqSource) {
            Copy-Item -Path $reqSource -Destination $reqDest -Force
            Write-Host "Copied requirements.txt to $ScriptsRoot" -ForegroundColor Green
        } else {
            Write-Host "No requirements.txt found; skipping dependency install." -ForegroundColor Yellow
        }

        # Create a Python virtualenv inside $ScriptsRoot\venv and install requirements if possible
        $PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
        if (-not $PythonPath) { $PythonPath = (Get-Command py -ErrorAction SilentlyContinue).Source }
        if ($PythonPath) {
            $VenvDir = Join-Path $ScriptsRoot "venv"
            if (-not (Test-Path $VenvDir)) {
                Write-Host "Creating virtualenv at $VenvDir" -ForegroundColor Cyan
                & $PythonPath -m venv $VenvDir
            }
            $VenvPython = Join-Path $VenvDir "Scripts\python.exe"
            if (-not (Test-Path $VenvPython)) { $VenvPython = Join-Path $VenvDir "bin/python" }
            if (Test-Path $reqDest -and Test-Path $VenvPython) {
                Write-Host "Installing requirements into virtualenv" -ForegroundColor Cyan
                & $VenvPython -m pip install --upgrade pip
                & $VenvPython -m pip install -r $reqDest
            } else {
                Write-Host "Virtualenv python or requirements not found; will fall back to system Python for service." -ForegroundColor Yellow
            }
        } else {
            Write-Host "System Python not found in PATH; service will attempt to use existing 'python' command if available." -ForegroundColor Yellow
        }

    # -------------------------
    # Resolve Service Name (config or parameter)
    # -------------------------
    $ConfiguredServiceName = $null
    if (Test-Path $configDest) {
        try {
            $cfg = Get-Content -Path $configDest -Raw | ConvertFrom-Json
            if ($cfg -and $cfg.PSObject.Properties.Name -contains 'service_name') { $ConfiguredServiceName = $cfg.service_name }
            elseif ($cfg -and $cfg.PSObject.Properties.Name -contains 'SERVICE_NAME') { $ConfiguredServiceName = $cfg.SERVICE_NAME }
        } catch {
            Write-Host "Warning: failed to parse organizer_config.json: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }

    if (-not $PSBoundParameters.ContainsKey('ServiceName') -and $ConfiguredServiceName) {
        $DesiredServiceName = $ConfiguredServiceName
        Write-Host "Using service name from organizer_config.json: $DesiredServiceName" -ForegroundColor Cyan
    } else {
        $DesiredServiceName = $ServiceName
        Write-Host "Using service name from parameter/default: $DesiredServiceName" -ForegroundColor Cyan
    }

    # If we've installed a service before under a different name, remove it so we can re-install under the new name
    $MarkerPath = Join-Path $ScriptsRoot "installed_service_name.txt"
    if (Test-Path $MarkerPath) {
        try {
            $PrevName = (Get-Content -Path $MarkerPath -Raw).Trim()
        } catch { $PrevName = $null }
        if ($PrevName -and $PrevName -ne $DesiredServiceName) {
            Write-Host "Service name changed from '$PrevName' to '$DesiredServiceName'. Removing previous service '$PrevName'..." -ForegroundColor Yellow
            if (Get-Service -Name $PrevName -ErrorAction SilentlyContinue) {
                try { Stop-Service -Name $PrevName -Force -ErrorAction SilentlyContinue } catch {}
                & $NssmExe remove $PrevName confirm | Out-Null
                Write-Host "Removed previous service '$PrevName'." -ForegroundColor Green
            } else {
                Write-Host "Previous service '$PrevName' not found; skipping removal." -ForegroundColor Yellow
            }
        }
    }

    # Use the resolved name from here on
    $ServiceName = $DesiredServiceName

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
    # Prefer virtualenv python if present
    if (Test-Path (Join-Path $ScriptsRoot "venv\Scripts\python.exe")) {
        $ServicePython = Join-Path $ScriptsRoot "venv\Scripts\python.exe"
    } elseif (Test-Path (Join-Path $ScriptsRoot "venv/bin/python")) {
        $ServicePython = Join-Path $ScriptsRoot "venv/bin/python"
    } else {
        $ServicePython = $PythonPath
    }

    $AppArgs = "`"$destFile`""
    if ($DryRun) { $AppArgs += " --dry-run" }

    if (-not (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue)) {
        & $NssmExe install $ServiceName $ServicePython $AppArgs
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
    # Persist the installed service name so future runs can detect renames
    try {
        Set-Content -Path $MarkerPath -Value $ServiceName -Force -Encoding UTF8
        Write-Host "Recorded installed service name to $MarkerPath" -ForegroundColor Cyan
    } catch {
        Write-Host "Warning: failed to write installed service marker: $($_.Exception.Message)" -ForegroundColor Yellow
    }

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
