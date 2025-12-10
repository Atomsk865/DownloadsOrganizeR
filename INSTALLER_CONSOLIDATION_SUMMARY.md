# Installer Consolidation Summary

**All installers consolidated into a single unified download experience.**

---

## What Changed

### ✅ New Unified Installer
- **File:** `installers/install.ps1`
- **Purpose:** Download latest version from GitHub and install
- **Size:** 9.2 KB
- **Execution:** PowerShell (requires Administrator)

### 🗑️ Removed Files
- ❌ `Setup-Installer.bat` - Windows batch installer (redundant)
- ❌ `Install-And-Monitor-OrganizerService.ps1` (root level) - Duplicate

### 📝 Updated Files
- **README.md** - Added one-liner installation command
- **docs/getting-started/README.md** - Highlighted one-liner
- **docs/getting-started/INSTALL.md** - Updated with new install.ps1
- **README.md file structure** - Updated installer reference

---

## One-Liner Installation

Copy and paste into PowerShell (run as Administrator):

```powershell
irm https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1 | iex
```

**What it does:**
- ✅ Downloads latest release from GitHub
- ✅ Extracts files to `C:\DownloadsOrganizeR`
- ✅ Installs Python dependencies (pip install -r requirements.txt)
- ✅ Creates directories for logs and config
- ✅ Optionally installs as Windows service

---

## Remaining Installers

### For Legacy/Advanced Users

**`installers/Setup-Installer.ps1`** (5.1 KB)
- Local installation from cloned repository
- More control over installation process
- Use when: Building from source locally

**`installers/Install-And-Monitor-OrganizerService.ps1`** (12 KB)
- Service setup and health monitoring
- Advanced service configuration
- Use when: Need custom service parameters

---

## Installation Decision Tree

```
Do you want to install DownloadsOrganizeR?
│
├─ YES, quickly
│  └─ Use one-liner (irm ... | iex)
│
├─ YES, from source
│  └─ Clone repo + Run Setup-Installer.ps1
│
└─ YES, with custom service config
   └─ Run Install-And-Monitor-OrganizerService.ps1
```

---

## Git Commit

**Commit:** 1aab244  
**Branch:** dev-enhancements  
**Message:** `chore: consolidate installers and add one-liner GitHub download`

**Changes:**
- Created: `installers/install.ps1` (new unified installer)
- Deleted: `Setup-Installer.bat`, `Install-And-Monitor-OrganizerService.ps1` (root)
- Updated: README.md, getting-started docs
- 7 files changed, 698 insertions(+), 464 deletions(-)

---

## Benefits

✅ **Simpler for Users**
- One clear installation method
- No confusion about which installer to use
- Professional one-liner for documentation

✅ **Always Latest**
- Automatically downloads latest release from GitHub
- No need to manually update installation script
- Fallback to main branch if no releases

✅ **Fewer Files to Maintain**
- Single source of truth for installation
- Less documentation confusion
- Cleaner repository structure

✅ **Professional Appearance**
- Easy to include in README
- Suitable for sharing on forums/forums
- Clear, modern installation experience

---

## How to Use

### Quick Start (Recommended)
1. Open PowerShell as Administrator
2. Copy the one-liner
3. Paste and press Enter
4. Follow prompts

### Full Path
1. Clone repository: `git clone https://github.com/Atomsk865/DownloadsOrganizeR.git`
2. Navigate to installers: `cd installers`
3. Run installer: `.\install.ps1`

---

## Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `installers/install.ps1` | One-liner installer (GitHub releases) | ✅ Active |
| `installers/Setup-Installer.ps1` | Local installation from source | ✅ Kept (legacy) |
| `installers/Install-And-Monitor-OrganizerService.ps1` | Service configuration | ✅ Kept (advanced) |
| `installers/Setup-Installer.bat` | Windows batch installer | ❌ Removed |
| `Install-And-Monitor-OrganizerService.ps1` (root) | Root-level duplicate | ❌ Removed |

---

## Documentation Updated

✅ **README.md** - One-liner added to Quick Start section  
✅ **docs/getting-started/README.md** - One-liner highlighted  
✅ **docs/getting-started/INSTALL.md** - Updated with new installer  
✅ **File structure references** - Updated installer paths  

---

## Status

**Complete** ✅

All installer consolidation is complete and committed to git.

Users can now install with a single command!

```powershell
irm https://raw.githubusercontent.com/Atomsk865/DownloadsOrganizeR/main/installers/install.ps1 | iex
```
