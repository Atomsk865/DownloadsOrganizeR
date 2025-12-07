# DownloadsOrganizeR

DownloadsOrganizeR is a Windows-based service and web dashboard that automatically organizes files in your Downloads folder into intuitive categories (Images, Videos, Documents, Archives, Audio, Installers, Code, Data, Apps, and Other). It monitors your Downloads in real time, moves files to categorized subfolders, and provides a browser-based dashboard for visibility, configuration, and health monitoring.

This README is user‑centric: quick install, how it works, features, configuration, and troubleshooting. For deeper details, see `docs/`.

- Supported OS: Windows (service). Development can run cross‑platform for the dashboard, but organizing service targets Windows.

## Quick Start

### Automated Installation (Recommended)

**One-Command Install** - Open PowerShell as Administrator:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; `
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/Install-DownloadsOrganizeR.ps1" -OutFile "$env:TEMP\Install-DownloadsOrganizeR.ps1"; `
& "$env:TEMP\Install-DownloadsOrganizeR.ps1"
```

**Or download and run:**
1. Download `Install-DownloadsOrganizeR.ps1` or `Install.bat`
2. Right-click → **Run as Administrator**
3. Follow the installation wizard

The installer will:
- ✅ Check/install Python 3.8+ (if needed)
- ✅ Download latest version from GitHub
- ✅ Install all dependencies
- ✅ Create and start Windows service
- ✅ Set up health monitoring
- ✅ Create desktop shortcut for dashboard

**Access Dashboard:** Click the desktop shortcut or visit `http://localhost:5000`  
**Default credentials:** `admin` / `change_this_password`

### Manual Installation

For advanced users or troubleshooting, see detailed instructions in [INSTALL.md](INSTALL.md)

## What It Does

- Watches your Downloads folder for new or changed files.
- Classifies by extension into categories.
- Moves files into categorized subfolders inside Downloads.
- Ensures unique filenames if duplicates exist (`name (1).ext`).
- Skips incomplete downloads (e.g., `.crdownload`, `.tmp`).
- Provides a web dashboard for monitoring, configuration, logs, and health.

## Key Features

- Real‑time organization using Watchdog.
- Extension‑to‑category routing with configurable rules.
- Collision‑safe moves via unique paths.
- Dashboard modules: Recent Files, Duplicates, File Categories, Resource Monitor, System Info, Statistics, Settings, Admin Tools, Reports & Analytics, User Links.
- Health thresholds (CPU, memory) configurable.
- Service logging and dashboard log management.

See `docs/FEATURES.md` for full descriptions and scenarios.

## How It Works

```text
User Downloads → [Watchdog Observer] → Organizer.py → Categorizes Files
                                              ↓
                                    organizer_config.json (routes)
                                              ↓
                                    OrganizerDashboard.py
                                    (reads logs & config)
```

Core paths:

**Program Files Installation (Recommended):**
- Application: `C:\Program Files\DownloadsOrganizeR\`
- Config: `C:\ProgramData\DownloadsOrganizeR\config\`
- Logs: `C:\ProgramData\DownloadsOrganizeR\logs\`
- Downloads: `C:\Users\{username}\Downloads\`

**Legacy/Simple Installation:**
- Application: `<INSTALL_DIR>\` (e.g., `C:\DownloadsOrganizeR\`)
- Config: `<INSTALL_DIR>\`
- Logs: `<INSTALL_DIR>\service-logs\`

Learn more in `docs/ARCHITECTURE.md`.

## Configuration Overview

- The dashboard reads and writes `organizer_config.json` for routes and thresholds.
- Organizer.py currently contains a hardcoded `EXTENSION_MAP`. Keep it in sync with config when adding categories.
- Environment variables for dashboard auth:
  - `DASHBOARD_USER` (default `admin`)
  - `DASHBOARD_PASS` (default `change_this_password`)

See `docs/INSTALL.md` for configuration steps.

## Troubleshooting

- Files not moving? Check `C:\Users\{username}\Downloads\organizer.log` for details.
- Incomplete downloads are ignored until finished (`.crdownload`, `.part`, `.tmp`).
- Verify extensions exist in routes (case‑insensitive).
- Confirm destination folders are writable.
- Dashboard not loading? Ensure `pip install -r requirements.txt` and Python 3.10+.

More in `docs/BUGS.md` and `docs/INSTALL.md`.

## Uninstall

- Remove the Windows service:
  - `nssm remove DownloadsOrganizer confirm`

## License

See `LICENSE`.

## Documentation Index

- `docs/INSTALL.md` – Installation and configuration
- `docs/FEATURES.md` – Feature details and scenarios
- `docs/BUGS.md` – Known issues and limitations
- `docs/ARCHITECTURE.md` – System overview and file paths
