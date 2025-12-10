# Compatibility shim: installer renamed to Install-And-Monitor-SortNStoreService.ps1
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$newScript = Join-Path $here 'Install-And-Monitor-SortNStoreService.ps1'
if (Test-Path $newScript) {
    & $newScript @args
} else {
    Write-Host "New installer script not found at $newScript" -ForegroundColor Red
    exit 1
}
