# 

# \# DownloadsOrganizer

# 

# \### Automated Downloads Organizer for Windows – One-click setup with PowerShell + Python

# 

# ---

# 

# \## ✅ Overview

# 

# \*\*Organizer\*\* is a smart Downloads folder organizer for Windows. It includes:

# \- A PowerShell installer that sets up the service automatically.

# \- A Python script that organizes your Downloads folder in real time.

# \- Perfect for users who want a hands-off, automated solution to keep their Downloads folder clean and organized.

# 

# ---

# 

# \## ✅ Features

# 

# \*\*Installer Script\*\*

# \- Auto-elevates to Administrator if needed.

# \- Creates `C:\\Scripts` directory for service files and logs.

# \- Copies the Python organizer script.

# \- Installs and configures the service using NSSM.

# \- Sets up logging and health monitoring.

# \- Provides user-friendly prompts and error handling.

# 

# \*\*Python Organizer Script\*\*

# \- Sorts files into category-based folders (Images, Videos, Documents, Music, Archives, etc.).

# \- Monitors Downloads in real time using watchdog.

# \- Handles duplicates gracefully.

# \- Ignores incomplete or temporary files.

# \- Generates a dashboard JSON summary.

# \- Logs all actions for easy troubleshooting.

# 

# ---

# 

# \## ✅ Requirements

# 

# \- Windows 10/11

# \- Administrator privileges (installer auto-prompts if not elevated)

# \- Python 3.8+ installed and added to PATH

# 

# \*\*Required Python package:\*\*

# ```bash

# pip install watchdog

# ```

# 

# ---

# 

# \## ✅ Quick Start

# 

# \*\*One-liner Setup:\*\*

# ```powershell

# Set-ExecutionPolicy Bypass -Scope Process -Force; cd "C:\\Path\\To\\Installer"; .\\Install-And-Monitor-OrganizerService.ps1

# ```

# Replace `C:\\Path\\To\\Installer` with the folder containing:

# \- `Install-And-Monitor-OrganizerService.ps1`

# \- `organizer.py`

# 

# ---

# 

# \### Installation Steps

# 

# 1\. \*\*Download the repo:\*\*

# &nbsp;   ```bash

# &nbsp;   git clone https://github.com/Atomsk865/DownloadsOrganizer.git

# &nbsp;   ```

# 2\. \*\*Open PowerShell as Administrator.\*\*

# 3\. \*\*Navigate to the repo folder:\*\*

# &nbsp;   ```powershell

# &nbsp;   cd "C:\\Path\\To\\organizer"

# &nbsp;   ```

# 4\. \*\*Run the installer:\*\*

# &nbsp;   ```powershell

# &nbsp;   Set-ExecutionPolicy Bypass -Scope Process -Force

# &nbsp;   .\\Install-And-Monitor-OrganizerService.ps1

# &nbsp;   ```

# 5\. \*\*Follow the prompts:\*\*

# &nbsp;   - Confirm with `Y` to continue.

# &nbsp;   - The script will handle NSSM installation, service setup, and health monitor creation.

# 

# ---

# 

# \## ✅ Output

# 

# \- Service `DownloadsOrganizer` runs automatically on startup.

# \- Logs stored in: `C:\\Scripts\\service-logs\\`

# \- Dashboard summary: `C:\\Scripts\\downloads\_dashboard.json`

# \- Health monitor script: `C:\\Scripts\\Monitor-OrganizerService.ps1`

# 

# ---

# 

# \## ✅ Uninstalling the Service

# 

# To remove the service:

# ```bash

# nssm remove DownloadsOrganizer confirm

# ```

# 

# ---

# 

# \## ✅ Troubleshooting

# 

# \- \*\*Python not found?\*\*  

# &nbsp; Install from https://www.python.org/downloads/ and add to PATH.

# 

# \- \*\*watchdog missing?\*\*  

# &nbsp; Run:

# &nbsp; ```bash

# &nbsp; pip install watchdog

# &nbsp; ```

# 

# \- \*\*Permission issues?\*\*  

# &nbsp; Ensure you run PowerShell as Administrator.

# 

# ---

# 

# \## ✅ License

# 

# MIT License – Free to use and modify.



