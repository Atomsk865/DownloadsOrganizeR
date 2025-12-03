# Architecture Overview

## Components
- **Organizer.py** – Watches Downloads and moves files to categorized subfolders.
- **OrganizerDashboard.py** – Flask-based web UI for monitoring, configuration, and service control.
- **Install-And-Monitor-OrganizerService.ps1** – Installer using NSSM to run Organizer as a Windows service.

## Data Flow

```
User Downloads → [Watchdog Observer] → Organizer.py → Categorizes Files
                                              ↓
                                    organizer_config.json (routes)
                                              ↓
                                    OrganizerDashboard.py
                                    (reads logs & config)
```

## Configuration
- `organizer_config.json` contains routes and thresholds; dashboard is the source of truth for web edits.
- Organizer.py currently has an `EXTENSION_MAP` that should be kept in sync when categories change.

## Logging
- Organizer logs in `C:\Users\{username}\Downloads\organizer.log`.
- Service logs in `C:\Scripts\service-logs\` when installed via NSSM.

## Expected Paths
- Organizer service: `C:\Scripts\Organizer.py`
- Config: `C:\Scripts\organizer_config.json`
- Service logs: `C:\Scripts\service-logs\`
- Downloads: `C:\Users\{username}\Downloads\`

