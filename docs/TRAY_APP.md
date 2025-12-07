# System Tray Application

## Overview

The DownloadsOrganizeR System Tray Application provides a convenient way to manage the organizer service and dashboard directly from your Windows system tray. It runs in the background and gives you quick access to all essential functions.

## Features

### Service Management
- **View Service Status** - Real-time status updates every 5 seconds
- **Start Service** - Start the DownloadsOrganizer service
- **Stop Service** - Stop the DownloadsOrganizer service
- **Restart Service** - Restart the service (useful after config changes)

### Dashboard Management
- **Open Dashboard** - Launch dashboard in your default browser
- **Start Dashboard Server** - Run the dashboard server in background
- **Stop Dashboard Server** - Stop the dashboard server

### System Updates
- **Update from GitHub** - Pull latest updates with automatic config backup
  - Confirms before updating
  - Backs up configuration files
  - Restarts service after update
  - Shows success/error notifications

### Quick Access
- **Double-click tray icon** - Opens dashboard in browser
- **Right-click tray icon** - Shows full menu
- **System notifications** - Get notified of actions and status

## Installation

The tray app is automatically installed by the main installer. It creates:

1. **Desktop Shortcut**: `DownloadsOrganizeR Tray.lnk`
2. **Startup Shortcut**: Launches automatically on Windows startup
3. **Launcher Files**:
   - `Launch-TrayApp.bat` - Batch launcher with dependency checks
   - `Launch-TrayApp.vbs` - Silent launcher (no console window)

## Usage

### Auto-Start on Boot
The installer adds the tray app to your Startup folder, so it launches automatically when Windows starts.

### Manual Launch
- **Desktop**: Double-click "DownloadsOrganizeR Tray" shortcut
- **Command Line**: Run `Launch-TrayApp.bat` in installation directory

### Tray Icon Menu

```
DownloadsOrganizeR System Tray
├── Service: ✓ Running
├──────────────────────
├── ▶ Start Service
├── ■ Stop Service
├── ⟲ Restart Service
├──────────────────────
├── 🌐 Open Dashboard
├── ▶ Start Dashboard Server
├── ■ Stop Dashboard Server
├──────────────────────
├── ⬇ Update from GitHub
├──────────────────────
└── ✕ Exit
```

## System Requirements

- **Python 3.8+** (already installed if you installed DownloadsOrganizeR)
- **PyQt6** - Automatically installed when first launched
- **Windows** - System tray is Windows-specific

### Dependencies

The tray app uses PyQt6 for the GUI, which is added to `requirements.txt`:

```
PyQt6>=6.6,<7; sys_platform == 'win32'
```

## Technical Details

### Service Status Detection
Uses NSSM to check service status:
```powershell
nssm status DownloadsOrganizer
```

Possible statuses:
- **SERVICE_RUNNING** - Service is running (green)
- **SERVICE_STOPPED** - Service is stopped (red)
- **Other** - Service in transitional state

### Dashboard Server
When you click "Start Dashboard Server", the tray app:
1. Runs `OrganizerDashboard.py` in background
2. Hides the console window
3. Opens browser after 2-second delay
4. Tracks the process for stopping later

### Update Process
When you click "Update from GitHub":
1. Confirms action with dialog
2. Checks if directory is a git repository
3. Runs `git fetch origin main`
4. Runs `git pull origin main`
5. Restarts service with NSSM
6. Shows success/error notification

## Troubleshooting

### Tray Icon Not Appearing

**Cause:** PyQt6 not installed

**Solution:**
```powershell
pip install PyQt6
```

Or run `Launch-TrayApp.bat` which auto-installs dependencies.

### "NSSM not found" Error

**Cause:** NSSM not in system PATH

**Solution:**
```powershell
# Add NSSM to PATH or use full path in code
$env:PATH += ";C:\Program Files\DownloadsOrganizeR"
```

Alternatively, reinstall using the official installer.

### Service Status Shows "Timeout"

**Cause:** NSSM command taking too long

**Solution:**
- Check if service is responding
- Restart Windows
- Reinstall service

### Tray App Crashes on Startup

**Cause:** Missing Python dependencies

**Solution:**
```powershell
pip install -r requirements.txt
```

### Update Fails with "Not a git repository"

**Cause:** Installation was moved or not cloned from GitHub

**Solution:**
Reinstall using the official installer to ensure proper git repository setup.

## Configuration

### Installation Paths

The tray app reads installation paths from `.install_path` marker file:

```json
{
  "install_dir": "C:\\Program Files\\DownloadsOrganizeR",
  "data_dir": "C:\\ProgramData\\DownloadsOrganizeR",
  "config_dir": "C:\\ProgramData\\DownloadsOrganizeR\\config",
  "log_dir": "C:\\ProgramData\\DownloadsOrganizeR\\logs"
}
```

### Custom Icon

To use a custom icon, place `logo.png` in `static/img/` directory. The tray app will automatically use it.

## Command-Line Options

### Batch Launcher (`Launch-TrayApp.bat`)
```batch
Launch-TrayApp.bat
```
- Checks Python availability
- Auto-installs PyQt6 if missing
- Launches with `pythonw` (no console)

### VBS Launcher (`Launch-TrayApp.vbs`)
```vbscript
wscript Launch-TrayApp.vbs
```
- Silent launch (no windows)
- Used by desktop and startup shortcuts

### Direct Python Launch
```powershell
python OrganizerTrayApp.py
# or for no console:
pythonw OrganizerTrayApp.py
```

## Best Practices

1. **Keep Running** - Let the tray app run in background for quick access
2. **Use Shortcuts** - Desktop and startup shortcuts are pre-configured
3. **Update Regularly** - Use the tray app's update button to stay current
4. **Monitor Status** - Status updates every 5 seconds automatically
5. **Dashboard Server** - Start dashboard server via tray for integrated experience

## Uninstallation

The tray app is removed by the main uninstaller. Manually remove:

1. **Exit tray app** - Right-click → Exit
2. **Desktop shortcut**: `%USERPROFILE%\Desktop\DownloadsOrganizeR Tray.lnk`
3. **Startup shortcut**: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\DownloadsOrganizeR Tray.lnk`
4. **Files**: Remove `OrganizerTrayApp.py`, `Launch-TrayApp.bat`, `Launch-TrayApp.vbs`

## Security

- Requires administrator privileges for service management (NSSM commands)
- Git operations run with user's credentials
- No sensitive data stored
- Dashboard server runs on localhost only

## Advanced Usage

### Multiple Instances

Only one instance should run at a time. The app doesn't enforce this, but multiple instances may conflict when managing the same service.

### Custom Service Name

If you renamed the service, edit `OrganizerTrayApp.py`:

```python
self.service_name = "YourServiceName"
```

### Custom Dashboard Port

If dashboard runs on different port, edit `OrganizerTrayApp.py`:

```python
self.dashboard_port = 8080  # Your port
```

## See Also

- [System Update Documentation](SYSTEM_UPDATE.md)
- [Installation Guide](INSTALL.md)
- [Service Management](FEATURES.md)

