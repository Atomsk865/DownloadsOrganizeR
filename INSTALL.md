# DownloadsOrganizeR - Installation Guide

## Quick Install (Windows)

### Prerequisites
- Windows 10/11 or Windows Server 2016+
- Administrator privileges
- Internet connection

### One-Command Install

Open PowerShell **as Administrator** and run:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; `
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/Install-DownloadsOrganizeR.ps1" -OutFile "$env:TEMP\Install-DownloadsOrganizeR.ps1"; `
& "$env:TEMP\Install-DownloadsOrganizeR.ps1"
```

### What the Installer Does

1. **Checks System Requirements**
   - Verifies Python 3.8+ is installed
   - Prompts to install Python if missing

2. **Chooses Installation Location**
   - Default: `C:\Program Files\DownloadsOrganizeR` (recommended - industry standard)
   - Alternative: `C:\DownloadsOrganizeR` (legacy/simple mode)
   - Custom path option available during installation
   - Program Files installations automatically use `C:\ProgramData\DownloadsOrganizeR` for config/logs

3. **Downloads Latest Version**
   - Clones from GitHub (if Git available)
   - Downloads ZIP as fallback

4. **Installs Dependencies**
   - Upgrades pip
   - Installs all requirements from requirements.txt

5. **Creates Windows Service**
   - Installs NSSM (service manager)
   - Creates and starts "DownloadsOrganizer" service
   - Configures automatic startup

6. **Sets Up Health Monitor**
   - Creates scheduled task
   - Checks service every 5 minutes
   - Auto-restarts if service stops

7. **Creates Desktop Shortcut**
   - "DownloadsOrganizeR Dashboard" shortcut
   - Automatically starts dashboard if not running
   - Opens browser to http://localhost:5000

## Installation Options

### Interactive Install (Recommended)
```powershell
.\Install-DownloadsOrganizeR.ps1
```

### Custom Installation Path
```powershell
.\Install-DownloadsOrganizeR.ps1 -InstallPath "D:\MyApps\DownloadsOrganizeR"
```

### Unattended Install
```powershell
.\Install-DownloadsOrganizeR.ps1 -Unattended
```

### Skip Python Check
```powershell
.\Install-DownloadsOrganizeR.ps1 -SkipPythonCheck
```

## Manual Installation

If you prefer manual installation:

1. **Install Python 3.8+**
   - Download from https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH"

2. **Clone Repository**
   ```powershell
   # Replace <INSTALL_DIR> with your chosen installation path
   git clone https://github.com/Atomsk865/DownloadsOrganizeR.git <INSTALL_DIR>
   cd <INSTALL_DIR>
   
   # Example using default location:
   # git clone https://github.com/Atomsk865/DownloadsOrganizeR.git C:\DownloadsOrganizeR
   # cd C:\DownloadsOrganizeR
   ```

3. **Install Dependencies**
   ```powershell
   python -m pip install -r requirements.txt
   ```

4. **Run Installer Script**
   ```powershell
   .\Install-And-Monitor-OrganizerService.ps1
   ```

## Post-Installation

### Access Dashboard
- Click desktop shortcut: **DownloadsOrganizeR Dashboard**
- Or visit: http://localhost:5000
- Default credentials: `admin` / `change_this_password`

### Verify Service Status
```powershell
Get-Service DownloadsOrganizer
```

### Check Health Monitor
```powershell
Get-ScheduledTask -TaskName "DownloadsOrganizer-HealthMonitor"
```

### View Logs
Service logs location:
```
<INSTALL_DIR>\service-logs\
├── organizer_stdout.log
├── organizer_stderr.log
└── health-monitor.log

# Example (if using default installation path):
# C:\DownloadsOrganizeR\service-logs\
```

## Uninstallation

### Using Uninstaller
```powershell
<INSTALL_DIR>\Uninstall.ps1

# Example: C:\DownloadsOrganizeR\Uninstall.ps1
```

### Manual Uninstall
```powershell
# Stop and remove service
nssm stop DownloadsOrganizer
nssm remove DownloadsOrganizer confirm

# Remove scheduled task
Unregister-ScheduledTask -TaskName "DownloadsOrganizer-HealthMonitor" -Confirm:$false

# Remove desktop shortcut
Remove-Item "$([Environment]::GetFolderPath('Desktop'))\DownloadsOrganizeR Dashboard.lnk"

# Remove installation directory (replace with your actual path)
Remove-Item <INSTALL_DIR> -Recurse -Force
# Example: Remove-Item C:\DownloadsOrganizeR -Recurse -Force
```

## Troubleshooting

### Python Not Found
**Error**: `Python not found in PATH`

**Solution**: 
1. Reinstall Python with "Add to PATH" option
2. Or manually add Python to PATH:
   ```powershell
   $env:Path += ";C:\Python3X;C:\Python3X\Scripts"
   ```

### Service Won't Start
**Error**: Service status shows "Stopped"

**Solution**:
1. Check logs: `<INSTALL_DIR>\service-logs\organizer_stderr.log`
2. Verify Python dependencies: `python -m pip check`
3. Manually test organizer: `python <INSTALL_DIR>\Organizer.py`

   (Replace `<INSTALL_DIR>` with your installation path, e.g., `C:\DownloadsOrganizeR`)

### Dashboard Not Loading
**Error**: Browser shows connection error

**Solution**:
1. Check if dashboard is running:
   ```powershell
   Get-Process python | Where-Object {$_.CommandLine -like "*SortNStoreDashboard*"}
   ```
2. Try manually starting from your installation directory:
   ```powershell
   cd <INSTALL_DIR>
   python SortNStoreDashboard.py
   ```
2. Start manually:
   ```powershell
   cd C:\DownloadsOrganizeR
   python SortNStoreDashboard.py
   ```
3. Check firewall settings for port 5000

### Permission Denied
**Error**: Access denied during installation

**Solution**: Run PowerShell as Administrator
```powershell
Start-Process powershell -Verb RunAs
```

## Advanced Configuration

### Change Dashboard Port
Edit `sortnstore_config.json`:
```json
{
  "dashboard_port": 5000
}
```

Then restart the dashboard.

### Custom File Categories
Edit `organizer_config.json`:
```json
{
  "routes": {
    "Images": ["jpg", "png", "gif"],
    "Documents": ["pdf", "docx", "txt"]
  }
}
```

### Configure Watch Folders
Use the dashboard:
1. Navigate to **File Organization** module
2. Add custom watch folders
3. Configure organization rules

## System Requirements

### Minimum
- Windows 10/11 (64-bit)
- Python 3.8+
- 2 GB RAM
- 500 MB disk space

### Recommended
- Windows 10/11 (64-bit)
- Python 3.10+
- 4 GB RAM
- 1 GB disk space

## Support

- **GitHub Issues**: https://github.com/Atomsk865/DownloadsOrganizeR/issues
- **Documentation**: See project README.md
- **Logs**: Check `service-logs` directory

## License

See LICENSE file in the installation directory.
