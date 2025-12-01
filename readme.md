# DownloadsOrganizeR 📦

Automatically organize your Downloads folder by file type. DownloadsOrganizeR monitors your Downloads folder in real-time and sorts files into categories (Images, Videos, Documents, etc.) — no manual work required.

---

## Install

If you prefer to install and run DownloadsOrganizeR using only the command line (no interactive GUI installer), two approaches are supported: (A) Run as a user-mode background process (no service), or (B) Install as a Windows service using NSSM (requires Administrator). To make either approach easier, a helper PowerShell script is included at `scripts/install-service-monitor.ps1` which automates venv creation, copying files, registering a service with NSSM, and optionally installing a simple scheduled-task monitor.

Quick: use the helper script (recommended)

The helper script bundles the common steps so you don't need to run many commands by hand.

From an elevated (Administrator) PowerShell prompt (for service mode) or a normal PowerShell prompt (for user-mode):

- Example: install as a service (requires NSSM present at C:\nssm\nssm.exe)
  ```powershell
  # Run from repository root, or pass -SourcePath to point to the repo
  powershell -ExecutionPolicy Bypass -File .\scripts\install-service-monitor.ps1 -InstallPath 'C:\DownloadsOrganizeR' -InstallService -NssmPath 'C:\nssm\nssm.exe'
  ```

- Example: install user-mode background run and optional Scheduled Task autostart (no admin required)
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\install-service-monitor.ps1 -InstallPath "$env:USERPROFILE\Downloads\DownloadsOrganizeR" -InstallUserMode -CreateScheduledTask
  ```

- See usage/help:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\install-service-monitor.ps1 -Help
  ```

The script will:
- Copy the minimal runtime files (Organizer.py, organizer_config.json, requirements.txt) into the target InstallPath.
- Create a Python virtual environment and install requirements inside it.
- For service mode: register the service with NSSM, configure stdout/stderr log paths, and start the service.
- Optionally create a Scheduled Task that monitors the service and restarts it if not running (5-minute repetition).

If you prefer the manual commands, read on.

### A — User-mode (CLI-only, no Windows service)
This option runs the organizer in the background for the current user. It does not create a Windows service and is the quickest CLI-only setup.

1. Clone the repository and prepare a Python virtual environment:
   - Open PowerShell (normal user)
   - Run:
     ```powershell
     git clone https://github.com/Atomsk865/DownloadsOrganizeR.git
     cd DownloadsOrganizeR

     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     pip install -r requirements.txt
     ```

2. (Optional) Copy files to a persistent location (recommended if you want them outside the repo):
   ```powershell
   mkdir C:\Scripts -Force
   Copy-Item -Path .\Organizer.py, .\organizer_config.json -Destination C:\Scripts
   New-Item -ItemType Directory -Path C:\Scripts\service-logs -Force
   ```

3. Run the organizer in the background (detached):
   - Using pythonw from the virtualenv (no console window):
     ```powershell
     Start-Process -FilePath "$PWD\.venv\Scripts\pythonw.exe" -ArgumentList "C:\Scripts\Organizer.py" -WindowStyle Hidden
     ```
   - Or start it minimized with a console:
     ```powershell
     Start-Process -FilePath "$PWD\.venv\Scripts\python.exe" -ArgumentList "C:\Scripts\Organizer.py" -WindowStyle Minimized
     ```

4. To stop: find the process and terminate it (Task Manager or):
   ```powershell
   Get-Process -Name python, pythonw -ErrorAction SilentlyContinue | Stop-Process -Force
   ```

Notes:
- This approach runs as the current user. It will not automatically start after reboot unless you add a Scheduled Task or put a shortcut in Startup.
- To auto-start on login via CLI, create a Scheduled Task (adjust paths if you copied files elsewhere):
  ```powershell
  schtasks /Create /TN "DownloadsOrganizeR" /TR "`"$PWD\.venv\Scripts\pythonw.exe`" `"C:\Scripts\Organizer.py`"" /SC ONLOGON /RL HIGHEST
  ```

### B — Windows service (CLI-only, Administrator required) using NSSM
This option creates a proper Windows service using NSSM (Non-Sucking Service Manager). It is fully scriptable from the CLI and appropriate for headless or always-on setups.

1. Prepare files and venv (run in an elevated PowerShell prompt if you plan to place files under `C:\`):
   ```powershell
   git clone https://github.com/Atomsk865/DownloadsOrganizeR.git
   cd DownloadsOrganizeR

   python -m venv C:\DownloadsOrganizeR\.venv
   C:\DownloadsOrganizeR\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt

   Copy-Item -Path .\Organizer.py, .\organizer_config.json -Destination C:\DownloadsOrganizeR -Force
   New-Item -ItemType Directory -Path C:\DownloadsOrganizeR\service-logs -Force
   ```

2. Download and extract NSSM (one-time, requires admin):
   - You can get NSSM from https://nssm.cc/
   - Place `nssm.exe` somewhere accessible, e.g. `C:\nssm\nssm.exe`, or add it to PATH.

3. Install the service with NSSM (run as Administrator):
   ```powershell
   C:\nssm\nssm.exe install DownloadsOrganizer "C:\DownloadsOrganizeR\.venv\Scripts\python.exe" "C:\DownloadsOrganizeR\Organizer.py"
   C:\nssm\nssm.exe set DownloadsOrganizer AppDirectory "C:\DownloadsOrganizeR"
   C:\nssm\nssm.exe set DownloadsOrganizer AppStdout "C:\DownloadsOrganizeR\service-logs\organizer_stdout.log"
   C:\nssm\nssm.exe set DownloadsOrganizer AppStderr "C:\DownloadsOrganizeR\service-logs\organizer_stderr.log"
   C:\nssm\nssm.exe start DownloadsOrganizer
   ```

4. To remove the service (Administrator):
   ```powershell
   C:\nssm\nssm.exe remove DownloadsOrganizer confirm
   ```

Notes:
- Installing a service requires Administrator privileges.
- The service will run as the account NSSM configures (by default the Local System account unless you change service user). If you need it to run as a specific user, configure that via `nssm.exe` GUI or use `nssm set DownloadsOrganizer ObjectName "DOMAIN\User" "Password"`.
- Make sure the virtualenv and the python executable paths are correct. Using the venv's python ensures proper isolation and installed dependencies.

### Configuration and environment notes
- The service and local runs both read `organizer_config.json`. If you copied files to `C:\DownloadsOrganizeR`, ensure `C:\DownloadsOrganizeR\organizer_config.json` exists and contains your desired `routes`, `memory_threshold_mb`, `cpu_threshold_percent`, and `logs_dir`.
- Default logs for service-mode are written to `C:\DownloadsOrganizeR\service-logs\`.
- Dashboard users: if you use the Dashboard, keep `organizer_config.json` in the location your Dashboard expects (default: `C:\DownloadsOrganizeR\organizer_config.json`) or update the Dashboard settings accordingly.

### Troubleshooting (CLI)
- If the service fails to start: check `C:\DownloadsOrganizeR\service-logs\organizer_stderr.log` and `organizer_stdout.log`.
- Permissions issues: ensure the service account (or your user) has read/write access to the Downloads folder and the configured target folders.
- If Organizer prompts for a username when started interactively, supply the same user as the service account or pre-edit the `organizer_config.json` to ensure desired paths.

---

## Quick Start (5 minutes)

### Option 1: Automated Service Installation (Recommended)

1. **Install Python** if you haven't already ([python.org](https://www.python.org/downloads/))
2. **Download this repository** or clone it:
   ```bash
   git clone https://github.com/Atomsk865/DownloadsOrganizeR.git
   cd DownloadsOrganizeR
   ```
3. **Run the installer** (Right-click PowerShell → Run as Administrator):
   ```powershell
   .\Install-And-Monitor-OrganizerService.ps1
   ```
4. **Done!** The service will start automatically on boot and organize your Downloads in real-time.

### Option 2: Manual Run (No Service)

```powershell
cd DownloadsOrganizeR
pip install -r requirements.txt
python Organizer.py
```

---

## Dashboard 📊

Monitor and configure the organizer from a web dashboard:

```bash
pip install -r requirements.txt
python OrganizerDashboard.py
```

Then open: **http://localhost:5000**

**Default credentials (Dashboard)**

- **Username:** `admin`
- **Password:** `change_this_password`

You can override these by setting environment variables before launching the dashboard:

```bash
export DASHBOARD_USER=myusername
export DASHBOARD_PASS=mypassword
python OrganizerDashboard.py
```

### Dashboard Features
- 🔍 Real-time service monitoring
- 📈 CPU, RAM, and network usage
- ⚙️ Customize file organization rules
- 📋 Live log viewer
- 💾 Drive space overview
- 📱 Responsive web UI

---

## What Gets Organized?

Files are automatically sorted into folders by type:

| Category | File Types |
|----------|-----------|
| **Images** | jpg, png, gif, svg, webp, heic, psd, ai, ... |
| **Videos** | mp4, mkv, avi, mov, wmv, webm, flv, ... |
| **Music** | mp3, wav, flac, aac, ogg, wma, m4a, ... |
| **Documents** | pdf, doc, docx, txt, excel, ppt, csv, ... |
| **Archives** | zip, rar, 7z, tar, gz, iso, ... |
| **Executables** | exe, msi, bat, cmd, ps1, app, ... |
| **Scripts** | py, js, html, css, json, xml, ts, php, ... |
| **Fonts** | ttf, otf, woff, eot, ... |
| **Shortcuts** | lnk, url, webloc, ... |
| **Logs** | log, out, err |
| **Other** | Everything else |

---

## Configuration

### Editing Organization Rules

1. Open the Dashboard: http://localhost:5000
2. Go to "Configuration" section
3. Add/remove file extensions for each category
4. Changes apply immediately

### Environment Variables (Dashboard Security)

Set custom login credentials:

```bash
set DASHBOARD_USER=myusername
set DASHBOARD_PASS=mypassword
python OrganizerDashboard.py
```

---

## Troubleshooting

### Service won't start?
- Check logs: `C:\Scripts\service-logs\organizer_stdout.log`
- Ensure Python is in PATH: `python --version`
- Try running manually: `cd C:\Scripts && python Organizer.py`

### Dashboard won't connect?
- Verify service is running: Check Windows Services
- Ensure port 5000 is available: `netstat -ano | findstr :5000`
- Check firewall settings

### Files not organizing?
- Check the organizer log: `C:\Users\{username}\Downloads\organizer.log`
- Verify file extensions are in the config
- Ensure destination folders are writable

---

## Uninstall

Remove the Windows service:

```powershell
nssm remove DownloadsOrganizer confirm
```

Then delete the `C:\Scripts\Organizer.py` file if desired.

---

## Requirements

- **Windows** (Service installation only)
- **Python 3.7+**
- **Dependencies:**
  ```
  watchdog==6.0.0     # File monitoring
  Flask==3.1.2        # Dashboard web framework
  psutil==7.1.3       # System metrics
  gputil==1.4.0       # GPU info (optional)
  ```

---

## File Structure

```
DownloadsOrganizeR/
├── Organizer.py                          # Core file organizer
├── OrganizerDashboard.py                 # Web dashboard
├── Install-And-Monitor-OrganizerService.ps1  # Service installer (GUI)
├── organizer_config.json                 # Configuration file
├── requirements.txt                      # Python dependencies
├── README.md                             # This file
└── scripts/
    └── install-service-monitor.ps1       # CLI helper script for installation
```

---

## License

[LICENSE](LICENSE)

---

## Support

Found a bug? Have a feature request? Open an issue on [GitHub](https://github.com/Atomsk865/DownloadsOrganizeR/issues).
