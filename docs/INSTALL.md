# Installation Guide

This guide covers installing the Windows service, running locally for development, configuring the dashboard, and uninstalling.

## Prerequisites

- Windows 10/11
- PowerShell 5.1+
- Python 3.10+

## Service Installation (Administrator)

1. Open PowerShell as Administrator in the repository directory.
2. Run the installer:

   ```powershell
   ./Install-And-Monitor-OrganizerService.ps1
   ```

3. The installer will:

- Install NSSM (Non-Sucking Service Manager)
- Copy `Organizer.py` to `C:\Scripts`
- Create a Windows service named `DownloadsOrganizer`
- Configure logs in `C:\Scripts\service-logs\`

4. The service starts automatically and organizes Downloads in real time.

### One-Click Installer (Batch)

Prefer a guided setup? Run `Setup-Installer.bat` from the repository root. It provides a menu to:

- Install the Windows service (calls the PowerShell installer)
- Start the dashboard locally with prompts for credentials
- Uninstall the service via NSSM

## Local Development (No Service)

Use this for testing and dashboard development.

```bash
pip install -r requirements.txt
python Organizer.py
```

Press Ctrl+C to stop.

## Dashboard Setup

Start the dashboard for monitoring, configuration, and health checks:

```bash
pip install -r requirements.txt
python OrganizerDashboard.py
```

Access `http://localhost:5000`.

Default credentials:

- Username: `admin`
- Password: `change_this_password`

Override via environment variables:

```bash
export DASHBOARD_USER=myusername
export DASHBOARD_PASS=mypassword
python OrganizerDashboard.py
```

## Configuration

- The dashboard reads and writes `organizer_config.json` for routes and thresholds.
- Organizer.py contains a hardcoded `EXTENSION_MAP`. If you add new categories via the dashboard, update Organizer.py accordingly until full dynamic loading is enabled.
- Common paths:
  - Service: `C:\Scripts\Organizer.py`
  - Config: `C:\Scripts\organizer_config.json`
  - Logs: `C:\Scripts\service-logs\`
  - Downloads: `C:\Users\{username}\Downloads\`

## Uninstall

Remove the service:

```powershell
nssm remove DownloadsOrganizer confirm
```

Optionally delete `C:\Scripts` if you want to remove files.

