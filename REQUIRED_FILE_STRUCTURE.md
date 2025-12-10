# Required File Structure for SortNStore Dashboard & Organizer Integration

## Directory Structure

```
DownloadsOrganizeR/
├── Organizer.py                    # Core file organizer service
├── OrganizerTrayApp.py             # Windows system tray GUI app
├── SortNStoreDashboard.py          # MAIN: Flask dashboard entry point
├── SortNStoreDashboard/            # Flask app package
│   ├── __init__.py                 # Package initialization with create_app()
│   ├── config_runtime.py           # Configuration management
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth.py                 # Authentication module
│   ├── helpers/
│   │   ├── __init__.py
│   │   └── helpers.py              # Helper functions
│   ├── routes/                     # All route blueprints
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── update_config.py
│   │   ├── metrics.py
│   │   ├── service_name.py
│   │   ├── auth_check.py
│   │   ├── start_service.py
│   │   ├── stop_service.py
│   │   ├── restart_service.py
│   │   └── ... (all other route modules)
│   └── ... (other support modules)
├── organizer_config.json           # Main config for Organizer service
├── dashboard_config.json           # Dashboard-specific config
└── dash/                           # HTML templates (if using)
    └── *.html
```

## Deprecated/Unused Files to Remove

- `OrganizerDashboard.py` - **DUPLICATE**: This is a stub that imports from SortNStoreDashboard. Not used directly. 
  - Entry point is `SortNStoreDashboard.py` instead
  - OrganizerTrayApp.py should reference `SortNStoreDashboard.py`

## File Import Patterns

### Primary Entry Points

**Organizer.py** (Service)
- Monitors Downloads folder
- Reads `organizer_config.json` for routes
- Standalone, no Flask dependencies

**SortNStoreDashboard.py** (Dashboard)
- Flask app entry point
- Imports from `SortNStoreDashboard` package
- Reads `organizer_config.json` and `dashboard_config.json`
- **MUST start with correct package setup shim**

**OrganizerTrayApp.py** (System Tray GUI)
- Launches `SortNStoreDashboard.py` via subprocess
- Starts/stops Organizer service (NSSM)
- Manages GitHub updates
- **Should reference `SortNStoreDashboard.py`** (line 321)

### Correct Import Statements

In any file importing dashboard components:
```python
# ✓ CORRECT - Use SortNStoreDashboard package
from SortNStoreDashboard.config_runtime import get_config
from SortNStoreDashboard.auth.auth import check_auth
from SortNStoreDashboard.routes.dashboard import routes_dashboard

# ✗ WRONG - Do not use OrganizerDashboard
from OrganizerDashboard.config_runtime import get_config
```

## Key Configuration Files

- `organizer_config.json` - Defines file extension routes, thresholds, custom paths
- `dashboard_config.json` - Dashboard UI settings, users, branding
- `.install_path` - Marker file with installation paths (Windows service)

## Windows Service Integration

When installed as service via PowerShell:
- Service name: `DownloadsOrganizer`
- Runs `C:\Scripts\Organizer.py` via NSSM
- OrganizerTrayApp.py can launch dashboard and manage service
- Both read/write to `C:\ProgramData\DownloadsOrganizeR\` (data dir)
