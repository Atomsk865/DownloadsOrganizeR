# DownloadsOrganizeR

DownloadsOrganizeR is a Windows-based service and web dashboard that automatically organizes files in your Downloads folder into intuitive categories (Images, Videos, Documents, Archives, Audio, Installers, Code, Data, Apps, and Other). It monitors your Downloads in real time, moves files to categorized subfolders, and provides a browser-based dashboard for visibility, configuration, and health monitoring.

This README is user‑centric: quick install, how it works, features, configuration, and troubleshooting. For deeper details, see `docs/`.

- Supported OS: Windows (service). Development can run cross‑platform for the dashboard, but organizing service targets Windows.

## Quick Start

1. Install prerequisites

   - Windows 10/11
   - PowerShell 5.1+
   - Python 3.10+

2. Install the service (Administrator)

   - Open PowerShell as Admin in the repo folder
   - Run:

     ```powershell
     ./Install-And-Monitor-OrganizerService.ps1
     ```

   - This installs NSSM, copies `Organizer.py` to `C:\Scripts`, and creates a Windows service `DownloadsOrganizer`.

3. Start the Dashboard (optional for monitoring)

  Run:

  ```bash
  pip install -r requirements.txt
  python OrganizerDashboard.py
  ```

  Visit `http://localhost:5000` (default credentials: `admin` / `change_this_password`)

Want more detail? See `docs/INSTALL.md`.

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

- Organizer service: `C:\Scripts\Organizer.py`
- Config: `C:\Scripts\organizer_config.json`
- Service logs: `C:\Scripts\service-logs\`
- Downloads: `C:\Users\{username}\Downloads\`

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
