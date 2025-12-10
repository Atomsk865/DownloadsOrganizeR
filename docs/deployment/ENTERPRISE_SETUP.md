# Enterprise Setup Guide for SortNStore

## Overview

SortNStore is designed with enterprise-grade safety features to prevent accidental file organization during deployment. This guide covers best practices for deploying SortNStore in business and enterprise environments.

## 🛡️ Enterprise Safety Philosophy

**Default Safe State**: The organizer service is **DISABLED by default** after installation. This prevents any file operations until:
- Configuration is reviewed and validated
- Watch folders are explicitly chosen
- Destination paths are verified
- The organizer is manually enabled by an administrator

This "fail-safe" approach ensures no files are accidentally moved or organized during initial deployment.

---

## 📋 Pre-Installation Checklist

### Before Installing the Service

- [ ] **Review System Requirements**
  - Windows Server 2012+ or Windows 10/11
  - Python 3.8 or higher installed
  - Administrator privileges available
  - Adequate disk space on destination drives

- [ ] **Plan Watch Folders**
  - Identify folders to monitor (e.g., Downloads, Incoming, Shared drives)
  - Verify folder paths are accessible by the service account
  - Check folder permissions (read/write required)
  - Document any network paths (UNC) or cloud storage locations

- [ ] **Plan Destination Strategy**
  - **Subfolder Mode**: Organize within each watch folder (simple, no extra configuration)
  - **Custom Base Mode**: Send all files to a single base location (centralized storage)
  - **Per-Category Mode**: Route specific categories to different locations (advanced)

- [ ] **Network/Cloud Considerations**
  - If using UNC paths (\\\\server\\share), ensure service account has access
  - If using cloud storage (OneDrive, Google Drive, Dropbox), verify sync is active
  - Test write permissions to all destination paths

- [ ] **Service Account Planning**
  - Default: Runs as LocalSystem (full access, but no network credentials)
  - Recommended: Domain/local user account with minimal required permissions
  - Document credentials if using specific service account

- [ ] **Backup Strategy**
  - Plan for configuration backups (config files stored in `C:\Scripts`)
  - Consider file backup before first run
  - Test restore procedures

---

## 🚀 Deployment Workflow

### Phase 1: Service Installation (No File Organization Yet)

1. **Run Installer as Administrator**
   ```powershell
   .\Install-And-Monitor-OrganizerService.ps1
   ```

2. **Installer Actions**
   - Copies `Organizer.py` to `C:\Scripts`
   - Copies configuration files
   - Sets `organizer_enabled=false` (SAFE MODE)
   - Installs NSSM (service wrapper)
   - Creates Windows service "DownloadsOrganizer"
   - Starts service in standby mode

3. **Service Status After Installation**
   - ✅ Service is running
   - ⚠️ Organizer is DISABLED (no file operations)
   - Service waits for Dashboard configuration

### Phase 2: Dashboard Setup

1. **Access Dashboard**
   - Open browser: `http://localhost:5000`
   - If remote: `http://<server-ip>:5000`

2. **Complete Setup Wizard** (4 Steps)
   
   **Step 1: Admin Account**
   - Create admin username and strong password
   - Password requirements enforced (12+ chars, mixed case, numbers, symbols)
   
   **Step 2: Authentication Method**
   - **Basic**: Simple username/password (default)
   - **LDAP/AD**: Active Directory integration (enterprise)
   - **Windows Auth**: Windows SSPI authentication (domain environments)
   
   **Step 3: Watch Folders & Features**
   - Select watch folders from recommended list
   - Add custom folders as needed
   - Configure optional features:
     - VirusTotal scanning (API key required)
     - Duplicate detection
     - Reporting
   
   **Step 4: Organizer Setup** ⚠️ **CRITICAL STEP**
   - **Destination Mode**: Choose subfolder, custom, or per-category
   - **Custom Destination**: Specify base path if using custom mode
   - **Enable Organizer**: Check this box to enable file organization
     - ⚠️ Leave unchecked to complete setup without enabling (safe)
     - ✅ Check to enable immediately after setup

3. **Review Configuration**
   - Verify watch folders are correct
   - Test destination paths are writable
   - Confirm service account has access to all paths

### Phase 3: Enabling and Testing

1. **Option A: Enable During Setup** (Step 4)
   - Check "Enable Organizer Service" in setup wizard
   - Service will be enabled after setup completes
   - Restart service to begin monitoring

2. **Option B: Enable After Setup** (Safer for Testing)
   - Complete setup with organizer disabled
   - Test dashboard access and authentication
   - Navigate to Settings → Service Control
   - Click "Enable Organizer Service"
   - Restart service when ready

3. **Initial Testing**
   - Place a test file in watch folder
   - Verify file is moved to correct destination
   - Check logs in Dashboard for confirmation
   - Monitor for 10-15 minutes before production use

4. **Service Restart** (Required after enabling)
   ```powershell
   Restart-Service DownloadsOrganizer
   ```
   Or use Dashboard: Settings → Service Control → Restart

---

## 🔐 Security Best Practices

### Service Account Configuration

**Scenario 1: Local Folders Only**
- Use LocalSystem account (default)
- No additional configuration needed

**Scenario 2: Network Shares (UNC Paths)**
- Create dedicated domain/local user account
- Grant read/write permissions to network shares
- Configure service to run as this account:
  ```powershell
  sc.exe config DownloadsOrganizer obj= "DOMAIN\username" password= "password"
  ```

**Scenario 3: Enterprise with Active Directory**
- Use domain service account with minimal privileges
- Apply principle of least privilege
- Regular password rotation via AD policies
- Monitor service account activity

### File System Permissions

**Minimum Required Permissions**:
- **Watch Folders**: Read, List, Execute
- **Destination Folders**: Read, Write, Create, Delete (for organizing)
- **Config Files** (`C:\Scripts`): Read, Write (for updates)
- **Log Files** (`C:\Scripts\service-logs`): Write, Append

**Recommended ACLs**:
```
Watch Folders:       Administrators (Full), Service Account (Read, List)
Destination Folders: Administrators (Full), Service Account (Modify)
Config Files:        Administrators (Full), Service Account (Read)
Log Files:           Administrators (Full), Service Account (Write)
```

### Network Security

**Dashboard Access Control**:
- Enable HTTPS if dashboard is network-accessible
- Use strong admin passwords (enforced by setup)
- Consider Windows Auth or LDAP for enterprise environments
- Restrict dashboard port (5000) via firewall to authorized IPs

**Firewall Configuration**:
```powershell
# Allow Dashboard on port 5000 (localhost only - default)
New-NetFirewallRule -DisplayName "SortNStore Dashboard" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -Profile Private

# Or for network access (restrict to management subnet)
New-NetFirewallRule -DisplayName "SortNStore Dashboard" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -RemoteAddress "192.168.1.0/24"
```

---

## 📊 Monitoring and Validation

### Pre-Production Validation Checklist

- [ ] **Configuration Verified**
  - Watch folders exist and are accessible
  - Destination paths are writable
  - Service account has required permissions
  
- [ ] **Test File Processing**
  - Place test files (various types) in watch folder
  - Verify correct categorization
  - Confirm destination paths
  - Check file integrity (no corruption)
  
- [ ] **Log Review**
  - Check `C:\Scripts\service-logs\organizer_stdout.log`
  - Look for errors or warnings
  - Verify file operations logged correctly
  
- [ ] **Dashboard Access**
  - Admin can login successfully
  - Service status displayed correctly
  - Metrics and logs visible
  - Configuration changes apply correctly
  
- [ ] **Service Health**
  - Service starts automatically after reboot
  - Memory usage within limits (< 200MB default)
  - CPU usage acceptable (< 60% default)
  - No crashes or restarts in Event Viewer

### Ongoing Monitoring

**Dashboard Metrics** (Real-time):
- Files processed count
- Service uptime
- Memory and CPU usage
- Recent file operations
- Error/warning counts

**Windows Event Logs**:
```powershell
# Check service events
Get-EventLog -LogName Application -Source "DownloadsOrganizer" -Newest 50

# Check service status
Get-Service DownloadsOrganizer
```

**Health Check Script** (Automated):
```powershell
# Monitor-OrganizerService.ps1 (created by installer)
# Checks memory, CPU, and restarts if thresholds exceeded
# Schedule via Task Scheduler for automatic monitoring
```

---

## 🔧 Configuration Management

### Configuration Files

**Primary Config**: `C:\Scripts\organizer_config.json`
```json
{
  "organizer_enabled": false,         // Master enable/disable switch
  "destination_mode": "subfolder",    // "subfolder", "custom", or "per-category"
  "base_destination": "",             // Used in custom mode
  "watch_folders": [                  // Folders to monitor
    "C:/Users/username/Downloads"
  ],
  "routes": {                         // File type routing rules
    "Images": ["jpg", "png", "gif"],
    "Documents": ["pdf", "docx"]
  }
}
```

**Dashboard Config**: `C:\Scripts\dashboard_config.json`
```json
{
  "setup_completed": true,
  "organizer_enabled": false,
  "users": [{
    "username": "admin",
    "role": "admin",
    "password_hash": "..."
  }],
  "roles": {
    "admin": {
      "manage_service": true,
      "manage_config": true
    }
  }
}
```

### Configuration Backup Strategy

**Manual Backup**:
```powershell
# Backup configuration
Copy-Item "C:\Scripts\organizer_config.json" "C:\Backups\organizer_config_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
Copy-Item "C:\Scripts\dashboard_config.json" "C:\Backups\dashboard_config_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
```

**Automated Backup** (via Dashboard):
- Navigate to Settings → Configuration Backup
- Click "Create Backup"
- Backups stored with timestamp
- Restore from backup via UI

### Version Control (Recommended)

```powershell
# Initialize git repo for configs
cd C:\Scripts
git init
git add organizer_config.json dashboard_config.json
git commit -m "Initial configuration"

# After changes
git add -A
git commit -m "Updated watch folders"
```

---

## 🏢 Enterprise Deployment Scenarios

### Scenario 1: Department File Server

**Requirements**:
- Monitor shared network folder
- Organize into subfolder categories
- Multiple users access organized files

**Configuration**:
```json
{
  "organizer_enabled": true,
  "destination_mode": "subfolder",
  "watch_folders": [
    "\\\\fileserver\\departments\\incoming"
  ],
  "routes": {
    "Documents": ["pdf", "docx", "xlsx"],
    "Images": ["jpg", "png"],
    "Archives": ["zip", "rar"]
  }
}
```

**Service Account**: Domain account with Modify permissions on `\\\\fileserver\\departments`

### Scenario 2: Centralized Storage with Cloud Backup

**Requirements**:
- Multiple watch folders (Downloads, Shared drive)
- Organize to centralized OneDrive location
- Automatic cloud backup via OneDrive sync

**Configuration**:
```json
{
  "organizer_enabled": true,
  "destination_mode": "custom",
  "base_destination": "C:/Users/serviceaccount/OneDrive/Organized",
  "watch_folders": [
    "C:/Users/serviceaccount/Downloads",
    "\\\\fileserver\\incoming"
  ]
}
```

**Service Account**: Local/domain account with OneDrive sync configured

### Scenario 3: Multi-Tier Storage with Archives

**Requirements**:
- Active files to fast SSD
- Archives to slower NAS
- Media to dedicated media server

**Configuration**:
```json
{
  "organizer_enabled": true,
  "destination_mode": "subfolder",
  "watch_folders": ["C:/Incoming"],
  "category_destinations": {
    "Documents": "D:/ActiveFiles/Documents",
    "Archives": "\\\\nas\\archive",
    "Videos": "\\\\mediaserver\\videos",
    "Images": "\\\\mediaserver\\images"
  }
}
```

**Service Account**: Domain account with access to all network shares

---

## 🚨 Troubleshooting

### Issue: Service Running but Files Not Organizing

**Diagnosis**:
1. Check organizer status:
   ```powershell
   Get-Content C:\Scripts\organizer_config.json | Select-String "organizer_enabled"
   ```
   Expected: `"organizer_enabled": true`

2. Check logs:
   ```powershell
   Get-Content C:\Scripts\service-logs\organizer_stdout.log -Tail 50
   ```
   Look for: "ORGANIZER SERVICE IS DISABLED" message

**Resolution**:
- Navigate to Dashboard → Settings → Service Control
- Click "Enable Organizer Service"
- Restart service: `Restart-Service DownloadsOrganizer`

### Issue: Permission Denied Errors

**Diagnosis**:
```powershell
# Check service account
sc.exe qc DownloadsOrganizer | Select-String "SERVICE_START_NAME"

# Check folder permissions
Get-Acl "C:\Path\To\Folder" | Format-List
```

**Resolution**:
1. Grant service account Modify permissions on watch and destination folders
2. If using LocalSystem and accessing network, reconfigure service to use domain account
3. Restart service after permission changes

### Issue: Service Won't Start After Reboot

**Diagnosis**:
```powershell
# Check service startup type
Get-Service DownloadsOrganizer | Select-Object StartType, Status

# Check Event Viewer
Get-EventLog -LogName Application -Source "DownloadsOrganizer" -Newest 10
```

**Resolution**:
```powershell
# Set to automatic start
Set-Service DownloadsOrganizer -StartupType Automatic

# Start service
Start-Service DownloadsOrganizer
```

### Issue: Files Going to Wrong Destinations

**Diagnosis**:
1. Check current configuration:
   ```powershell
   Get-Content C:\Scripts\organizer_config.json | ConvertFrom-Json | Select-Object destination_mode, base_destination
   ```

2. Check category routing:
   ```powershell
   Get-Content C:\Scripts\organizer_config.json | ConvertFrom-Json | Select-Object -ExpandProperty routes
   ```

**Resolution**:
- Review and update `destination_mode` via Dashboard
- Verify `base_destination` path if using custom mode
- Check `category_destinations` for per-category routing
- Restart service after configuration changes

---

## 📖 Additional Resources

### Documentation Links
- **Installation Guide**: `docs/INSTALL.md`
- **Configuration Reference**: `CONFIGURATION.md`
- **API Documentation**: Dashboard → Docs → API Reference
- **Changelog**: `CHANGELOG.md`

### Support Channels
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Full docs in `/docs` directory
- **Dashboard Help**: Built-in help accessible from Dashboard UI

### Update Procedures

**Updating the Service**:
1. Stop service: `Stop-Service DownloadsOrganizer`
2. Backup configuration files
3. Replace `C:\Scripts\Organizer.py` with new version
4. Update dependencies: `pip install -r requirements.txt --upgrade`
5. Start service: `Start-Service DownloadsOrganizer`
6. Verify in logs that service started successfully

**Rolling Back**:
1. Stop service
2. Restore backed-up `Organizer.py`
3. Restore configuration files
4. Start service

---

## ✅ Post-Deployment Checklist

After completing setup and enabling the organizer:

- [ ] Service running and organizer enabled
- [ ] Test file successfully organized
- [ ] Dashboard accessible and functional
- [ ] Logs showing no errors
- [ ] Service starts automatically after reboot
- [ ] Monitoring/health checks configured
- [ ] Configuration backed up
- [ ] Documentation updated with site-specific details
- [ ] Administrator trained on Dashboard usage
- [ ] Escalation procedures documented

---

## 🎯 Key Takeaways for Enterprise Deployment

1. **Safety First**: Service installs in disabled state by default
2. **Explicit Enablement**: Administrator must consciously enable organizer
3. **Configuration Review**: Setup wizard forces review of all settings
4. **Testing Phase**: Recommended to test before enabling in production
5. **Monitoring Required**: Use Dashboard metrics and Windows Event Logs
6. **Backup Strategy**: Configuration backups essential before changes
7. **Service Account**: Use dedicated account for network/domain scenarios
8. **Security Hardening**: Apply least privilege principle to all components

---

## Document Version

- **Version**: 1.0
- **Date**: December 2025
- **Applies To**: SortNStore v2.x and later
- **Maintainer**: SortNStore Development Team

For questions or clarifications, refer to the documentation or open an issue on GitHub.
