# DownloadsOrganizeR - AI Coding Agent Instructions

## Project Overview

**DownloadsOrganizeR** is a Windows-based file organization service that automatically categorizes downloaded files into folders by type (Images, Videos, Documents, etc.) using real-time file system monitoring. It comprises three main components:

1. **Organizer.py** - Core service that watches the Downloads folder and organizes files
2. **OrganizerDashboard.py** - Flask web UI for monitoring, configuration, and service control
3. **Install-And-Monitor-OrganizerService.ps1** - Windows service installer using NSSM

## Architecture & Data Flow

### Component Interaction
```
User Downloads → [Watchdog Observer] → Organizer.py → Categorizes Files
                                              ↓
                                    organizer_config.json (rules)
                                              ↓
                                    OrganizerDashboard.py
                                    (reads logs & config)
```

### Key Configuration File: `organizer_config.json`
- **routes**: Maps folder names to file extensions (e.g., "Images": ["jpg", "png", ...])
- **memory_threshold_mb**: Health monitor memory limit (default: 200MB)
- **cpu_threshold_percent**: Health monitor CPU limit (default: 60%)
- **logs_dir**: Service log directory (default: `C:\Scripts\service-logs`)

Dashboard reads this file to display routes and thresholds; changes via the web UI update both the config and the running service configuration.

### File Organization Logic (Organizer.py)

**Extension-to-Category Mapping:**
- Organizer.py has hardcoded `EXTENSION_MAP` (currently uses 9 categories + "Other" fallback)
- `organizer_config.json` is the source of truth for dynamic category configuration (used by Dashboard)
- On file arrival: extension matched → target category → `C:\Users\{username}\Downloads\{Category}\` folder

**Unique Path Handling:**
- If file exists in destination, append `({counter})` to filename (e.g., `image (1).jpg`)
- Uses `get_unique_path()` function

**Watch Events:** 
Monitors three events via `DownloadsHandler`:
- `on_created` - New file detected
- `on_moved` - File moved into Downloads
- `on_modified` - File modification (queues re-organization)

## Critical Developer Workflows

### Running Organizer Service Locally (Development)
```powershell
cd C:\Scripts
python Organizer.py
# Prompts for Windows username, then monitors Downloads folder
# Press Ctrl+C to stop
```

### Running Dashboard Locally
```bash
pip install -r requirements.txt
python OrganizerDashboard.py
# Access at http://localhost:5000
# Default credentials: admin / change_this_password (env vars: DASHBOARD_USER, DASHBOARD_PASS)
```

### Service Installation (Windows Admin)
```powershell
# Run as Administrator
.\Install-And-Monitor-OrganizerService.ps1
# Auto-elevates if not run as Admin
# Copies Organizer.py to C:\Scripts
# Installs NSSM and creates Windows service "DownloadsOrganizer"
```

### Removing Service
```powershell
nssm remove DownloadsOrganizer confirm
```

## Project-Specific Patterns

### Configuration Sync Pattern
- **Challenge:** Organizer.py has hardcoded `EXTENSION_MAP`; Dashboard reads from `organizer_config.json`
- **Current Design:** Dashboard is the config source for web users; Organizer.py needs updates to read config at startup
- **When Modifying Rules:** Update `organizer_config.json` routes section; if adding new categories, also update `EXTENSION_MAP` in Organizer.py and Dashboard's `DEFAULT_CONFIG`

### Logging Pattern
- **Organizer.py:** Logs to `C:\Users\{username}\Downloads\organizer.log` (INFO + console output)
- **Service:** Logs to `C:\Scripts\service-logs\organizer_stdout.log` and `organizer_stderr.log` (configured in NSSM)
- **Dashboard:** Streams and manages logs via web UI with file truncation

### Ignored Files
Organizer.py skips:
- Files in `IGNORE_FILES` set: `{"dashboard_config.json", "organizer.log"}`
- Files with extensions in `IGNORE_EXTENSIONS`: `{".crdownload", ".part", ".tmp"}` (incomplete downloads)

### Dashboard State Management
- Uses basic HTTP Basic Auth (env vars: `DASHBOARD_USER`, `DASHBOARD_PASS`)
- Service status queried via platform-specific commands (psutil)
- Config changes persisted to `organizer_config.json`
- Bootstrap 5 for UI (no client-side state management)

## Integration Points & Dependencies

### External Libraries
- **watchdog 6.0.0** - File system event monitoring
- **psutil 7.1.3** - Process/system metrics for Dashboard
- **Flask 3.1.2** - Dashboard web framework
- **gputil 1.4.0** - GPU info (optional, graceful degradation if missing)

### Windows-Specific Integration
- **NSSM (Non-Sucking Service Manager)** - Runs Organizer.py as Windows service
- Service runs as `$env:USERDOMAIN\$env:USERNAME` (current user) by default
- PowerShell 5.1+ required; scripts use `-ExecutionPolicy Bypass`

### Expected File Paths
- **Organizer.py** source: Same folder as installer script
- **Deployment target:** `C:\Scripts\Organizer.py`
- **Config:** `C:\Scripts\organizer_config.json` (or local if running standalone)
- **Service logs:** `C:\Scripts\service-logs\`
- **Downloads folder:** Auto-detected as `C:\Users\{username}\Downloads\`

## Common Modifications & Tips

### Adding a New File Category
1. Add to `EXTENSION_MAP` in **Organizer.py** and `DEFAULT_CONFIG` in **OrganizerDashboard.py**
2. Update `organizer_config.json` routes section
3. Restart service or Dashboard

### Debugging File Organization Issues
- Check `C:\Users\{username}\Downloads\organizer.log` for specific file movements
- Verify extension is in config (case-insensitive in code)
- Confirm destination folder exists and is writable

### Environment Variable Configuration (Dashboard)
- `DASHBOARD_USER` - Basic auth username (default: "admin")
- `DASHBOARD_PASS` - Basic auth password (default: "change_this_password")

## Files Reference

| File | Purpose |
|------|---------|
| `Organizer.py` | Core file watcher & organizer service |
| `OrganizerDashboard.py` | Flask web dashboard (~960 lines) |
| `organizer_config.json` | Runtime configuration (routes, thresholds) |
| `Install-And-Monitor-OrganizerService.ps1` | Windows service installer |
| `Monitor-OrganizerService.ps1` | Health check script (auto-generated) |
| `requirements.txt` | Python dependencies |
