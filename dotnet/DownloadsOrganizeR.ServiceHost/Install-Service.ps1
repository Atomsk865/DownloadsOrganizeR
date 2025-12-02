<#
Installs DownloadsOrganizeR.ServiceHost as a Windows service.
Requires: PowerShell Admin. Uses .NET SDK to publish unless a prebuilt publish dir is provided.
#>

param(
  [string]$PublishDir = "$PSScriptRoot\publish",
  [string]$ServiceName = 'DownloadsOrganizer',
  [string]$PythonExe = 'C:\Scripts\venv\Scripts\python.exe',
  [string]$ScriptPath = 'C:\Scripts\Organizer.py',
  [string]$WorkingDirectory = 'C:\Scripts',
  [string]$Project = (Join-Path $PSScriptRoot 'DownloadsOrganizeR.ServiceHost.csproj')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-Admin {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  $p = New-Object Security.Principal.WindowsPrincipal($id)
  if (-not $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host 'Please run as Administrator.' -ForegroundColor Yellow
    exit 1
  }
}

function Ensure-Directory {
  param([string]$Path)
  if (-not (Test-Path $Path)) { [void](New-Item -ItemType Directory -Path $Path -Force) }
}

function Test-Dotnet {
  return [bool](Get-Command dotnet -ErrorAction SilentlyContinue)
}

function Publish-App {
  param([string]$Proj, [string]$OutDir)
  if (-not (Test-Dotnet)) {
    throw ".NET SDK ('dotnet') not found. Install SDK or provide -PublishDir with prebuilt binaries."
  }
  Write-Host "Publishing self-contained win-x64 from $Proj ..." -ForegroundColor Cyan
  dotnet publish "$Proj" -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -o "$OutDir"
}

function Write-AppSettings {
  param([string]$OutDir)
  $cfg = @{ PythonExe=$PythonExe; ScriptPath=$ScriptPath; WorkingDirectory=$WorkingDirectory; RestartOnExit=$true; RestartDelayMs=5000 } | ConvertTo-Json
  $cfg | Out-File -FilePath (Join-Path $OutDir 'appsettings.json') -Encoding utf8
}

function Install-Service {
  param([string]$OutDir, [string]$Name)
  $exe = Join-Path $OutDir 'DownloadsOrganizeR.ServiceHost.exe'
  if (-not (Test-Path $exe)) { throw "Executable not found: $exe" }
  Write-Host "Creating service $Name ..." -ForegroundColor Cyan
  sc.exe create $Name binPath= "`"$exe`"" start= auto | Out-Null
  sc.exe description $Name "DownloadsOrganizeR Python Host" | Out-Null
  sc.exe start $Name | Out-Null
  Write-Host "Service $Name installed and started." -ForegroundColor Green
}

Ensure-Admin
Ensure-Directory -Path $PublishDir

$exePath = Join-Path $PublishDir 'DownloadsOrganizeR.ServiceHost.exe'
if (Test-Path $exePath) {
  Write-Host "Using existing publish folder: $PublishDir" -ForegroundColor Yellow
} else {
  Publish-App -Proj $Project -OutDir $PublishDir
}

Write-AppSettings -OutDir $PublishDir
Install-Service -OutDir $PublishDir -Name $ServiceName
