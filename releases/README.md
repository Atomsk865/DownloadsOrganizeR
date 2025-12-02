# DownloadsOrganizeR Releases

This directory contains versioned offline installer packages for historical reference and rollback capability.

## Structure

Each release folder (e.g., `v1.0-beta/`) contains:
- `DownloadsOrganizeR-v*.zip` - Complete offline package with all files
- `RELEASE_NOTES.md` - Version-specific changes and features
- `Setup-Offline.ps1` - Installer script for that version

## Using Offline Installers

1. Download the desired version's `.zip` file
2. Extract to a temporary location
3. Run PowerShell as Administrator
4. Execute:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\Setup-Offline.ps1
```

## Using Online Installer (Latest)

For the latest version from GitHub:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\dist\Setup-DownloadsOrganizeR-Online.ps1
```

Options:

- `-Branch <branch>` - Specify branch (default: Prod-Beta)
- `-InstallService` - Install Windows service
- `-NoStartDashboard` - Skip auto-start dashboard

## Version History

### v1.0-beta (December 2, 2025)

- Initial production release
- Setup wizard with Basic/LDAP/Windows auth
- Dashboard with role-based access control
- Automated file organization service
- Health monitoring and metrics
- Setup reset capability for admins
