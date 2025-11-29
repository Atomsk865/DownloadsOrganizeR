
# 📦 Organizer Service Installer

## Overview
`Install-And-Monitor-OrganizerService.ps1` automates the setup of a Windows service that runs `Organizer.py` to organize your Downloads folder in real time. It installs **NSSM**, configures the service, and creates a health monitoring script.

---

## Features
- ✅ Auto-elevates to Administrator if not already.
- ✅ Installs **NSSM** and configures `DownloadsOrganizer` service.
- ✅ Copies `Organizer.py` to `C:\Scripts`.
- ✅ Creates health monitoring script for CPU and memory usage.
- ✅ Logs all actions to:
  ```
  C:\Scripts\Installer-Transcript.log
  ```

---

## Requirements
- Windows PowerShell (Run as Administrator)
- Python installed and available in PATH
- Internet access (to download NSSM)
- `Organizer.py` in the same folder as this installer script

---

## Parameters
| Parameter              | Description                                      |
|------------------------|--------------------------------------------------|
| `ServiceName`          | Name of the Windows service (default: DownloadsOrganizer) |
| `ScriptsRoot`          | Root folder for scripts (default: C:\Scripts)   |
| `MemoryThresholdMB`    | Memory threshold for health monitor             |
| `CpuThresholdPercent`  | CPU threshold for health monitor                |
| `CheckIntervalSec`     | Interval for health checks                      |
| `DryRun`               | Switch for dry-run mode                         |
| `ServiceUser`          | Service account user                            |
| `ServicePassword`      | Service account password (secure string)        |

---

## Usage
Run PowerShell as Administrator:
```powershell
.\Install-And-Monitor-OrganizerService.ps1
```

Follow prompts to confirm `Organizer.py` location.

---

## Service Details
- Service Name: `DownloadsOrganizer`
- Logs:
  ```
  C:\Scripts\service-logs\organizer_stdout.log
  C:\Scripts\service-logs\organizer_stderr.log
  ```

---

## Health Monitoring
A script `Monitor-OrganizerService.ps1` is generated in `C:\Scripts` to monitor CPU and memory usage.

---

## Uninstall
To remove the service:
```powershell
nssm remove DownloadsOrganizer confirm
```
---

## ▶️ Manual Run (Without NSSM)
If you prefer not to install the service, you can run `Organizer.py` manually:

```powershell
cd C:\Scripts
python Organizer.py
```

For continuous monitoring, you can use:
```powershell
while ($true) {
    python Organizer.py
    Start-Sleep -Seconds 30
}
```

---

# Organizer Dashboard

A web-based dashboard for monitoring and managing the **DownloadsOrganizer** service. Built with Python and Flask, this tool provides real-time insights into system resources, service status, drive space, network activity, and more. Easily configure file routing rules, resource thresholds, and view live logs—all from a user-friendly interface.

---

## Features

- **Service status monitoring and control**
- **Real-time CPU, RAM, and network usage**
- **Customizable file organization rules by extension**
- **Live stdout/stderr log streaming and management**
- **Drive space and hardware info display**
- **Task manager for top processes**
- **Easy configuration via web UI**

---

## Requirements

- Python 3.7+
- Flask
- psutil
- setuptools
- *(Optional)* GPUtil for GPU info

---

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Atomsk865/DownloadsOrganizeR.git
   cd DownloadsOrganizeR
   ```
   
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Dashboard:**
   Create a batch file to run it:
   ```bash
   @echo off
   REM Launch OrganizerDashboard.py
   powershell Start-Process python "C:\Path\To\OrganizerDashboard.py"

   REM Give it a moment to start, then open the dashboard in your default browser
   timeout /t 3 >nul
   start http://localhost:5000

   exit
   ```
   or type:
   ```bash
   python organizerdashboard.py
   ```

