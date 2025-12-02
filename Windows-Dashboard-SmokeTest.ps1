<#
Windows Dashboard Smoke Test

Purpose:
- Start the Flask dashboard locally
- Complete first-time setup (Basic auth)
- Verify an authenticated admin call
- Reset setup flag and verify redirect behavior

Prerequisites:
- Run in PowerShell on Windows
- Python 3.12+ installed and on PATH
- Required packages installed: `pip install -r C:\Scripts\requirements.txt`
- Repo deployed to `C:\Scripts` (or adjust `$RepoRoot`)

Usage:
  Right-click → Run with PowerShell (or from elevated PS):
    .\Windows-Dashboard-SmokeTest.ps1

#>

param(
  [string]$RepoRoot = 'C:\Scripts',
  [int]$Port = 5000,
  [ValidateSet('basic','ldap','windows')]
  [string]$AuthMethod = 'basic',
  [string]$AdminUser = 'admin',
  [string]$AdminPass = 'AdminPass123!@#',
  # LDAP params
  [string]$LdapServer = '',
  [string]$LdapBaseDn = '',
  [string]$LdapUserDnTemplate = 'uid={username},{base_dn}',
  [bool]$LdapUseSsl = $true,
  [string]$LdapBindDn = '',
  [string]$LdapBindPassword = '',
  [string]$LdapSearchFilter = '(uid={username})',
  [string[]]$LdapAllowedGroups = @(),
  # Windows params
  [string]$WinDomain = '',
  [string[]]$WinAllowedGroups = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function New-BasicAuthHeader {
  param([string]$Username, [string]$Password)
  $bytes = [System.Text.Encoding]::ASCII.GetBytes("$Username:$Password")
  $b64 = [Convert]::ToBase64String($bytes)
  @{ Authorization = "Basic $b64"; 'Content-Type' = 'application/json' }
}

function Test-PortOpen {
  param([string]$Host = 'localhost', [int]$Port)
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $client.Connect($Host, $Port)
    $client.Close()
    return $true
  } catch { return $false }
}

function Wait-ForPort {
  param([int]$Port, [int]$TimeoutSec = 20)
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    if (Test-PortOpen -Port $Port) { return }
    Start-Sleep -Milliseconds 300
  }
  throw "Port $Port did not open within $TimeoutSec seconds"
}

function Start-Dashboard {
  param([string]$RepoRoot, [int]$Port)
  Write-Host "Starting dashboard at http://localhost:$Port ..."
  Push-Location $RepoRoot
  $startInfo = New-Object System.Diagnostics.ProcessStartInfo
  $startInfo.FileName = 'python'
  $startInfo.Arguments = 'OrganizerDashboard.py'
  $startInfo.UseShellExecute = $true
  $proc = [System.Diagnostics.Process]::Start($startInfo)
  Pop-Location
  Wait-ForPort -Port $Port -TimeoutSec 25
  return $proc
}

function Stop-ProcessSafe {
  param([System.Diagnostics.Process]$Process)
  try { if ($Process -and -not $Process.HasExited) { $Process.Kill() } } catch {}
}

function Initialize-SetupBasic {
  param([string]$BaseUrl, [string]$AdminUser, [string]$AdminPass)
  Write-Host "Completing setup (basic auth) ..."
  $body = @{ admin_username = $AdminUser; admin_password = $AdminPass; auth_method = 'basic'; auth_fallback_enabled = $true } | ConvertTo-Json
  $resp = Invoke-RestMethod -UseBasicParsing -Method POST -Uri "$BaseUrl/api/setup/initialize" -Body $body -ContentType 'application/json'
  if (-not $resp.success) { throw "Setup initialize failed: $($resp | ConvertTo-Json -Compress)" }
}

function Initialize-SetupLdap {
  param(
    [string]$BaseUrl, [string]$AdminUser, [string]$AdminPass,
    [string]$Server, [string]$BaseDn, [string]$UserDnTemplate,
    [bool]$UseSsl, [string]$BindDn, [string]$BindPassword,
    [string]$SearchFilter, [string[]]$AllowedGroups
  )
  Write-Host "Completing setup (LDAP auth) ..."
  if (-not $Server -or -not $BaseDn) { throw "LDAP Server and BaseDn are required" }
  $bodyObj = @{ admin_username = $AdminUser; admin_password = $AdminPass; auth_method = 'ldap'; auth_fallback_enabled = $true;
    server = $Server; base_dn = $BaseDn; user_dn_template = $UserDnTemplate; use_ssl = $UseSsl; bind_dn = $BindDn; bind_password = $BindPassword; search_filter = $SearchFilter; allowed_groups = $AllowedGroups }
  $body = $bodyObj | ConvertTo-Json -Depth 5
  $resp = Invoke-RestMethod -UseBasicParsing -Method POST -Uri "$BaseUrl/api/setup/initialize" -Body $body -ContentType 'application/json'
  if (-not $resp.success) { throw "Setup initialize (LDAP) failed: $($resp | ConvertTo-Json -Compress)" }
}

function Initialize-SetupWindows {
  param([string]$BaseUrl, [string]$AdminUser, [string]$AdminPass, [string]$Domain, [string[]]$AllowedGroups)
  Write-Host "Completing setup (Windows auth) ..."
  $bodyObj = @{ admin_username = $AdminUser; admin_password = $AdminPass; auth_method = 'windows'; auth_fallback_enabled = $true; domain = $Domain; allowed_groups = $AllowedGroups }
  $body = $bodyObj | ConvertTo-Json -Depth 5
  $resp = Invoke-RestMethod -UseBasicParsing -Method POST -Uri "$BaseUrl/api/setup/initialize" -Body $body -ContentType 'application/json'
  if (-not $resp.success) { throw "Setup initialize (Windows) failed: $($resp | ConvertTo-Json -Compress)" }
}

function Test-AdminAuth {
  param([string]$BaseUrl, [string]$AdminUser, [string]$AdminPass)
  Write-Host "Testing authenticated admin config read ..."
  $headers = New-BasicAuthHeader -Username $AdminUser -Password $AdminPass
  $resp = Invoke-WebRequest -UseBasicParsing -Method GET -Uri "$BaseUrl/api/dashboard/config" -Headers $headers
  if ($resp.StatusCode -ne 200) { throw "Admin auth GET failed: $($resp.StatusCode) $($resp.Content)" }
}

function Reset-Setup {
  param([string]$BaseUrl, [string]$AdminUser, [string]$AdminPass)
  Write-Host "Resetting setup (admin rights required) ..."
  $headers = New-BasicAuthHeader -Username $AdminUser -Password $AdminPass
  $resp = Invoke-WebRequest -UseBasicParsing -Method POST -Uri "$BaseUrl/api/setup/reset" -Headers $headers
  if ($resp.StatusCode -ne 200) { throw "Reset setup failed: $($resp.StatusCode) $($resp.Content)" }
}

function Verify-RedirectToSetup {
  param([string]$BaseUrl)
  Write-Host "Verifying redirect to /setup after reset ..."
  $resp = Invoke-WebRequest -UseBasicParsing -Method GET -Uri "$BaseUrl/" -MaximumRedirection 0 -ErrorAction SilentlyContinue
  if ($resp.StatusCode -ne 302 -and $resp.StatusCode -ne 301) { throw "Expected redirect, got $($resp.StatusCode)" }
  if (-not ($resp.Headers.Location -like '*setup*')) { throw "Expected Location header pointing to /setup" }
}

$BaseUrl = "http://localhost:$Port"
$dashboardProc = $null

try {
  # 1) Start dashboard
  $dashboardProc = Start-Dashboard -RepoRoot $RepoRoot -Port $Port

  # 2) Initialize setup based on selected method
  switch ($AuthMethod) {
    'basic'   { Initialize-SetupBasic -BaseUrl $BaseUrl -AdminUser $AdminUser -AdminPass $AdminPass }
    'ldap'    { Initialize-SetupLdap -BaseUrl $BaseUrl -AdminUser $AdminUser -AdminPass $AdminPass -Server $LdapServer -BaseDn $LdapBaseDn -UserDnTemplate $LdapUserDnTemplate -UseSsl $LdapUseSsl -BindDn $LdapBindDn -BindPassword $LdapBindPassword -SearchFilter $LdapSearchFilter -AllowedGroups $LdapAllowedGroups }
    'windows' { Initialize-SetupWindows -BaseUrl $BaseUrl -AdminUser $AdminUser -AdminPass $AdminPass -Domain $WinDomain -AllowedGroups $WinAllowedGroups }
  }

  # 3) Verify admin can access protected config
  Test-AdminAuth -BaseUrl $BaseUrl -AdminUser $AdminUser -AdminPass $AdminPass

  # 4) Reset setup flag and verify redirect to wizard
  Reset-Setup -BaseUrl $BaseUrl -AdminUser $AdminUser -AdminPass $AdminPass
  Verify-RedirectToSetup -BaseUrl $BaseUrl

  Write-Host "\n✓ Smoke test completed successfully" -ForegroundColor Green
}
catch {
  Write-Host "\n✗ Smoke test failed: $($_.Exception.Message)" -ForegroundColor Red
  throw
}
finally {
  Stop-ProcessSafe -Process $dashboardProc
}
