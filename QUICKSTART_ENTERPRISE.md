# Quick Start Guide - Enterprise Setup

## For System Administrators

This is a condensed guide for deploying SortNStore in enterprise environments. For detailed information, see `ENTERPRISE_SETUP.md`.

---

## ⚡ Quick Installation (5 Minutes)

### Step 1: Install Service
```powershell
# Run as Administrator
.\Install-And-Monitor-OrganizerService.ps1
```

**What happens:**
- Service installs as "DownloadsOrganizer"
- Organizer is **DISABLED** (safe mode)
- Configuration files created in `C:\Scripts`
- Service starts but does NOT organize files yet

### Step 2: Complete Setup Wizard
1. Open browser: `http://localhost:5000/setup`
2. **Step 1**: Create admin account (strong password required)
3. **Step 2**: Choose authentication method (Basic recommended for start)
4. **Step 3**: Select watch folders (Downloads folder suggested)
5. **Step 4**: Configure organizer:
   - **Destination Mode**: Choose "Subfolder" (safest)
   - **Enable Organizer**: ⚠️ **UNCHECK** for testing (recommended)
   - Click "Complete Setup"

### Step 3: Test Configuration (IMPORTANT)
```powershell
# Check service is running
Get-Service DownloadsOrganizer

# View logs to confirm disabled state
Get-Content C:\Scripts\service-logs\organizer_stdout.log -Tail 20

# You should see: "ORGANIZER SERVICE IS DISABLED"
```

**Place a test file in your watch folder - it should NOT move**

### Step 4: Enable Organizer (When Ready)
1. Login to Dashboard: `http://localhost:5000`
2. Navigate to: **Settings** → **Service Control**
3. Click: **"Enable Organizer Service"**
4. Restart service:
   ```powershell
   Restart-Service DownloadsOrganizer
   ```

### Step 5: Verify Operation
1. Place a test file (e.g., `test.jpg`) in watch folder
2. Check Dashboard logs - should see file being organized
3. Verify file moved to correct destination (e.g., `Images` subfolder)

---

## 🎯 Common Scenarios

### Scenario A: Single User Desktop
**Goal**: Organize Downloads folder into subfolders

**Setup**:
- Watch Folder: `C:\Users\YourName\Downloads`
- Destination Mode: `Subfolder`
- Enable: Yes (after testing)

**Result**: Files organized into `Downloads\Images`, `Downloads\Documents`, etc.

### Scenario B: Shared Network Folder
**Goal**: Organize incoming files from network share

**Setup**:
- Watch Folder: `\\fileserver\incoming`
- Destination Mode: `Subfolder`
- Service Account: Domain account with network access
- Enable: After permission testing

**Service Configuration**:
```powershell
sc.exe config DownloadsOrganizer obj= "DOMAIN\svc_organizer" password= "P@ssw0rd"
Restart-Service DownloadsOrganizer
```

### Scenario C: Centralized Cloud Storage
**Goal**: Organize multiple folders to OneDrive

**Setup**:
- Watch Folders: `C:\Downloads`, `C:\Incoming`
- Destination Mode: `Custom`
- Base Destination: `C:\Users\username\OneDrive\Organized`
- Enable: After cloud sync confirmation

---

## 🔧 Configuration Cheat Sheet

### Enable/Disable via PowerShell
```powershell
# View current state
$cfg = Get-Content C:\Scripts\organizer_config.json | ConvertFrom-Json
$cfg.organizer_enabled

# Enable
$cfg.organizer_enabled = $true
$cfg | ConvertTo-Json | Set-Content C:\Scripts\organizer_config.json
Restart-Service DownloadsOrganizer

# Disable
$cfg.organizer_enabled = $false
$cfg | ConvertTo-Json | Set-Content C:\Scripts\organizer_config.json
Restart-Service DownloadsOrganizer
```

### Change Watch Folders
```powershell
$cfg = Get-Content C:\Scripts\organizer_config.json | ConvertFrom-Json
$cfg.watch_folders = @("C:\Folder1", "\\server\share")
$cfg | ConvertTo-Json | Set-Content C:\Scripts\organizer_config.json
Restart-Service DownloadsOrganizer
```

### Switch Destination Mode
```powershell
$cfg = Get-Content C:\Scripts\organizer_config.json | ConvertFrom-Json
$cfg.destination_mode = "custom"
$cfg.base_destination = "D:\Organized"
$cfg | ConvertTo-Json | Set-Content C:\Scripts\organizer_config.json
Restart-Service DownloadsOrganizer
```

---

## 🚨 Troubleshooting Quick Fixes

### Service Running but Not Organizing Files
**Check if enabled:**
```powershell
Get-Content C:\Scripts\organizer_config.json | Select-String "organizer_enabled"
# If shows: "organizer_enabled": false
# Fix: Enable via Dashboard or PowerShell
```

### Permission Denied Errors
**Fix permissions:**
```powershell
# Grant service account access
$folder = "C:\Path\To\Folder"
$acl = Get-Acl $folder
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("NT AUTHORITY\SYSTEM","Modify","Allow")
$acl.SetAccessRule($rule)
Set-Acl $folder $acl
```

### Service Won't Start
**Check logs:**
```powershell
Get-EventLog -LogName Application -Source "DownloadsOrganizer" -Newest 10
Get-Content C:\Scripts\service-logs\organizer_stderr.log
```

### Dashboard Won't Load
**Check service status:**
```powershell
Get-Service DownloadsOrganizer
# If stopped:
Start-Service DownloadsOrganizer

# Check port 5000 is not blocked:
Test-NetConnection -ComputerName localhost -Port 5000
```

---

## 📊 Monitoring Commands

### Check Service Health
```powershell
# Service status
Get-Service DownloadsOrganizer | Format-List

# Resource usage
Get-Process -Name python | Select-Object CPU,WS,PM

# Recent files organized (from logs)
Get-Content C:\Scripts\service-logs\organizer_stdout.log -Tail 50 | Select-String "Moved"
```

### Dashboard Metrics
Navigate to: `http://localhost:5000`
- **Service Status**: Top right corner
- **Files Processed**: Main dashboard card
- **Recent Activity**: Recent files table
- **Logs**: Real-time log streaming

---

## ✅ Pre-Production Checklist

Before enabling organizer in production:

- [ ] Service installed and running
- [ ] Setup wizard completed
- [ ] Watch folders accessible
- [ ] Destination paths writable
- [ ] Service account has correct permissions
- [ ] Test file successfully placed (did NOT move while disabled)
- [ ] Logs show "DISABLED" message clearly
- [ ] Dashboard accessible
- [ ] Admin can login
- [ ] Configuration backed up
- [ ] Monitoring configured

---

## 📞 Support Resources

| Issue | Resource |
|-------|----------|
| Detailed deployment | `ENTERPRISE_SETUP.md` |
| Cloud/network paths | `CLOUD_STORAGE_GUIDE.md` |
| Configuration options | `CONFIGURATION.md` |
| API reference | Dashboard → Docs |
| Bugs/features | GitHub Issues |

---

## 🎓 Key Concepts

### Organizer Enabled vs Service Running

**Service Running** (Windows Service):
- Service process is active
- Dashboard is accessible
- Can check logs and status
- **Does not mean files are being organized**

**Organizer Enabled** (Configuration Flag):
- `organizer_enabled = true` in config
- File system monitoring is active
- Files are being organized
- **Requires service to be running**

**Both must be true for file organization to occur**

### Safe Installation Philosophy

1. **Install** → Service running, organizer disabled
2. **Configure** → Setup wizard, review settings
3. **Test** → Validate permissions and paths
4. **Enable** → Explicitly activate organizer
5. **Monitor** → Watch logs and dashboard

This prevents accidental file operations during deployment.

---

## 💡 Pro Tips

1. **Always test with organizer disabled first**
2. **Use subfolder mode until familiar with custom mode**
3. **Back up configuration before changes**
4. **Monitor logs during first hour of operation**
5. **Use service account for network access**
6. **Document your configuration choices**
7. **Schedule regular config backups**
8. **Review logs weekly for errors**

---

## 🚀 Ready to Deploy?

Follow this order:
1. Read this guide (you're here! ✓)
2. Run installation script
3. Complete setup wizard (**disable organizer**)
4. Test configuration thoroughly
5. Enable organizer when ready
6. Monitor for 24 hours
7. Document your setup for team

**Need detailed help?** See `ENTERPRISE_SETUP.md` for comprehensive guidance.

---

**Document Version**: 1.0  
**Last Updated**: December 2025  
**For**: SortNStore v2.x and later
