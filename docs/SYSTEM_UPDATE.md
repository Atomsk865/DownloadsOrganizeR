# System Update Feature

## Overview

The System Update feature allows you to pull the latest updates from the GitHub main branch directly through the dashboard, with automatic configuration backup and import capabilities.

## Key Features

### 1. One-Click Updates
- Pull latest code from GitHub main branch
- Automatic service restart after update (Windows NSSM)
- Git operations handled safely with proper error handling

### 2. Automatic Config Backup
All configuration files are automatically backed up before updating:
- `organizer_config.json` - Main organizer settings
- `dashboard_config.json` - Dashboard user settings
- `dashboard_branding.json` - Branding customization
- `sortnstore_config.json` - Alternative config file

**Backup Location:** `C:\Program Files\DownloadsOrganizeR\Backups\Configs\{TIMESTAMP}\`

**Timestamp Format:** `YYYYMMDD_HHMMSS` (e.g., `20231207_143022`)

### 3. Config Import Tool
- View all available backups with timestamps
- Select specific config file to restore
- Pre-import backup created (`.before_import` suffix)
- Service restart recommended after import

## Usage

### Updating the System

1. Navigate to the Dashboard
2. Scroll to the **System Update** section
3. Click **"Update from GitHub Main"**
4. Wait for the update process to complete
5. Review the update status and backup information

**Expected Result:**
```
✓ Update Completed!
Backup created: 20231207_143022
Location: C:\Program Files\DownloadsOrganizeR\Backups\Configs\20231207_143022
Files backed up: organizer_config.json, dashboard_config.json, ...
✓ Service restarted successfully

⚠️ Config files may need updates for new features. Use Config Import to restore settings if needed.
```

### Viewing Backups

1. Click **"View Backups"** button
2. Browse available backups by date/time
3. See which files are included in each backup

### Importing Configuration

1. Click **"View Backups"** to expand the backups list
2. Find the backup you want to restore from
3. Click **"Import"** on that backup
4. Select which config file to restore
5. Click **"Import Selected"**
6. Restart the service for changes to take effect

## Important Notes

### After Updating

⚠️ **Configuration Changes May Be Required**

New features may introduce new configuration options that don't exist in your current config. After updating:

1. Check the update notification for config warnings
2. Review your configuration files for new options
3. Use the Config Import tool to restore custom settings if needed
4. Restart the service after making changes

### Git Repository Requirement

This feature requires the installation to be a Git repository. If you installed manually or moved files, you may see:

```
Error: Not a git repository. Please reinstall using the installer.
```

**Solution:** Run the Windows installer (`Install-DownloadsOrganizeR.ps1`) which clones the repository properly.

### Service Restart

The system attempts to restart the Windows service automatically using NSSM:
```powershell
nssm restart DownloadsOrganizer
```

If automatic restart fails, manually restart the service:
```powershell
# PowerShell (as Administrator)
nssm restart DownloadsOrganizer

# Or via Services.msc
services.msc → DownloadsOrganizer → Right-click → Restart
```

## Backup Management

### Backup Structure
```
C:\Program Files\DownloadsOrganizeR\
└── Backups\
    └── Configs\
        ├── 20231207_143022\
        │   ├── organizer_config.json
        │   ├── dashboard_config.json
        │   ├── dashboard_branding.json
        │   └── sortnstore_config.json
        ├── 20231207_150035\
        │   └── ...
        └── 20231208_091500\
            └── ...
```

### Manual Backup Cleanup

Backups are not automatically deleted. To clean up old backups:

```powershell
# PowerShell - Delete backups older than 30 days
$BackupDir = "C:\Program Files\DownloadsOrganizeR\Backups\Configs"
Get-ChildItem $BackupDir | Where-Object {
    $_.CreationTime -lt (Get-Date).AddDays(-30)
} | Remove-Item -Recurse -Force
```

### Import Safety

Before importing a config, the current version is backed up with `.before_import` suffix:
- `organizer_config.json.before_import`
- `dashboard_config.json.before_import`

This allows you to quickly revert if the import causes issues.

## Troubleshooting

### Git Pull Fails

**Error:** `Git pull failed: ...`

**Solutions:**
1. Check internet connection
2. Verify GitHub is accessible
3. Check if local changes conflict:
   ```powershell
   cd "C:\Program Files\DownloadsOrganizeR"
   git status
   git stash  # Save local changes
   # Try update again
   ```

### Service Restart Fails

**Error:** Service restart failed

**Manual Solution:**
```powershell
# PowerShell as Administrator
nssm restart DownloadsOrganizer

# Check service status
nssm status DownloadsOrganizer
```

### Backup Not Found

**Error:** `Backup file not found`

**Cause:** Backup may have been manually deleted

**Solution:** Use a different backup or manually restore from:
- `C:\ProgramData\DownloadsOrganizeR\config\` (current configs)
- Previous backup timestamp

## API Endpoints

### POST `/api/system/update`
Pull updates from GitHub and backup configs.

**Response:**
```json
{
  "success": true,
  "message": "Update completed successfully",
  "backup": {
    "timestamp": "20231207_143022",
    "location": "C:\\Program Files\\DownloadsOrganizeR\\Backups\\Configs\\20231207_143022",
    "files": ["organizer_config.json", "dashboard_config.json"]
  },
  "git_output": "Already up to date.\n",
  "service_restarted": true,
  "notice": "⚠️ Config files may need updates..."
}
```

### GET `/api/system/backups`
List all available config backups.

**Response:**
```json
{
  "backups": [
    {
      "timestamp": "20231207_143022",
      "path": "C:\\Program Files\\DownloadsOrganizeR\\Backups\\Configs\\20231207_143022",
      "files": ["organizer_config.json", "dashboard_config.json"],
      "date": "2023-12-07 14:30:22"
    }
  ]
}
```

### POST `/api/system/import-config`
Import a config file from backup.

**Request Body:**
```json
{
  "timestamp": "20231207_143022",
  "config_file": "organizer_config.json"
}
```

**Response:**
```json
{
  "success": true,
  "message": "organizer_config.json imported successfully",
  "notice": "Service restart recommended for changes to take effect"
}
```

## Security Considerations

- Requires authentication (dashboard login)
- CSRF protection on all endpoints
- Git operations timeout after 30 seconds
- Backup files stored in installation directory (admin-only access)
- Pre-import backups prevent accidental data loss

## Related Features

- **Config Backup Route** (`/api/config/backup`) - Manual config backup
- **Service Management** - Start/Stop/Restart controls
- **Watch Folders** - Configuration page for folder settings
- **Dashboard Config** - User and role management

