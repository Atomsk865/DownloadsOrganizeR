<#
Setup-Installer.ps1 - Interactive installer for DownloadsOrganizeR (Windows)

Purpose:
- Prompt for an install directory (default: C:\Organizer)
- Create folder structure (C:\Organizer, C:\Organizer\logs, C:\Organizer\config\json)
- Copy project files into the chosen directory
- Adjust organizer_config.json paths to use local install directories
- (Optional) Offer to install Windows service via NSSM

Run as: PowerShell (Admin recommended)
#>

param(
    [string]$DefaultInstallDir = "C:\Organizer",
    [switch]$InstallService
)

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[ERROR] $msg" -ForegroundColor Red }

try {
    $repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    Write-Info "Repository root: $repoRoot"

    # Prompt for install directory
    $installDir = Read-Host "Enter install directory [default: $DefaultInstallDir]"
    if ([string]::IsNullOrWhiteSpace($installDir)) { $installDir = $DefaultInstallDir }
    $installDir = $installDir.Trim()

    # Create structure
    $logsDir   = Join-Path $installDir 'logs'
    $configDir = Join-Path $installDir 'config'
    $jsonDir   = Join-Path $configDir 'json'
    Write-Info "Creating install directories..."
    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
    New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    New-Item -ItemType Directory -Force -Path $jsonDir | Out-Null

    # Files to copy (Python app + dashboard + static)
    $includePatterns = @(
        'Organizer.py',
        'OrganizerDashboard.py',
        'OrganizerDashboard',
        'dash',
        'requirements.txt',
        'py.typed'
    )

    Write-Info "Copying application files to $installDir"
    foreach ($pat in $includePatterns) {
        $src = Join-Path $repoRoot $pat
        $dst = Join-Path $installDir $pat
        if (Test-Path $src) {
            Write-Info "Copy: $src -> $dst"
            Copy-Item -Path $src -Destination $dst -Recurse -Force
        } else {
            Write-Warn "Missing: $src (skipped)"
        }
    }

    # Copy organizer_config.json and adjust paths
    $srcCfg = Join-Path $repoRoot 'organizer_config.json'
    $dstCfg = Join-Path $installDir 'organizer_config.json'
    if (Test-Path $srcCfg) {
        Copy-Item -Path $srcCfg -Destination $dstCfg -Force
        Write-Info "Adjusting organizer_config.json paths"
        $cfg = Get-Content -Raw -Path $dstCfg | ConvertFrom-Json
        # Ensure relative paths are set to local install dirs
        $cfg.logs_dir         = (Resolve-Path -LiteralPath $logsDir).Path
        $cfg.downloads_json   = (Join-Path $jsonDir 'downloads_dashboard.json')
        $cfg.file_moves_json  = (Join-Path $jsonDir 'file_moves.json')
        # Optional: file_hashes_json if present
        if (-not ($cfg.PSObject.Properties.Name -contains 'file_hashes_json')) {
            # add key if not present
            $cfg | Add-Member -NotePropertyName 'file_hashes_json' -NotePropertyValue (Join-Path $jsonDir 'file_hashes.json')
        } else {
            $cfg.file_hashes_json = (Join-Path $jsonDir 'file_hashes.json')
        }
        # Persist updated config
        ($cfg | ConvertTo-Json -Depth 6) | Set-Content -Path $dstCfg -Encoding UTF8
    } else {
        Write-Warn "organizer_config.json not found in repo root"
    }

    # Create empty initial JSON state files if missing
    $downloadsJson  = Join-Path $jsonDir 'downloads_dashboard.json'
    $fileMovesJson  = Join-Path $jsonDir 'file_moves.json'
    $fileHashesJson = Join-Path $jsonDir 'file_hashes.json'
    foreach ($p in @($downloadsJson, $fileMovesJson, $fileHashesJson)) {
        if (-not (Test-Path $p)) { Write-Info "Seed JSON: $p"; '{}' | Set-Content -Path $p -Encoding UTF8 }
    }

    Write-Info "Install completed at: $installDir"
    Write-Info "Logs directory:       $logsDir"
    Write-Info "Config JSON directory: $jsonDir"

    # Optional service install via NSSM
    if ($InstallService) {
        Write-Info "Installing Windows service via NSSM (DownloadsOrganizer)"
        $nssm = "nssm"
        if (-not (Get-Command $nssm -ErrorAction SilentlyContinue)) {
            Write-Warn "NSSM not found in PATH. Please install NSSM first. Skipping service install."
        } else {
            $pyExe = "python"
            $orgPy = Join-Path $installDir 'Organizer.py'
            & $nssm install DownloadsOrganizer $pyExe $orgPy
            & $nssm set DownloadsOrganizer AppDirectory $installDir
            & $nssm set DownloadsOrganizer AppStdout (Join-Path $logsDir 'organizer_stdout.log')
            & $nssm set DownloadsOrganizer AppStderr (Join-Path $logsDir 'organizer_stderr.log')
            & $nssm start DownloadsOrganizer
            Write-Info "Service DownloadsOrganizer installed and started."
        }
    } else {
        Write-Info "To install as a service later, rerun with -InstallService or use Install-And-Monitor-OrganizerService.ps1"
    }
}
catch {
    Write-Err $_.Exception.Message
    exit 1
}
