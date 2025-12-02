<#
DownloadsOrganizeR Production Installer (Prod-Beta)

Run as Administrator.
- Copies repo files to C:\Scripts (or uses RepoSource)
- Creates Python venv and installs requirements
- Initializes config files
- Optionally installs Windows service via NSSM
- Optionally starts Dashboard
#>

param(
  [string]$RepoSource = (Get-Location).Path,
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
    $psi.Arguments = "-ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`" "
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
  & $venvPython -m pip install --upgrade pip setuptools wheel
  try {
    & $venvPython -m pip install --default-timeout 120 -r $req
  } catch {
    Write-Warning 'Initial requirements install failed. Retrying with increased verbosity...'
    & $venvPython -m pip install --default-timeout 180 -v -r $req
  }
}

function Init-Configs {
  param([string]$Root)
  $org = Join-Path $Root 'organizer_config.json'
  $dash = Join-Path $Root 'dashboard_config.json'
  if (-not (Test-Path $org)) { '{}' | Out-File -FilePath $org -Encoding utf8 }
  if (-not (Test-Path $dash)) { '{"setup_completed": false, "users": [], "roles": {"admin": {"manage_config": true}, "viewer": {}} }' | Out-File -FilePath $dash -Encoding utf8 }
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
  & $nssm install $ServiceName $venvPython $svcScript
  & $nssm set $ServiceName AppStdout (Join-Path $Root 'service-logs\organizer_stdout.log')
  & $nssm set $ServiceName AppStderr (Join-Path $Root 'service-logs\organizer_stderr.log')
  & $nssm start $ServiceName
}

function Start-Dashboard {
  param([string]$Root)
  Write-Host 'Starting Dashboard...'
  $venvPython = Join-Path $Root 'venv\Scripts\python.exe'
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $venvPython
  $psi.Arguments = 'OrganizerDashboard.py'
  $psi.UseShellExecute = $true
  [System.Diagnostics.Process]::Start($psi) | Out-Null
}

# Main
Ensure-Admin
Copy-RepoFiles -Source $RepoSource -Target $TargetRoot
$venvPath = Ensure-Venv -Root $TargetRoot
Pip-Install -Root $TargetRoot
Init-Configs -Root $TargetRoot
if ($InstallService) { Install-Service -Root $TargetRoot -ServiceName $ServiceName }
if (-not $NoStartDashboard) { Start-Dashboard -Root $TargetRoot }

Write-Host @"
`n✓ Setup completed. Open http://localhost:5000 to run first-time setup.
"@ -ForegroundColor Green
