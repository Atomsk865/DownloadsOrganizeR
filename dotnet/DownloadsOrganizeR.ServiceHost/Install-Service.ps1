<#
Installs DownloadsOrganizeR.ServiceHost as a Windows service.
Requires: PowerShell Admin, .NET SDK or published binary.
#>

param(
  [string]$PublishDir = "$PSScriptRoot\publish",
  [string]$ServiceName = 'DownloadsOrganizer',
  [string]$PythonExe = 'C:\Scripts\venv\Scripts\python.exe',
  [string]$ScriptPath = 'C:\Scripts\Organizer.py',
  [string]$WorkingDirectory = 'C:\Scripts'
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

function Publish-App {
  param([string]$OutDir)
  Write-Host 'Publishing self-contained win-x64...' -ForegroundColor Cyan
  dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -o $OutDir
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
  sc.exe description $Name "DownloadsOrganizeR Python Host"
  sc.exe start $Name | Out-Null
  Write-Host "Service $Name installed and started." -ForegroundColor Green
}

Ensure-Admin
Publish-App -OutDir $PublishDir
Write-AppSettings -OutDir $PublishDir
Install-Service -OutDir $PublishDir -Name $ServiceName
