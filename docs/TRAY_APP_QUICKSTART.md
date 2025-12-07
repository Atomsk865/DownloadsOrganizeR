# System Tray App Quick Reference

## Launch

**Auto-Start:** Launches automatically on Windows boot
**Manual:** Double-click "DownloadsOrganizeR Tray" desktop shortcut

## Quick Actions

### Service Control
- **Start**: Right-click tray → ▶ Start Service
- **Stop**: Right-click tray → ■ Stop Service  
- **Restart**: Right-click tray → ⟲ Restart Service
- **Status**: Shows in menu (updates every 5 seconds)

### Dashboard
- **Open**: Double-click tray icon OR Right-click → 🌐 Open Dashboard
- **Start Server**: Right-click → ▶ Start Dashboard Server
- **Stop Server**: Right-click → ■ Stop Dashboard Server

### System Update
1. Right-click tray → ⬇ Update from GitHub
2. Confirm action
3. Wait for update and service restart
4. Check notification

## Keyboard Shortcuts
- **Double-click tray icon** = Open dashboard in browser
- **Right-click tray icon** = Show menu

## Status Indicators

| Icon Text | Meaning |
|-----------|---------|
| Service: ✓ Running | Service is operational |
| Service: ✗ Stopped | Service is not running |
| Service: ⚠ Timeout | NSSM command timed out |
| Service: ⚠ NSSM not found | NSSM not in PATH |

## Troubleshooting

### Tray icon not showing
```powershell
pip install PyQt6
# Then restart tray app
```

### Can't control service
- Must run as Administrator for service operations
- Check NSSM is installed: `nssm status DownloadsOrganizer`

### Update fails
- Ensure installation is a git repository
- Check internet connection
- Verify GitHub access

## Files

| File | Purpose |
|------|---------|
| `OrganizerTrayApp.py` | Main application |
| `Launch-TrayApp.bat` | Launcher with checks |
| `Launch-TrayApp.vbs` | Silent wrapper |

## Shortcuts

| Location | Path |
|----------|------|
| Desktop | `%USERPROFILE%\Desktop\DownloadsOrganizeR Tray.lnk` |
| Startup | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\DownloadsOrganizeR Tray.lnk` |

## Exit Tray App
Right-click → ✕ Exit

## See Full Documentation
[TRAY_APP.md](TRAY_APP.md)

