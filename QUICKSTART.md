# DownloadsOrganizeR - Quick Reference

## Getting Started

### Launch Dashboard
- **Desktop Shortcut**: Double-click "DownloadsOrganizeR Dashboard"
- **Browser**: Visit http://localhost:5000
- **Credentials**: admin / change_this_password

### First-Time Setup
1. Click desktop shortcut to launch dashboard
2. Log in with default credentials
3. Change your password (Settings → Change Password)
4. Configure watch folders (File Organization module)
5. Customize file categories (File Categories module)

## Service Management

### Check Service Status
```powershell
Get-Service DownloadsOrganizer
```

### Start/Stop Service
```powershell
Start-Service DownloadsOrganizer
Stop-Service DownloadsOrganizer
Restart-Service DownloadsOrganizer
```

### View Service Logs
```
# Program Files installation (recommended):
C:\ProgramData\DownloadsOrganizeR\logs\
├── organizer_stdout.log (activity log)
├── organizer_stderr.log (error log)
└── health-monitor.log (health checks)

# Legacy installation:
<INSTALL_DIR>\service-logs\
```

## Dashboard Features

### Main Modules
- **File Organization** - Configure watch folders and rules
- **Statistics** - View file organization metrics
- **Recent Files** - Track recently organized files
- **File Categories** - Manage category mappings
- **Custom Routes** - Create advanced routing rules
- **Batch Organizer** - Organize existing files
- **Duplicate Detection** - Find and manage duplicates
- **System Info** - Monitor system resources
- **Settings** - Configure service and dashboard

### Common Tasks

**Add Watch Folder**
1. Navigate to File Organization module
2. Click "Add Watch Folder"
3. Browse and select folder
4. Enable monitoring

**Create Custom Category**
1. Go to File Categories module
2. Click "Add Category"
3. Enter name and extensions
4. Save changes

**Run Batch Organization**
1. Open Batch Organizer module
2. Select source folder
3. Choose destination or use default categories
4. Click "Organize Now"

## File Organization

### Default Categories
- **Images**: jpg, png, gif, bmp, svg, webp
- **Videos**: mp4, avi, mkv, mov, wmv, flv
- **Documents**: pdf, doc, docx, txt, rtf, odt
- **Archives**: zip, rar, 7z, tar, gz
- **Audio**: mp3, wav, flac, m4a, aac
- **Installers**: exe, msi, dmg, pkg
- **Code**: py, js, html, css, java, cpp
- **Data**: csv, json, xml, sql, db
- **Apps**: apk, app, deb, rpm
- **Other**: Everything else

### Organization Rules
- Files are moved to: `Downloads\{Category}\filename.ext`
- Duplicate names get numbered: `filename (1).ext`
- Incomplete downloads are ignored (`.crdownload`, `.tmp`, `.part`)
- Config files are preserved (`organizer.log`, `dashboard_config.json`)

## Configuration Files

### Main Config
```
<INSTALL_DIR>\organizer_config.json
# Default: C:\DownloadsOrganizeR\organizer_config.json
```
Contains file routes (category mappings)

### Dashboard Config
```
<INSTALL_DIR>\dashboard_config.json
# Default: C:\DownloadsOrganizeR\dashboard_config.json
```
Dashboard settings and preferences

### Branding Config
```
<INSTALL_DIR>\dashboard_branding.json
# Default: C:\DownloadsOrganizeR\dashboard_branding.json
```
Custom colors and themes

## Troubleshooting

### Service Not Running
**Check status:**
```powershell
Get-Service DownloadsOrganizer | Select-Object Status, StartType
```

**Check logs:**
```powershell
Get-Content <INSTALL_DIR>\service-logs\organizer_stderr.log -Tail 50
# Example: Get-Content C:\DownloadsOrganizeR\service-logs\organizer_stderr.log -Tail 50
```

**Restart service:**
```powershell
Restart-Service DownloadsOrganizer
```

### Dashboard Won't Load
**Check if running:**
```powershell
Get-Process python | Where-Object {$_.CommandLine -like "*SortNStoreDashboard*"}
```

**Start manually:**
```powershell
cd C:\DownloadsOrganizeR
python SortNStoreDashboard.py
```

**Check port availability:**
```powershell
Test-NetConnection -ComputerName localhost -Port 5000
```

### Files Not Being Organized
1. Verify service is running
2. Check Downloads folder is being watched
3. Review file extensions in categories
4. Check logs for errors
5. Ensure sufficient disk space

### Permission Issues
- Run as Administrator when making changes
- Ensure service account has access to Downloads
- Check NTFS permissions on watch folders

## Health Monitoring

### Automatic Health Checks
- Health monitor runs every 5 minutes
- Automatically restarts service if stopped
- Logs all health check activities

### Manual Health Check
```powershell
# Check scheduled task
Get-ScheduledTask -TaskName "DownloadsOrganizer-HealthMonitor"

# Run health check manually
<INSTALL_DIR>\Monitor-OrganizerService.ps1
# Example: C:\DownloadsOrganizeR\Monitor-OrganizerService.ps1

# View health log
Get-Content <INSTALL_DIR>\service-logs\health-monitor.log -Tail 20
# Example: Get-Content C:\DownloadsOrganizeR\service-logs\health-monitor.log -Tail 20
```

## Uninstallation

### Automated Uninstall
```powershell
<INSTALL_DIR>\Uninstall.ps1
# Example: C:\DownloadsOrganizeR\Uninstall.ps1
```

### Manual Uninstall Steps
1. Stop service: `Stop-Service DownloadsOrganizer`
2. Remove service: `<INSTALL_DIR>\nssm.exe remove DownloadsOrganizer confirm`
3. Remove task: `Unregister-ScheduledTask -TaskName "DownloadsOrganizer-HealthMonitor"`
4. Delete shortcut: `Remove-Item "$([Environment]::GetFolderPath('Desktop'))\DownloadsOrganizeR Dashboard.lnk"`
5. Delete folder: `Remove-Item <INSTALL_DIR> -Recurse -Force`

## Updates

### Check for Updates
Visit the dashboard Settings module to check for new versions

### Manual Update
```powershell
cd <INSTALL_DIR>
git pull origin main
# Example: cd C:\DownloadsOrganizeR
python -m pip install -r requirements.txt --upgrade
Restart-Service DownloadsOrganizer
```

## Support & Resources

- **Documentation**: See INSTALL.md and docs/ folder
- **GitHub Issues**: https://github.com/Atomsk865/DownloadsOrganizeR/issues
- **Logs Location**: `<INSTALL_DIR>\service-logs\` (default: `C:\DownloadsOrganizeR\service-logs\`)
- **Config Location**: `<INSTALL_DIR>\` (default: `C:\DownloadsOrganizeR\`)

## Keyboard Shortcuts

### Dashboard
- `Ctrl + K`: Quick command palette
- `Ctrl + /`: Toggle theme (light/dark)
- `Esc`: Close modals

## Security Notes

- Change default password immediately after installation
- Dashboard uses basic authentication over HTTP
- For production use, consider HTTPS with proper certificates
- Service runs with local system privileges
- Health monitor runs as SYSTEM account

## Performance Tips

1. **Optimize Watch Folders**: Monitor only necessary directories
2. **Adjust Check Frequency**: Modify in config if needed
3. **Clean Up Logs**: Rotate logs periodically to save space
4. **Exclude Large Files**: Use size filters if organizing large media
5. **Use SSD**: Install on SSD for faster file operations

## Common Configuration Examples

### Watch Multiple Folders
Edit `organizer_config.json`:
```json
{
  "watch_folders": [
    "C:\\Users\\YourName\\Downloads",
    "D:\\Shared\\Downloads"
  ]
}
```

### Custom File Extensions
```json
{
  "routes": {
    "Photos": ["jpg", "jpeg", "png", "raw", "cr2"],
    "Videos": ["mp4", "avi", "mkv", "mov"]
  }
}
```

### Change Dashboard Port
```json
{
  "dashboard_port": 8080
}
```

---

**Need more help?** See INSTALL.md or open an issue on GitHub
