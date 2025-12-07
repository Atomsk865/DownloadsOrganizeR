# DownloadsOrganizeR Quick Installer
# This script forces a fresh download bypassing all caches

$ErrorActionPreference = "Stop"

Write-Host "Downloading DownloadsOrganizeR installer..." -ForegroundColor Cyan

# Force fresh download with multiple cache-busting methods
$timestamp = [DateTime]::Now.Ticks
$url = "https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/Install-DownloadsOrganizeR.ps1?t=$timestamp"
$installerPath = "$env:TEMP\Install-DownloadsOrganizeR-$timestamp.ps1"

# Delete any old cached versions
Remove-Item "$env:TEMP\Install-DownloadsOrganizeR*.ps1" -Force -ErrorAction SilentlyContinue

# Download with no-cache headers
$webClient = New-Object System.Net.WebClient
$webClient.Headers.Add("Cache-Control", "no-cache, no-store, must-revalidate")
$webClient.Headers.Add("Pragma", "no-cache")
$webClient.Headers.Add("Expires", "0")
$webClient.DownloadFile($url, $installerPath)

Write-Host "Starting installation..." -ForegroundColor Green
Write-Host ""

# Execute the installer
& $installerPath

# Cleanup
Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
