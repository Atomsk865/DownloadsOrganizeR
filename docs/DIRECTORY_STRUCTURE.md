# Directory Structure Overview

This document explains the organization of the DownloadsOrganizeR repository.

## Root Directory

The root directory contains only the essential user-facing files:

| Item | Purpose | Notes |
|------|---------|-------|
| `README.md` | Main project documentation | Start here |
| `LICENSE` | MIT License | Legal terms |
| `Organizer.py` | Core file organization service | **REQUIRED** |
| `OrganizerTrayApp.py` | Windows system tray GUI | **REQUIRED** |
| `SortNStoreDashboard.py` | Flask web dashboard | **REQUIRED** |
| `requirements.txt` | Python dependencies | Install with pip |
| `organizer_config.json` | Service configuration | User-editable |
| `dashboard_config.json` | Dashboard configuration | User-editable |

All other development files and documentation are organized in subfolders.

---

## Folder Structure

### `/docs/` - Documentation
All project documentation, guides, and references.

```
docs/
├── README.md                          # Documentation index
├── INSTALLATION.md                    # Setup & installation guide
├── CONFIGURATION.md                   # Configuration reference
├── TROUBLESHOOTING.md                 # Common issues & solutions
├── ARCHITECTURE.md                    # System design & components
├── CHANGELOG.md                       # Version history
├── API.md                             # REST API documentation
├── DIRECTORY_STRUCTURE.md             # This file
├── images/                            # Screenshots & diagrams
│   └── Dashboard.png
├── backups/                           # Configuration backups
│   ├── organizer_config.json.bak
│   └── dashboard_config.json.bak
└── ... (54+ markdown files)
```

**Use Case**: Read documentation to understand, configure, and troubleshoot the system.

---

### `/installers/` - Installation & Build Scripts
Scripts for building, packaging, and installing the application.

```
installers/
├── Setup-Installer.ps1               # Main PowerShell installer (Windows)
├── Setup-Installer.bat               # Batch file installer (Windows)
├── build.py                          # Build script
├── build_exe.py                      # Windows EXE builder
├── installer_builder.py              # GUI installer builder
├── Install-And-Monitor-OrganizerService.ps1  # Service installer
└── SortNStore.spec                   # PyInstaller spec file
```

**Use Case**: Run these scripts to build releases, create installers, or package the application for distribution.

**Example**:
```bash
python installers/build_exe.py  # Build Windows EXE
```

---

### `/scripts/` - Utility & Development Scripts
Maintenance, testing, and diagnostic scripts.

```
scripts/
├── check_environment.py              # Environment verification
├── check_routes.py                   # Flask route checking
├── preflight_check.py                # Pre-flight system checks
├── Monitor-OrganizerService.ps1      # Service monitoring script
├── Windows-Dashboard-SmokeTest.ps1   # Dashboard testing script
├── BatchOrganizer.py                 # Batch file organization
├── demo_v2_features.py               # Feature demonstrations
├── test_*.py                         # Test scripts (various)
└── ... (utility scripts)
```

**Use Case**: Run these for development, testing, and maintenance tasks.

**Example**:
```bash
python scripts/check_environment.py    # Verify environment
python scripts/preflight_check.py      # Run pre-flight checks
```

---

### `/SortNStoreDashboard/` - Dashboard Package
The Python package containing the Flask web application.

```
SortNStoreDashboard/
├── __init__.py                       # Package initialization & create_app()
├── config_runtime.py                 # Configuration management
├── cache.py                          # Caching utilities
├── rate_limiting.py                  # Rate limiting
├── query_optimizer.py                # Query optimization
├── auth/
│   ├── __init__.py
│   └── auth.py                       # Authentication module (LDAP, Windows, Basic)
├── helpers/
│   ├── __init__.py
│   └── helpers.py                    # Utility functions
└── routes/
    ├── __init__.py
    ├── dashboard.py                  # Main dashboard route
    ├── login.py                      # Login/logout
    ├── api_*.py                      # API endpoints (30+ routes)
    ├── start_service.py              # Service control
    ├── update_config.py              # Configuration updates
    ├── metrics.py                    # System metrics
    ├── auth_*.py                     # Authentication routes
    └── ... (and many more)
```

**Use Case**: This is the Flask application code. Most users won't modify this.

---

### `/dash/` - HTML Templates
Flask HTML templates for the web dashboard UI.

```
dash/
├── dashboard.html                    # Main dashboard page
├── login.html                        # Login page
├── dashboard_base.html               # Base template
├── dashboard_config.html             # Configuration page
├── dashboard_scripts.html            # JavaScript includes
├── statistics_full.html              # Statistics view
├── modules/
│   ├── recent_files.html             # Recent files widget
│   ├── statistics.html               # Statistics widget
│   ├── resource_monitor.html         # Resource monitoring widget
│   ├── file_categories.html          # File categories widget
│   ├── system_info.html              # System info widget
│   └── ... (more widgets)
└── ... (template files)
```

**Note**: Flask requires these to be in the root or specified template folder. Placed here for organization.

---

### `/static/` - Static Assets
CSS, JavaScript, images, and other static files.

```
static/
├── css/
│   ├── style.css                     # Main stylesheet
│   ├── dashboard.css                 # Dashboard styles
│   └── ... (more stylesheets)
├── js/
│   ├── dashboard.js                  # Main dashboard JavaScript
│   ├── api.js                        # API client
│   └── ... (more scripts)
└── img/
    ├── logo.png                      # Application logo
    ├── icon.ico                      # Favicon
    └── ... (images)
```

**Use Case**: Web UI styling and interactivity.

---

### `/tests/` - Unit & Integration Tests
Test files for the application.

```
tests/
├── test_setup_validation.py          # Setup validation tests
└── ... (other test files)
```

**Use Case**: Run tests to verify application functionality.

**Example**:
```bash
pytest tests/
```

---

### `/config/` - Configuration Data Files
Runtime configuration and state files.

```
config/
└── json/
    ├── file_moves.json               # File movement history
    ├── downloads_dashboard.json      # Dashboard data
    └── ... (config files)
```

**Note**: These are generated/updated at runtime.

---

### `/examples/` - Example Configurations
Example configuration files and templates.

```
examples/
├── batch_organizer_config.json       # Example batch config
├── config_basic_auth.json            # Basic auth example
├── config_ldap_auth.json             # LDAP auth example
├── config_windows_auth.json          # Windows auth example
└── ... (more examples)
```

**Use Case**: Reference these when setting up custom configurations.

---

### `/releases/` - Release Files
Official release packages and documentation.

```
releases/
└── v1.0-beta/
    ├── RELEASE_NOTES.md
    ├── Setup-Offline.ps1
    └── ... (release files)
```

---

### `/dotnet/` - .NET Integration (Optional)
C# service host for Windows integration (optional component).

```
dotnet/
├── README.md
└── DownloadsOrganizeR.ServiceHost/   # .NET service host
```

---

### `/dist/` - Build Artifacts
Generated distribution files (EXE, ZIP, etc.).

```
dist/
├── README.md
├── Setup-DownloadsOrganizeR.ps1
├── Setup-DownloadsOrganizeR-Online.ps1
└── ... (built artifacts)
```

**Note**: Ignored in git (.gitignore).

---

## File Organization Logic

### User-Facing Files (Root)
- Entry point scripts users run directly
- Configuration files users edit
- Essential documentation (README, LICENSE)

### Development Files (Subfolders)
- Developers: See `/docs/ARCHITECTURE.md` and package code
- Installers: Run scripts in `/installers/`
- Maintainers: See `/scripts/` for utilities

### Runtime Files (Auto-generated)
- `/config/json/` - Generated at runtime
- `/dist/` - Built artifacts (ignored in git)
- `.bak` files - Configuration backups

---

## Installation Impact

When installed as a Windows service:

```
C:\Program Files\DownloadsOrganizeR\
└── (Copy of: Organizer.py, SortNStoreDashboard.py, OrganizerTrayApp.py, SortNStoreDashboard/, dash/, static/)

C:\ProgramData\DownloadsOrganizeR\
├── organizer_config.json          (user edits here)
├── dashboard_config.json          (user edits here)
└── logs/
    ├── organizer.log
    ├── dashboard.log
    └── dashboard_tray_errors.log
```

The installer copies essential files to Program Files and stores user data in ProgramData.

---

## Contributing

When adding new files:

1. **Core application code**: Add to `/SortNStoreDashboard/` package
2. **Routes/APIs**: Add to `/SortNStoreDashboard/routes/`
3. **Documentation**: Add to `/docs/`
4. **Tests**: Add to `/tests/`
5. **Scripts**: Add to `/scripts/` (utilities) or `/installers/` (build scripts)
6. **Templates**: Add to `/dash/`
7. **Styles/JS**: Add to `/static/`

---

## Quick Navigation

| Task | Location |
|------|----------|
| View documentation | `/docs/` |
| Install application | `/installers/` |
| Run utility scripts | `/scripts/` |
| Understand architecture | `/docs/ARCHITECTURE.md` |
| Configure settings | Root: `organizer_config.json`, `dashboard_config.json` |
| View examples | `/examples/` |
| Run tests | `pytest tests/` |
| View code | `/SortNStoreDashboard/` |

---

## Summary

The reorganization ensures:
- ✅ Clean root directory (8 essential files)
- ✅ Logical folder organization
- ✅ Professional presentation
- ✅ Easy navigation
- ✅ Clear separation of concerns
- ✅ User-friendly structure

