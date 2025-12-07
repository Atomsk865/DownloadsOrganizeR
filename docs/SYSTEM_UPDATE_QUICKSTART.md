# System Update Quick Reference

## Quick Actions

### Update System
1. Dashboard → System Update section
2. Click "Update from GitHub Main"
3. Wait for completion
4. Review backup location in status message

### View Backups
1. Click "View Backups" button
2. Browse by timestamp
3. Click "Import" on desired backup

### Import Config
1. Select backup timestamp
2. Choose config file (radio button)
3. Click "Import Selected"
4. Restart service for changes

## Backup Locations

```
C:\Program Files\DownloadsOrganizeR\Backups\Configs\{YYYYMMDD_HHMMSS}\
```

Example: `C:\Program Files\DownloadsOrganizeR\Backups\Configs\20231207_143022\`

## Files Backed Up

- `organizer_config.json` - Main organizer settings
- `dashboard_config.json` - Dashboard/user settings
- `dashboard_branding.json` - Branding customization
- `sortnstore_config.json` - Alternative config

## Manual Service Restart

```powershell
# PowerShell as Administrator
nssm restart DownloadsOrganizer
```

## Emergency Config Restore

If update breaks something:

```powershell
# Navigate to config directory
cd "C:\ProgramData\DownloadsOrganizeR\config"

# Restore from .before_import backup
copy organizer_config.json.before_import organizer_config.json

# Restart service
nssm restart DownloadsOrganizer
```

## Clean Old Backups

```powershell
# Delete backups older than 30 days
$BackupDir = "C:\Program Files\DownloadsOrganizeR\Backups\Configs"
Get-ChildItem $BackupDir | Where-Object {
    $_.CreationTime -lt (Get-Date).AddDays(-30)
} | Remove-Item -Recurse -Force
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not a git repository" | Reinstall using official installer |
| Git pull fails | Check internet, verify GitHub access |
| Service restart fails | Manually run `nssm restart DownloadsOrganizer` |
| Backup not found | Check `C:\Program Files\DownloadsOrganizeR\Backups\Configs\` exists |
| Import fails | Verify timestamp and file name are correct |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/system/update` | POST | Pull updates and backup configs |
| `/api/system/backups` | GET | List all backups |
| `/api/system/import-config` | POST | Import config from backup |

## Status Messages

### Success
```
✓ Update Completed!
Backup created: 20231207_143022
✓ Service restarted successfully
⚠️ Config files may need updates for new features.
```

### Errors
- **Git fetch failed** - Network or GitHub connectivity issue
- **Git pull failed** - Local changes conflict or network issue
- **Config backup failed** - Check disk space and permissions
- **Not a git repository** - Reinstall required

## Best Practices

1. **Review Notifications** - Read config change warnings after updates
2. **Test After Update** - Verify organizer still works as expected
3. **Keep Recent Backups** - Don't delete last 2-3 backups
4. **Document Custom Settings** - Know what you've changed from defaults
5. **Monitor First Run** - Check logs after update for any errors

## See Also

- [Full Documentation](SYSTEM_UPDATE.md)
- [Installation Guide](INSTALL.md)
- [Features](FEATURES.md)
- [Troubleshooting](BUGS.md)

