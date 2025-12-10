# Compatibility shim: monitoring script renamed to Monitor-SortNStoreService.ps1
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$newScript = Join-Path $here 'Monitor-SortNStoreService.ps1'
if (Test-Path $newScript) {
    & $newScript @args
} else {
    Write-Host "New monitoring script not found at $newScript" -ForegroundColor Red
    exit 1
}
