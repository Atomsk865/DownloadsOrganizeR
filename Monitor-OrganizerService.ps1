param(
    [string]$ServiceName = 'DownloadsOrganizer',
    [int]$MemoryThresholdMB = 200,
    [int]$CpuThresholdPercent = 60,
    [int]$CheckIntervalSec = 30
)

function Get-OrganizerProc {
    Get-Process | Where-Object {
        $_.ProcessName -like 'python*'
    } | Where-Object {
        try {
            $_.Path -and ((Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine -like '*Organizer.py*')
        } catch { $false }
    } | Select-Object -First 1
}

$ConfigFile = Join-Path (Split-Path -Parent $PSCommandPath) 'organizer_config.json'
if (Test-Path $ConfigFile) {
    try {
        $cfg = Get-Content $ConfigFile -Raw | ConvertFrom-Json
        if ($cfg.memory_threshold_mb) { $MemoryThresholdMB = [int]$cfg.memory_threshold_mb }
        if ($cfg.cpu_threshold_percent) { $CpuThresholdPercent = [int]$cfg.cpu_threshold_percent }
        if ($cfg.check_interval_sec)    { $CheckIntervalSec   = [int]$cfg.check_interval_sec }
    } catch { }
}

$coreCount = [Environment]::ProcessorCount
Write-Host "Monitoring '$ServiceName' (mem > $MemoryThresholdMB MB OR CPU > $CpuThresholdPercent % -> restart)."

while ($true) {
    $svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($svc -and $svc.Status -eq 'Running') {
        $proc = Get-OrganizerProc
        if ($proc) {
            try {
                $memMB = [math]::Round($proc.WorkingSet64 / 1MB, 2)
                $cpuBeforeSec = $proc.CPU
                Start-Sleep -Seconds ([Math]::Min($CheckIntervalSec, 2))
                $procRefreshed = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
                if ($procRefreshed) {
                    $cpuAfterSec = $procRefreshed.CPU
                    $interval = 2
                    $cpuPct = 0
                    if ($interval -gt 0 -and $coreCount -gt 0) {
                        $delta = $cpuAfterSec - $cpuBeforeSec
                        $cpuPct = [math]::Round(($delta / $interval) * (100 / $coreCount), 1)
                    }
                    if (($memMB -gt $MemoryThresholdMB) -or ($cpuPct -gt $CpuThresholdPercent)) {
                        Write-Host "Threshold exceeded (Mem=$memMB MB, CPU=$cpuPct%). Restarting service..."
                        Restart-Service -Name $ServiceName -Force
                        Start-Sleep -Seconds 5
                    }
                }
            } catch { }
        }
    } else {
        Write-Host "Service not running. Attempting to start..."
        Start-Service -Name $ServiceName -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds $CheckIntervalSec
}
