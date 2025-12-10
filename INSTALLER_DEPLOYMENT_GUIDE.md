# Installer Deployment Guide

**Quick reference for different installation scenarios**

---

## Installation Scenarios

### 1️⃣ Personal User (Simplest)

**Target:** Individual users, home automation, personal projects

```powershell
irm https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1 | iex
```

**What you get:**
- Installed to: `C:\DownloadsOrganizeR`
- Optional Windows service
- Full interactive prompts
- Personal-friendly defaults

**Time:** ~5 minutes

---

### 2️⃣ Small Business (Recommended)

**Target:** Small teams, workgroups, 5-50 users

```powershell
# Option A: Interactive (Recommended)
$params = @{
    InstallDir = 'C:\DownloadsOrganizeR'
    DeploymentMode = 'Enterprise'
    InstallService = $true
    EnableLogging = $true
}
irm https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1 | iex -ArgumentList @(($params | ConvertTo-Json))

# Option B: Script-based (for multiple machines)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1" -OutFile "C:\Scripts\install.ps1"
foreach ($computer in $computers) {
    Invoke-Command -ComputerName $computer -FilePath C:\Scripts\install.ps1 -ArgumentList @(
        @{
            InstallDir = 'C:\Program Files\DownloadsOrganizeR'
            DeploymentMode = 'Enterprise'
            InstallService = $true
            EnableLogging = $true
        } | ConvertTo-Json
    )
}
```

**What you get:**
- Installed to: `C:\Program Files\DownloadsOrganizeR`
- Automatic Windows service
- Audit logging enabled
- Enterprise configuration
- Installation records for each machine

**Time:** ~10 minutes per machine

---

### 3️⃣ Enterprise (Large Scale)

**Target:** Large organizations, 50+ users, domain environments

```powershell
# Script deployment via Group Policy or Configuration Manager
$installScript = @"
`$params = @{
    InstallDir = 'C:\Program Files\DownloadsOrganizeR'
    DeploymentMode = 'Enterprise'
    InstallService = `$true
    Silent = `$true
    EnableLogging = `$true
    SkipHealthCheck = `$false
}
`$installerUri = 'https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1'
Invoke-Expression ((Invoke-WebRequest -Uri `$installerUri).Content) @params
"@

# Deploy via SCCM/Intune/Group Policy
```

**What you get:**
- Installed to: `C:\Program Files\DownloadsOrganizeR`
- Fully automated, no user interaction
- Complete audit trail
- Restricted permissions (Enterprise)
- Installation validation
- Detailed logging for compliance

**Time:** ~5 minutes per machine (no user interaction)

---

### 4️⃣ CI/CD Pipeline (Automated)

**Target:** Infrastructure as Code, DevOps, automated deployments

```powershell
# PowerShell Core (pwsh) compatible
param(
    [string]$TargetDir = '/opt/DownloadsOrganizeR',
    [bool]$EnableService = $true
)

# Download and execute installer
$Uri = 'https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1'
$params = @{
    InstallDir = $TargetDir
    DeploymentMode = 'Enterprise'
    InstallService = $EnableService
    Silent = $true
    EnableLogging = $true
}

Invoke-Expression ((Invoke-WebRequest -Uri $Uri).Content) @params

# Verify installation
$config = Get-Content "$TargetDir\config\installation_record.json" | ConvertFrom-Json
Write-Host "Installation verified: $($config.InstallationDate)"
```

**What you get:**
- Automated deployment
- No user interaction
- Comprehensive logging
- Verification capability
- Integration with CI/CD
- Version tracking

**Time:** ~3 minutes

---

### 5️⃣ Air-Gapped Environment (Offline)

**Target:** Secure networks, no internet access, isolated systems

```powershell
# Step 1: On a system with internet, download the installer
# Run on internet-connected machine:
$Uri = 'https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1'
Invoke-WebRequest -Uri $Uri -OutFile C:\Offline\install.ps1

# Also download the latest release manually from:
# https://github.com/Atomsk865/DownloadsOrganizeR/releases

# Step 2: Copy to air-gapped system and execute:
# (on offline system)
& C:\Offline\install.ps1 `
    -InstallDir 'C:\Program Files\DownloadsOrganizeR' `
    -DeploymentMode Enterprise `
    -SkipHealthCheck `
    -EnableLogging
```

**What you get:**
- Works without internet
- Offline deployment capability
- No GitHub API calls
- Manual verification possible
- Full audit trail

**Time:** ~5 minutes

---

### 6️⃣ Development/Testing

**Target:** Developers, testing environments, pre-deployment

```powershell
# Local development with source installation
git clone https://github.com/Atomsk865/DownloadsOrganizeR.git
cd DownloadsOrganizeR

# Manual installation for development
python -m pip install -r requirements.txt
python Organizer.py  # Run organizer
python SortNStoreDashboard.py  # Run dashboard

# Or use the installer for testing
.\installers\install.ps1 `
    -InstallDir 'C:\Dev\DownloadsOrganizeR' `
    -DeploymentMode Personal `
    -EnableLogging
```

**What you get:**
- Development environment
- Full source code access
- Easy debugging
- Optional service installation
- Isolated from production

**Time:** ~5 minutes

---

## Decision Tree

```
Are you a...

├─ Individual/Home User?
│  └─ Use Personal Mode (one-liner)
│     irm ... | iex
│
├─ Small Business (5-50 users)?
│  └─ Use Enterprise Mode (interactive)
│     With EnableLogging enabled
│
├─ Large Enterprise (50+ users)?
│  └─ Use Enterprise Mode (silent)
│     Via Group Policy or SCCM
│
├─ CI/CD or DevOps?
│  └─ Use Silent Mode
│     With SkipHealthCheck (if needed)
│
├─ Air-Gapped Network?
│  └─ Download manually first
│     Then deploy offline
│
└─ Developer/Testing?
   └─ Clone repo + manual install
      Or use installer with EnableLogging
```

---

## Comparison Table

| Scenario | Mode | Service | Logging | User Prompts | Audit |
|----------|------|---------|---------|--------------|-------|
| **Personal** | Personal | Optional | Optional | Yes | Basic |
| **Small Business** | Enterprise | Yes | Yes | Yes | Standard |
| **Enterprise** | Enterprise | Yes | Yes | No | Detailed |
| **CI/CD** | Enterprise | Yes | Yes | No | Detailed |
| **Air-Gapped** | Enterprise | Yes | Yes | No | Full |
| **Development** | Personal | Optional | Yes | Yes | Basic |

---

## Parameter Combinations

### Minimal Install (Personal)
```powershell
irm https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1 | iex
```
Default: Personal mode, interactive, no logging

### Standard Install (Business)
```powershell
irm ... | iex -ArgumentList @((@{
    DeploymentMode = 'Enterprise'
    EnableLogging = $true
} | ConvertTo-Json))
```
Sets: Enterprise mode, logging enabled

### Production Install (Enterprise)
```powershell
irm ... | iex -ArgumentList @((@{
    DeploymentMode = 'Enterprise'
    InstallService = $true
    Silent = $true
    EnableLogging = $true
} | ConvertTo-Json))
```
Sets: Enterprise mode, service, silent, logging

### Minimal CI/CD Install
```powershell
irm ... | iex -ArgumentList @((@{
    Silent = $true
} | ConvertTo-Json))
```
Sets: Silent mode (fastest, minimal output)

---

## Verification After Installation

### Check Installation Record
```powershell
# Personal mode
$record = Get-Content 'C:\DownloadsOrganizeR\config\installation_record.json' | ConvertFrom-Json

# Enterprise mode
$record = Get-Content 'C:\Program Files\DownloadsOrganizeR\config\installation_record.json' | ConvertFrom-Json

$record | Format-List
```

### Verify Service (if installed)
```powershell
Get-Service DownloadsOrganizeR
```

### Check Installation Log
```powershell
# Open log file
$logFile = Get-ChildItem $env:TEMP -Filter "DownloadsOrganizeR-Install*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $logFile.FullName
```

### Verify Python Dependencies
```powershell
# Test imports
python -c "import flask, watchdog, psutil; print('All dependencies OK')"
```

---

## Troubleshooting by Scenario

### Personal Mode Issues
- **Service won't start**: Ensure Python is in PATH
- **Dashboard won't load**: Check if port 5000 is available
- **Files not organizing**: Verify config.json settings

### Enterprise Deployment Issues
- **Permission denied**: Check C:\Program Files permissions
- **Service fails to start**: Check NSSM configuration
- **Logging disabled**: Enable with `-EnableLogging` flag

### Silent Deployment Issues
- **Script continues despite errors**: Check error log
- **Installation incomplete**: Review installation_record.json
- **No feedback**: Enable logging to troubleshoot

---

## Best Practices by Role

### System Administrators
1. Use Enterprise mode for all deployments
2. Enable logging for compliance
3. Save installation records
4. Test on dev environment first
5. Document custom parameters

### Developers
1. Use Personal mode for development
2. Clone repo for source access
3. Enable logging for debugging
4. Use SkipHealthCheck only when necessary
5. Keep installer script updated

### DevOps Engineers
1. Use Silent mode for automation
2. Implement health checks
3. Version control installer parameters
4. Log all deployments
5. Plan for rollback scenarios

### IT Managers
1. Require Enterprise mode
2. Maintain audit trails (EnableLogging)
3. Test thoroughly before rollout
4. Plan deployment timeline
5. Document procedures

---

**Reference:** Installer v2.0 (Production Ready)  
**Last Updated:** December 2025  
**Compatible:** Windows 10/11, Windows Server 2016+
