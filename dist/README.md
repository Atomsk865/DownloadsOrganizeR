# DownloadsOrganizeR - Production Setup (Prod-Beta)

This folder contains streamlined Windows installers to deploy DownloadsOrganizeR as a local service with a web dashboard.

## Installation Methods

### Online Installer (Recommended)

Downloads the latest version from GitHub automatically:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\dist\Setup-DownloadsOrganizeR-Online.ps1
```

**Advantages:**

- Always gets the latest version
- Smaller download size
- Automatic updates available

### Offline Installer

Use the pre-packaged release from `releases/` folder:

1. Download `releases/v1.0-beta/DownloadsOrganizeR-v1.0-beta.zip`
2. Extract to a temporary location
3. Run:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\Setup-Offline.ps1
```

**Advantages:**

- No internet required
- Version pinning for stability
- Historical rollback capability

### Local Development Installer

For development/testing from local repo:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\dist\Setup-DownloadsOrganizeR.ps1
```

## What the Installer Does

1. Creates `C:\Scripts` target folder and copies core files
2. Creates a Python virtual environment under `C:\Scripts\venv`
3. Installs required packages from `requirements.txt`
4. Initializes default configs (`organizer_config.json`, `dashboard_config.json`)
5. Optionally installs NSSM service `DownloadsOrganizer`
6. Starts the dashboard web UI

## Installer Options

All installers support these parameters:

- `-TargetRoot <path>` - Installation directory (default: `C:\Scripts`)
- `-InstallService` - Install Windows service via NSSM (requires NSSM on PATH)
- `-InstallDotnetService` - Install Windows service via .NET Service Host (requires .NET SDK or prebuilt publish)
- `-NoStartDashboard` - Skip automatic dashboard startup
- `-ServiceName <name>` - Custom service name (default: `DownloadsOrganizer`)

**Online installer additional options:**

- `-Branch <branch>` - GitHub branch to download (default: `Prod-Beta`)
- `-GitHubRepo <owner/repo>` - Repository to download from

**Service installation methods:**

- **NSSM** (traditional): Use `-InstallService` flag; requires NSSM installed
- **.NET Service Host** (native): Use `-InstallDotnetService` flag; auto-publishes or uses prebuilt binaries

## Quick Start

1. Run installer as Administrator
2. Open <http://localhost:5000>
3. Complete first-time setup wizard:
   - Set admin credentials
   - Choose authentication method (Basic/LDAP/Windows)
   - Configure domain/LDAP settings if needed
4. Monitor file organization in Downloads folder

## Requirements

- **OS:** Windows 10/11 or Windows Server 2016+
- **Python:** 3.12 or higher (added to PATH)
- **NSSM:** For Windows service (optional)
- **Ports:** 5000 (dashboard, configurable)

## Troubleshooting

- **Python not found:** Ensure Python 3.12+ is installed and added to system PATH
- **LDAP errors:** Verify certificates/trust for `ldaps://` URLs
- **Service won't start:** Check service logs in `C:\Scripts\service-logs\`
- **Port conflict:** Dashboard port 5000 already in use; change in config
- **Permission denied:** Run PowerShell as Administrator

## Version Management

See `releases/README.md` for version history and rollback instructions.

