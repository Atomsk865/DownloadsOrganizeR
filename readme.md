
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

3. **Run the Dashboard: **
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

