# Installation Paths - Dynamic Configuration

## Overview

DownloadsOrganizeR now supports **fully dynamic installation paths**. All hardcoded references to `C:\Scripts` and `C:\DownloadsOrganizeR` have been replaced with configurable paths based on where the user chooses to install the application.

## Default Installation Location

- **Current Default**: `C:\Program Files\DownloadsOrganizeR` (recommended - follows Windows best practices)
- **Alternative**: `C:\DownloadsOrganizeR` (legacy/simple mode - all files in one location)
- **Previous Default**: `C:\Scripts` (deprecated)

### Windows Folder Structure

**Program Files Installation (Recommended):**
```
C:\Program Files\DownloadsOrganizeR\       [Application Files]
├── Organizer.py
├── SortNStoreDashboard.py
├── requirements.txt
└── [Other application files]

C:\ProgramData\DownloadsOrganizeR\         [Configuration & Data]
├── config\
│   ├── organizer_config.json
│   └── dashboard_config.json
└── logs\
    ├── organizer_stdout.log
    ├── organizer_stderr.log
    └── health-monitor.log
```

**Benefits:**
- ✅ Follows Microsoft Windows guidelines
- ✅ Proper permission separation (Program Files is protected)
- ✅ Enterprise-ready and IT-friendly
- ✅ Multi-user support (ProgramData is accessible to all users)
- ✅ Survives user profile changes

**Legacy/Simple Installation:**
```
<INSTALL_DIR>\                             [Everything in one place]
├── Organizer.py
├── SortNStoreDashboard.py
├── organizer_config.json
├── dashboard_config.json
└── service-logs\
```

## How Dynamic Path Detection Works

### 1. Installation Marker File

During installation, the installer creates a `.install_path` marker file in the installation directory containing the full installation path. This file is used by the dashboard and other scripts to auto-detect the installation location.

**File**: `.install_path`  
**Location**: `<INSTALL_DIR>\.install_path`  
**Content**: Single line containing the installation directory path  
**Example**: `C:\DownloadsOrganizeR`

### 2. Dashboard Auto-Detection

The dashboard (`SortNStoreDashboard.py`) includes automatic installation path detection:

```python
def get_installation_directory():
    """Detect the installation directory based on script location or config."""
    # Try to read from marker file first (created during installation)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    install_marker = os.path.join(script_dir, ".install_path")
    
    if os.path.exists(install_marker):
        try:
            with open(install_marker, 'r') as f:
                install_path = f.read().strip()
                if os.path.isdir(install_path):
                    return install_path
        except Exception:
            pass
    
    # Fallback: use script directory
    return script_dir
```

**Key Variables**:
- `INSTALL_DIR` - Detected installation directory
- `DEFAULT_LOGS_DIR` - Automatically set to `<INSTALL_DIR>\service-logs`

### 3. PowerShell Scripts

All PowerShell installation scripts now accept a configurable installation directory parameter:

**Primary Installer**: `Install-DownloadsOrganizeR.ps1`
- Interactive prompt for installation directory
- Default: `C:\DownloadsOrganizeR`
- Creates `.install_path` marker file

**Legacy Installer**: `Install-And-Monitor-OrganizerService.ps1`
- Parameter: `-ScriptsRoot`
- Default: `C:\DownloadsOrganizeR`

**Service Installer**: `dotnet/DownloadsOrganizeR.ServiceHost/Install-Service.ps1`
- Parameters: `-PythonExe`, `-ScriptPath`, `-WorkingDirectory`
- Defaults updated to `C:\DownloadsOrganizeR`

## Documentation Placeholder Convention

All documentation now uses the `<INSTALL_DIR>` placeholder for installation paths with examples showing the default location:

```powershell
# Access logs
Get-Content <INSTALL_DIR>\service-logs\organizer_stderr.log -Tail 50

# Example (using default path):
# Get-Content C:\DownloadsOrganizeR\service-logs\organizer_stderr.log -Tail 50
```

## Files Updated

### Python Scripts
- ✅ `SortNStoreDashboard.py` - Added dynamic path detection, `INSTALL_DIR` and `DEFAULT_LOGS_DIR` globals

### HTML/Frontend
- ✅ `dash/dashboard_config.html` - Scripts Root input now shows placeholder "Auto-detected from installation"
- ✅ `dash/config_modules.html` - Scripts Root input now shows placeholder "Auto-detected from installation"

### Documentation
- ✅ `INSTALL.md` - All paths converted to `<INSTALL_DIR>` with default examples
- ✅ `QUICKSTART.md` - All paths converted to `<INSTALL_DIR>` with default examples
- ✅ `readme.md` - Core paths updated to show configurable installation directory
- ✅ `docs/INSTALL.md` - All references updated
- ✅ `docs/ARCHITECTURE.md` - File paths updated
- ✅ `docs/FEATURES.md` - Log paths updated
- ✅ `docs/BUGS.md` - Path assumptions updated

### Installation Scripts
- ✅ `Install-DownloadsOrganizeR.ps1` - Creates `.install_path` marker file during installation
- ✅ `Install-And-Monitor-OrganizerService.ps1` - Default changed from `C:\Scripts` to `C:\DownloadsOrganizeR`
- ✅ `dotnet/DownloadsOrganizeR.ServiceHost/Install-Service.ps1` - All path parameters updated

### Distribution Files
- ✅ `dist/README.md` - References updated
- ✅ `dist/Setup-DownloadsOrganizeR.ps1` - Default `TargetRoot` changed
- ✅ `dist/Setup-DownloadsOrganizeR-Online.ps1` - Default `TargetRoot` changed
- ✅ `dist/EXE_INSTALLER_README.md` - Location reference updated

### Test Scripts
- ✅ `Windows-Dashboard-SmokeTest.ps1` - Default `$RepoRoot` changed to `C:\DownloadsOrganizeR`

## Configuration Files

The following configuration files are automatically created/updated with the correct installation paths during installation:

- `organizer_config.json` - Logs directory set dynamically
- `dashboard_config.json` - Paths relative to installation directory
- `dashboard_branding.json` - No path dependencies

## Service Configuration

When installed as a Windows service via NSSM, the service configuration includes:

- **AppDirectory**: Set to installation directory
- **AppStdout**: `<INSTALL_DIR>\service-logs\organizer_stdout.log`
- **AppStderr**: `<INSTALL_DIR>\service-logs\organizer_stderr.log`

## Migration from C:\Scripts

If upgrading from an older installation using `C:\Scripts`:

1. **Option 1: Reinstall (Recommended)**
   - Run the new installer with your preferred installation location
   - The installer will detect existing services and update them

2. **Option 2: Manual Migration**
   ```powershell
   # Stop existing service
   nssm stop DownloadsOrganizer
   
   # Move files
   Move-Item C:\Scripts\* C:\DownloadsOrganizeR\
   
   # Update service paths
   nssm set DownloadsOrganizer AppDirectory C:\DownloadsOrganizeR
   nssm set DownloadsOrganizer Application C:\DownloadsOrganizeR\venv\Scripts\python.exe
   nssm set DownloadsOrganizer AppParameters C:\DownloadsOrganizeR\Organizer.py
   nssm set DownloadsOrganizer AppStdout C:\DownloadsOrganizeR\service-logs\organizer_stdout.log
   nssm set DownloadsOrganizer AppStderr C:\DownloadsOrganizeR\service-logs\organizer_stderr.log
   
   # Create marker file
   "C:\DownloadsOrganizeR" | Out-File C:\DownloadsOrganizeR\.install_path -NoNewline
   
   # Start service
   nssm start DownloadsOrganizer
   ```

## Custom Installation Locations

You can install DownloadsOrganizeR to any directory:

```powershell
# Example: Install to D:\Apps\FileOrganizer
.\Install-DownloadsOrganizeR.ps1
# When prompted, enter: D:\Apps\FileOrganizer
```

**Requirements**:
- Must be a local drive (UNC paths not supported for service installation)
- User must have write permissions
- Path should not contain special characters that might cause issues with Windows services

## Environment Variables

No environment variables are required for path configuration. The system uses:
1. `.install_path` marker file (primary)
2. Script location detection (fallback)

## Troubleshooting

### Dashboard showing wrong paths
- Check `.install_path` file exists in installation directory
- Verify file contains correct path
- Restart dashboard service

### Service logs in wrong location
- Check NSSM service configuration: `nssm get DownloadsOrganizer AppStdout`
- Verify service was installed with correct paths
- Check service `AppDirectory` setting: `nssm get DownloadsOrganizer AppDirectory`

### Path contains spaces
- Always use quotes in PowerShell: `cd "C:\Program Files\DownloadsOrganizeR"`
- NSSM handles spaces in paths correctly
- Python scripts use `os.path` which handles spaces natively

## Developer Notes

When adding new features that reference file paths:

1. **Use `INSTALL_DIR` global** in `SortNStoreDashboard.py`
2. **Use `$InstallDir` parameter** in PowerShell scripts
3. **Document paths with `<INSTALL_DIR>` placeholder** in markdown files
4. **Never hardcode** `C:\Scripts` or `C:\DownloadsOrganizeR`

### Example (Python):
```python
log_file = os.path.join(INSTALL_DIR, "service-logs", "mylog.log")
```

### Example (PowerShell):
```powershell
function Do-Something {
    param([string]$InstallDir)
    $configFile = Join-Path $InstallDir "config.json"
}
```

## Testing Path Configuration

To verify dynamic path detection is working:

```powershell
# Test 1: Check marker file
Get-Content <INSTALL_DIR>\.install_path

# Test 2: Verify service paths
nssm get DownloadsOrganizer AppDirectory
nssm get DownloadsOrganizer AppStdout

# Test 3: Check dashboard detection (in Python)
python -c "import sys; sys.path.insert(0, '<INSTALL_DIR>'); from SortNStoreDashboard import INSTALL_DIR; print(INSTALL_DIR)"
```

## Related Documentation

- [INSTALL.md](INSTALL.md) - Complete installation guide
- [QUICKSTART.md](QUICKSTART.md) - Quick reference with updated paths
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture overview
