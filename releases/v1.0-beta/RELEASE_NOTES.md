# Release Notes - v1.0-beta

**Release Date:** December 2, 2025  
**Branch:** Prod-Beta

## Features

### Core Functionality
- **Automated File Organization**: Real-time monitoring of Downloads folder with category-based organization (Images, Videos, Documents, Archives, Audio, Code, Executables, Installers, Compressed)
- **Windows Service**: Run as background service using NSSM
- **Web Dashboard**: Flask-based UI for monitoring and configuration

### Setup Wizard
- **First-Time Setup Flow**: Guided configuration on initial dashboard launch
- **Multi-Auth Support**: Choose between Basic, LDAP, or Windows authentication
- **Validation**: Server and client-side validation for credentials and auth settings
- **Setup Reset**: Admins can re-run setup wizard from config page

### Authentication & Security
- **Basic Auth**: bcrypt-hashed passwords with configurable admin credentials
- **LDAP/AD Integration**: Support for LDAP/Active Directory with group filtering
- **Windows Auth**: Native Windows authentication with domain and group support
- **Auth Fallback**: Optional fallback to Basic auth when primary method fails
- **Role-Based Access Control**: Admin and viewer roles with granular rights

### Dashboard Features
- **Real-Time Metrics**: CPU, memory, disk, and network monitoring
- **Service Control**: Start, stop, restart organizer service
- **Log Management**: Stream and clear logs from dashboard
- **Config Editor**: JSON config editing with validation
- **Layout Customization**: Save dashboard layout preferences
- **Recent Files**: Track recently organized files with open functionality

### Configuration Management
- **Runtime Config Singleton**: Centralized config state management
- **Persistent Storage**: Configs saved to JSON with atomic updates
- **Health Thresholds**: Configurable CPU and memory alerts
- **Route Customization**: Define file extension to folder mappings

## Installation

### Online Installer (Recommended)
Downloads latest from GitHub:
```powershell
PowerShell -ExecutionPolicy Bypass -File .\dist\Setup-DownloadsOrganizeR-Online.ps1
```

### Offline Installer
Extract release package and run:
```powershell
PowerShell -ExecutionPolicy Bypass -File .\Setup-Offline.ps1
```

### Options
- `-TargetRoot <path>` - Install location (default: C:\Scripts)
- `-InstallService` - Install and start Windows service
- `-NoStartDashboard` - Skip dashboard auto-start

## Requirements

- **OS**: Windows 10/11 or Windows Server 2016+
- **Python**: 3.12 or higher
- **NSSM**: For Windows service installation (optional)
- **Ports**: 5000 (dashboard), configurable

## Known Issues

- LDAP SSL certificate validation requires system trust
- Windows auth requires domain-joined machine for domain users
- Service logs directory must be writable by service account

## Upgrade Notes

First release - no upgrade path needed.

## Testing

Includes:
- Automated test suite (pytest)
- Windows smoke test script
- Integration tests for auth and setup flows

## Files Included

- `Organizer.py` - Core file organization service
- `OrganizerDashboard.py` - Flask dashboard application
- `OrganizerDashboard/` - Modular routes, auth, helpers
- `dash/` - HTML templates
- `requirements.txt` - Python dependencies
- `organizer_config.json` - Service configuration
- `dashboard_config.json` - Dashboard and user config
- `Install-And-Monitor-OrganizerService.ps1` - Service installer
- `Windows-Dashboard-SmokeTest.ps1` - Validation script

## Security Notes

- Default admin password should be changed immediately
- Store configs in secure locations
- Use HTTPS reverse proxy for production deployments
- LDAP bind credentials stored in plaintext in config (use service accounts with minimal permissions)

## Support

- GitHub Issues: https://github.com/Atomsk865/DownloadsOrganizeR/issues
- Documentation: See README.md and doc files in repository
