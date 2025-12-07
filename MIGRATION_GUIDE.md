# Migration Guide - Upgrading to Program Files Installation

## Overview

As of the latest version, DownloadsOrganizeR follows Windows best practices by installing to `C:\Program Files\DownloadsOrganizeR` with configuration and logs in `C:\ProgramData\DownloadsOrganizeR`.

If you're upgrading from an older installation using `C:\Scripts` or `C:\DownloadsOrganizeR`, this guide will help you migrate.

## Check Your Current Installation

```powershell
# Check where your service is installed
nssm get DownloadsOrganizer AppDirectory

# Check current log location
nssm get DownloadsOrganizer AppStderr
```

## Migration Options

### Option 1: Fresh Install (Recommended)

The easiest approach is to perform a fresh installation using the new installer:

```powershell
# Stop and backup existing installation
Stop-Service DownloadsOrganizer

# Backup your config files
Copy-Item C:\Scripts\organizer_config.json C:\Temp\organizer_config_backup.json -ErrorAction SilentlyContinue
Copy-Item C:\DownloadsOrganizeR\organizer_config.json C:\Temp\organizer_config_backup.json -ErrorAction SilentlyContinue
Copy-Item C:\Scripts\dashboard_config.json C:\Temp\dashboard_config_backup.json -ErrorAction SilentlyContinue
Copy-Item C:\DownloadsOrganizeR\dashboard_config.json C:\Temp\dashboard_config_backup.json -ErrorAction SilentlyContinue

# Run the new installer (it will detect and upgrade existing service)
.\Install-DownloadsOrganizeR.ps1

# Restore your custom configurations
Copy-Item C:\Temp\organizer_config_backup.json "C:\ProgramData\DownloadsOrganizeR\config\organizer_config.json" -ErrorAction SilentlyContinue
Copy-Item C:\Temp\dashboard_config_backup.json "C:\ProgramData\DownloadsOrganizeR\config\dashboard_config.json" -ErrorAction SilentlyContinue

# Clean up old installation (optional)
Remove-Item C:\Scripts -Recurse -Force
# OR
Remove-Item C:\DownloadsOrganizeR -Recurse -Force
```

### Option 2: Manual Migration

If you prefer to manually migrate your existing installation:

#### Step 1: Stop the Service

```powershell
nssm stop DownloadsOrganizer
```

#### Step 2: Create New Directory Structure

```powershell
# Create Program Files directory
New-Item -ItemType Directory -Path "C:\Program Files\DownloadsOrganizeR" -Force

# Create ProgramData directories
New-Item -ItemType Directory -Path "C:\ProgramData\DownloadsOrganizeR\config" -Force
New-Item -ItemType Directory -Path "C:\ProgramData\DownloadsOrganizeR\logs" -Force
```

#### Step 3: Move Files

```powershell
# Determine your current installation path
$OldPath = "C:\Scripts"  # OR "C:\DownloadsOrganizeR"

# Move application files to Program Files
Get-ChildItem $OldPath -File -Filter "*.py" | Copy-Item -Destination "C:\Program Files\DownloadsOrganizeR"
Copy-Item "$OldPath\requirements.txt" "C:\Program Files\DownloadsOrganizeR\" -ErrorAction SilentlyContinue
Copy-Item "$OldPath\nssm.exe" "C:\Program Files\DownloadsOrganizeR\" -ErrorAction SilentlyContinue

# Move configuration files to ProgramData
Copy-Item "$OldPath\organizer_config.json" "C:\ProgramData\DownloadsOrganizeR\config\" -ErrorAction SilentlyContinue
Copy-Item "$OldPath\dashboard_config.json" "C:\ProgramData\DownloadsOrganizeR\config\" -ErrorAction SilentlyContinue
Copy-Item "$OldPath\dashboard_branding.json" "C:\ProgramData\DownloadsOrganizeR\config\" -ErrorAction SilentlyContinue

# Move logs (optional - or start fresh)
if (Test-Path "$OldPath\service-logs") {
    Copy-Item "$OldPath\service-logs\*" "C:\ProgramData\DownloadsOrganizeR\logs\" -ErrorAction SilentlyContinue
}
```

#### Step 4: Update Service Configuration

```powershell
$NssmPath = "C:\Program Files\DownloadsOrganizeR\nssm.exe"
$PythonExe = (Get-Command python).Source

# Update service paths
& $NssmPath set DownloadsOrganizer AppDirectory "C:\Program Files\DownloadsOrganizeR"
& $NssmPath set DownloadsOrganizer Application $PythonExe
& $NssmPath set DownloadsOrganizer AppParameters "C:\Program Files\DownloadsOrganizeR\Organizer.py"

# Update log paths
& $NssmPath set DownloadsOrganizer AppStdout "C:\ProgramData\DownloadsOrganizeR\logs\organizer_stdout.log"
& $NssmPath set DownloadsOrganizer AppStderr "C:\ProgramData\DownloadsOrganizeR\logs\organizer_stderr.log"

# Set environment variables for data directories
& $NssmPath set DownloadsOrganizer AppEnvironmentExtra "ORGANIZER_DATA_DIR=C:\ProgramData\DownloadsOrganizeR"
& $NssmPath set DownloadsOrganizer AppEnvironmentExtra "ORGANIZER_CONFIG_DIR=C:\ProgramData\DownloadsOrganizeR\config"
& $NssmPath set DownloadsOrganizer AppEnvironmentExtra "ORGANIZER_LOG_DIR=C:\ProgramData\DownloadsOrganizeR\logs"
```

#### Step 5: Create Installation Marker

```powershell
# Create .install_path marker file
$markerData = @{
    install_dir = "C:\Program Files\DownloadsOrganizeR"
    data_dir = "C:\ProgramData\DownloadsOrganizeR"
    config_dir = "C:\ProgramData\DownloadsOrganizeR\config"
    log_dir = "C:\ProgramData\DownloadsOrganizeR\logs"
} | ConvertTo-Json

$markerData | Out-File "C:\Program Files\DownloadsOrganizeR\.install_path" -Encoding utf8
```

#### Step 6: Restart Service

```powershell
nssm start DownloadsOrganizer
Start-Sleep -Seconds 3

# Verify service is running
Get-Service DownloadsOrganizer
```

#### Step 7: Update Desktop Shortcut

```powershell
# Remove old shortcut
Remove-Item "$([Environment]::GetFolderPath('Desktop'))\DownloadsOrganizeR Dashboard.lnk" -ErrorAction SilentlyContinue

# Create new shortcut (or run the installer to do this automatically)
# The installer's New-DashboardShortcut function will create the proper shortcut
```

#### Step 8: Verify and Clean Up

```powershell
# Test dashboard
Start-Process "http://localhost:5000"

# Check logs
Get-Content "C:\ProgramData\DownloadsOrganizeR\logs\organizer_stdout.log" -Tail 20

# If everything works, remove old installation
# CAUTION: Only do this after verifying everything works!
Remove-Item $OldPath -Recurse -Force
```

## Troubleshooting Migration

### Service Won't Start

1. Check Python path is correct:
   ```powershell
   nssm get DownloadsOrganizer Application
   python --version
   ```

2. Check environment variables are set:
   ```powershell
   nssm get DownloadsOrganizer AppEnvironmentExtra
   ```

3. Check logs:
   ```powershell
   Get-Content "C:\ProgramData\DownloadsOrganizeR\logs\organizer_stderr.log" -Tail 50
   ```

### Dashboard Not Loading

1. Verify installation marker exists:
   ```powershell
   Get-Content "C:\Program Files\DownloadsOrganizeR\.install_path"
   ```

2. Check if dashboard process is running:
   ```powershell
   Get-Process python | Where-Object {$_.CommandLine -like "*SortNStoreDashboard*"}
   ```

3. Manually start dashboard to see errors:
   ```powershell
   cd "C:\Program Files\DownloadsOrganizeR"
   python SortNStoreDashboard.py
   ```

### Config Not Found

If the dashboard or service can't find configuration:

1. Verify files exist in ProgramData:
   ```powershell
   Get-ChildItem "C:\ProgramData\DownloadsOrganizeR\config"
   ```

2. Check file permissions (ProgramData should be accessible to all users):
   ```powershell
   icacls "C:\ProgramData\DownloadsOrganizeR"
   ```

3. If files are missing, copy from backup or let the service create defaults

### Permission Issues

If you get permission errors:

```powershell
# Grant Users group read/write access to ProgramData folder
icacls "C:\ProgramData\DownloadsOrganizeR" /grant Users:(OI)(CI)M /T

# Program Files should remain protected (read-only for Users)
icacls "C:\Program Files\DownloadsOrganizeR" /grant Users:(OI)(CI)RX /T
```

## Benefits After Migration

After migrating to the new structure, you'll have:

- ✅ **Better Security**: Application files protected in Program Files
- ✅ **Proper Permissions**: ProgramData accessible to all users with appropriate ACLs
- ✅ **Enterprise Ready**: Follows Microsoft guidelines for installed applications
- ✅ **Multi-User Support**: Configuration accessible across user accounts
- ✅ **IT-Friendly**: Standard location that IT departments expect
- ✅ **Easier Backups**: Configuration in one central location

## Rolling Back

If you need to roll back to the old installation:

1. Stop service: `nssm stop DownloadsOrganizer`
2. Restore old service configuration (use your backup commands)
3. Copy files back to original location
4. Update service paths back to old location
5. Restart service: `nssm start DownloadsOrganizer`

## Support

If you encounter issues during migration:

- Check service logs: `C:\ProgramData\DownloadsOrganizeR\logs\organizer_stderr.log`
- Review this guide carefully
- Open an issue on GitHub with error details
- Consider fresh install as the safest migration path
