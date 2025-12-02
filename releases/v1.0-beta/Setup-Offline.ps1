<#
DownloadsOrganizeR Offline Installer - v1.0-beta

Installs from local package (no internet required).
Run as Administrator.
#>

param(
  [string]$TargetRoot = 'C:\Scripts',
  [switch]$InstallService,
  [switch]$NoStartDashboard,
  [string]$ServiceName = 'DownloadsOrganizer',
  [string]$PythonExe = 'python'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-Admin {
  $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
  if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host 'Elevating to Administrator...'
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = 'powershell.exe'
    $psi.Verb = 'runas'
    $psi.Arguments = "-ExecutionPolicy Bypass -File `"$PSCommandPath`" -TargetRoot $TargetRoot"
    if ($InstallService) { $psi.Arguments += ' -InstallService' }
    if ($NoStartDashboard) { $psi.Arguments += ' -NoStartDashboard' }
    [System.Diagnostics.Process]::Start($psi) | Out-Null
    exit
  }
}

function Copy-RepoFiles {
  param([string]$Source, [string]$Target)
  Write-Host "Copying files from $Source to $Target ..."
  if (-not (Test-Path $Target)) { New-Item -ItemType Directory -Path $Target | Out-Null }
  $items = @(
    'Organizer.py',
    'OrganizerDashboard.py',
    'OrganizerDashboard',
    'dash',
    'requirements.txt',
    'organizer_config.json',
    'dashboard_config.json',
    'Install-And-Monitor-OrganizerService.ps1',
    'Windows-Dashboard-SmokeTest.ps1'
  )
  foreach ($item in $items) {
    $src = Join-Path $Source $item
    $dst = Join-Path $Target $item
    if (Test-Path $src) {
      if ((Get-Item $src).PSIsContainer) {
        robocopy $src $dst /MIR /NFL /NDL /NP /NJH /NJS | Out-Null
      } else {
        Copy-Item -Recurse -Force $src -Destination $dst
      }
    }
  }
}

function Ensure-Venv {
  param([string]$Root)
  $venvPath = Join-Path $Root 'venv'
  if (-not (Test-Path $venvPath)) {
    Write-Host 'Creating Python virtual environment...'
    Push-Location $Root
    & $PythonExe -m venv venv
    Pop-Location
  }
  return $venvPath
}

function Pip-Install {
  param([string]$Root)
  $venvPython = Join-Path $Root 'venv\Scripts\python.exe'
  $req = Join-Path $Root 'requirements.txt'
  Write-Host 'Installing requirements...'
  & $venvPython -m pip install --upgrade pip | Out-Null
  & $venvPython -m pip install -r $req
}

function Init-Configs {
  param([string]$Root)
  $org = Join-Path $Root 'organizer_config.json'
  $dash = Join-Path $Root 'dashboard_config.json'
  # Preserve existing configs if present
  if (-not (Test-Path $org)) { 
    Copy-Item -Path (Join-Path $PSScriptRoot 'organizer_config.json') -Destination $org -ErrorAction SilentlyContinue
  }
  if (-not (Test-Path $dash)) { 
    Copy-Item -Path (Join-Path $PSScriptRoot 'dashboard_config.json') -Destination $dash -ErrorAction SilentlyContinue
  }
}

function Install-Service {
  param([string]$Root, [string]$ServiceName)
  Write-Host "Installing Windows service $ServiceName via NSSM ..."
  $nssm = 'nssm.exe'
  $svcScript = Join-Path $Root 'Organizer.py'
  $venvPython = Join-Path $Root 'venv\Scripts\python.exe'
  if (-not (Get-Command $nssm -ErrorAction SilentlyContinue)) {
    throw 'NSSM not found on PATH. Please install NSSM and try again.'
  }
  # Check if service already exists
  $existingSvc = & $nssm status $ServiceName 2>$null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "Service $ServiceName already exists. Stopping and removing..."
    & $nssm stop $ServiceName
    & $nssm remove $ServiceName confirm
  }
  & $nssm install $ServiceName $venvPython $svcScript
  & $nssm set $ServiceName AppDirectory $Root
  $logsDir = Join-Path $Root 'service-logs'
  if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }
  & $nssm set $ServiceName AppStdout (Join-Path $logsDir 'organizer_stdout.log')
  & $nssm set $ServiceName AppStderr (Join-Path $logsDir 'organizer_stderr.log')
  & $nssm start $ServiceName
  Write-Host "Service $ServiceName installed and started."
}

function Start-Dashboard {
  param([string]$Root)
  Write-Host 'Starting Dashboard...'
  $venvPython = Join-Path $Root 'venv\Scripts\python.exe'
  $dashScript = Join-Path $Root 'OrganizerDashboard.py'
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $venvPython
  $psi.Arguments = "`"$dashScript`""
  $psi.WorkingDirectory = $Root
  $psi.UseShellExecute = $true
  [System.Diagnostics.Process]::Start($psi) | Out-Null
}

# Main
Ensure-Admin
$repoSource = $PSScriptRoot
Copy-RepoFiles -Source $repoSource -Target $TargetRoot
$venvPath = Ensure-Venv -Root $TargetRoot
Pip-Install -Root $TargetRoot
Init-Configs -Root $TargetRoot
if ($InstallService) { Install-Service -Root $TargetRoot -ServiceName $ServiceName }
if (-not $NoStartDashboard) { Start-Dashboard -Root $TargetRoot }

Write-Host "`n✓ Offline setup completed (v1.0-beta). Open http://localhost:5000 to run first-time setup." -ForegroundColor Green
