# SortNStore - Flexible Destination & Cloud Storage Guide

## Overview

SortNStore now supports **flexible destination configurations** allowing you to organize files into:
- **Local subfolders** (default behavior)
- **Custom base directories** (any local path)
- **Network paths (UNC)** - `\\server\share\folder`
- **Cloud storage** - OneDrive, Google Drive, Dropbox, iCloud, etc.
- **Per-category custom paths** - Different destination for each file type
- **Mixed mode** - Some categories local, some cloud, some network

---

## Destination Modes

### 1. Subfolder Mode (Default)

Files organized into subfolders within the watch folder.

**Configuration:**
```json
{
  "watch_folders": ["C:\\Users\\You\\Downloads"],
  "destination_mode": "subfolder"
}
```

**Result:**
```
C:\Users\You\Downloads\
  ├── Images\
  ├── Documents\
  ├── Videos\
  └── Other\
```

### 2. Custom Base Destination

All categories go to a single base location.

**Configuration:**
```json
{
  "watch_folders": ["C:\\Users\\You\\Downloads"],
  "destination_mode": "custom",
  "base_destination": "D:\\Organized"
}
```

**Result:**
```
D:\Organized\
  ├── Images\
  ├── Documents\
  ├── Videos\
  └── Other\
```

### 3. Per-Category Custom Destinations

Each category can have its own destination (local, network, or cloud).

**Configuration:**
```json
{
  "watch_folders": ["C:\\Users\\You\\Downloads"],
  "category_destinations": {
    "Images": "C:\\Users\\You\\Pictures",
    "Videos": "D:\\Media\\Videos",
    "Documents": "C:\\Users\\You\\OneDrive\\Documents",
    "Music": "\\\\NAS\\Media\\Music"
  }
}
```

**Result:**
```
C:\Users\You\Pictures\ → Images
D:\Media\Videos\ → Videos
C:\Users\You\OneDrive\Documents\ → Documents
\\NAS\Media\Music\ → Music
```

---

## Cloud Storage Integration

### Supported Cloud Services

✅ **OneDrive** (Microsoft)  
✅ **Google Drive** (Google)  
✅ **Dropbox**  
✅ **iCloud Drive** (Apple)  
✅ **Box.com**  
✅ **MEGA**  
✅ **pCloud**  
✅ **Sync.com**  

And any other cloud service that mounts as a local folder!

---

## Configuration Examples

### Example 1: OneDrive Integration

Organize files directly into OneDrive for automatic cloud sync.

```json
{
  "watch_folders": ["C:\\Users\\John\\Downloads"],
  "base_destination": "C:\\Users\\John\\OneDrive\\Organized",
  "routes": {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Documents": [".pdf", ".docx", ".txt"],
    "Videos": [".mp4", ".mkv"],
    "Other": []
  }
}
```

**Files automatically sync to OneDrive:**
```
C:\Users\John\OneDrive\Organized\
  ├── Images\      ← Synced to cloud
  ├── Documents\   ← Synced to cloud
  ├── Videos\      ← Synced to cloud
  └── Other\       ← Synced to cloud
```

---

### Example 2: Google Drive Integration

**Windows (Google Drive for Desktop):**
```json
{
  "watch_folders": ["C:\\Users\\Sarah\\Downloads"],
  "base_destination": "G:\\My Drive\\Organized"
}
```

**macOS:**
```json
{
  "watch_folders": ["/Users/sarah/Downloads"],
  "base_destination": "/Users/sarah/Google Drive/Organized"
}
```

---

### Example 3: Dropbox Integration

```json
{
  "watch_folders": ["C:\\Users\\Mike\\Downloads"],
  "category_destinations": {
    "Images": "C:\\Users\\Mike\\Dropbox\\Photos",
    "Documents": "C:\\Users\\Mike\\Dropbox\\Documents",
    "Videos": "D:\\Local\\Videos",
    "Music": "C:\\Users\\Mike\\Dropbox\\Music"
  }
}
```

**Result:**
- Images → Dropbox (cloud synced)
- Documents → Dropbox (cloud synced)
- Videos → Local drive (not synced)
- Music → Dropbox (cloud synced)

---

### Example 4: Network Storage (NAS/UNC)

```json
{
  "watch_folders": ["C:\\Users\\Admin\\Downloads"],
  "category_destinations": {
    "Videos": "\\\\NAS-Server\\Media\\Videos",
    "Music": "\\\\NAS-Server\\Media\\Music",
    "Documents": "\\\\NAS-Server\\Documents",
    "Backups": "\\\\NAS-Server\\Backups"
  },
  "retry_queue": {
    "enabled": true,
    "interval_seconds": 300,
    "max_retries": 20
  }
}
```

**Features:**
- Files move to network storage
- Automatic retry if NAS temporarily unavailable
- Retry every 5 minutes up to 20 times

---

### Example 5: Mixed Local + Cloud + Network

The ultimate flexible setup!

```json
{
  "watch_folders": ["C:\\Users\\Alice\\Downloads"],
  "category_destinations": {
    "Images": "C:\\Users\\Alice\\OneDrive\\Pictures",
    "Videos": "D:\\Local\\Videos",
    "Documents": "C:\\Users\\Alice\\Google Drive\\Documents",
    "Music": "\\\\NAS\\Media\\Music",
    "Code": "C:\\Users\\Alice\\Dropbox\\Projects",
    "Archives": "\\\\NAS\\Backups\\Archives"
  },
  "retry_queue": {
    "enabled": true,
    "interval_seconds": 600
  }
}
```

**Routing:**
```
Images    → OneDrive (cloud)
Videos    → Local drive D:
Documents → Google Drive (cloud)
Music     → Network NAS
Code      → Dropbox (cloud)
Archives  → Network NAS
```

---

### Example 6: Multi-User/Multi-Folder Setup

Watch multiple folders and organize to shared cloud storage.

```json
{
  "watch_folders": [
    "C:\\Users\\Alice\\Downloads",
    "C:\\Users\\Bob\\Downloads",
    "C:\\Users\\Carol\\Desktop"
  ],
  "base_destination": "C:\\Users\\Shared\\OneDrive\\FamilyFiles",
  "routes": {
    "Images": [".jpg", ".jpeg", ".png"],
    "Documents": [".pdf", ".docx"],
    "Videos": [".mp4", ".mov"],
    "Other": []
  }
}
```

All users' downloads organized into shared OneDrive folder.

---

## Cloud Storage Path Examples

### Windows Paths

**OneDrive:**
```
C:\Users\YourName\OneDrive\Documents
C:\Users\YourName\OneDrive - CompanyName\Files
```

**Google Drive (Drive for Desktop):**
```
G:\My Drive\Organized
G:\Shared drives\TeamDrive\Files
```

**Dropbox:**
```
C:\Users\YourName\Dropbox\Organized
```

**iCloud Drive:**
```
C:\Users\YourName\iCloudDrive\Documents
```

**Box:**
```
C:\Users\YourName\Box\Organized
```

### macOS Paths

**OneDrive:**
```
/Users/yourname/OneDrive/Documents
```

**Google Drive:**
```
/Users/yourname/Google Drive/Organized
```

**Dropbox:**
```
/Users/yourname/Dropbox/Organized
```

**iCloud Drive:**
```
/Users/yourname/Library/Mobile Documents/com~apple~CloudDocs/
```

---

## Network Paths (UNC)

### Basic UNC Path

```json
{
  "category_destinations": {
    "Videos": "\\\\server\\share\\Videos",
    "Music": "\\\\192.168.1.100\\media\\Music"
  }
}
```

### UNC with Credentials

For network paths requiring authentication, Windows will use your current credentials. For different credentials:

**Option 1: Map Network Drive**
```cmd
net use Z: \\server\share /user:domain\username password
```

Then use in config:
```json
{
  "category_destinations": {
    "Videos": "Z:\\Videos"
  }
}
```

**Option 2: Use Credential Manager**
1. Open Windows Credential Manager
2. Add network credentials
3. Use UNC path in config

---

## Advanced Configuration

### Complete Configuration Template

```json
{
  "watch_folders": [
    "C:\\Users\\You\\Downloads",
    "C:\\Users\\You\\Desktop"
  ],
  
  "destination_mode": "custom",
  "base_destination": "C:\\Users\\You\\OneDrive\\Organized",
  
  "category_destinations": {
    "Images": "C:\\Users\\You\\Pictures",
    "Videos": "D:\\Media\\Videos",
    "Documents": "C:\\Users\\You\\OneDrive\\Documents",
    "Music": "\\\\NAS\\Media\\Music",
    "Code": "C:\\Users\\You\\Dropbox\\Code",
    "Archives": "\\\\NAS\\Backups"
  },
  
  "routes": {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Music": [".mp3", ".wav", ".flac"],
    "Code": [".py", ".js", ".html", ".css"],
    "Archives": [".zip", ".rar", ".7z"],
    "Other": []
  },
  
  "custom_routes": {
    "psd": "C:\\Users\\You\\Dropbox\\Design\\Photoshop"
  },
  
  "tag_routes": {
    "invoice": "C:\\Users\\You\\OneDrive\\Finance\\Invoices",
    "receipt": "C:\\Users\\You\\OneDrive\\Finance\\Receipts"
  },
  
  "retry_queue": {
    "enabled": true,
    "interval_seconds": 600,
    "max_retries": 10
  },
  
  "duplicate_detection": {
    "enabled": true
  },
  
  "logs_dir": "C:\\SortNStore\\logs"
}
```

---

## Priority System

Destinations are resolved in this order:

1. **`category_destinations`** - Per-category override (highest priority)
2. **`base_destination`** - Custom base path
3. **Subfolder mode** - Watch folder + category (default)

### Example Priority

```json
{
  "base_destination": "D:\\Organized",
  "category_destinations": {
    "Images": "C:\\Pictures"
  }
}
```

**Routing:**
- Images → `C:\Pictures` (category override wins)
- Documents → `D:\Organized\Documents` (base_destination)
- Videos → `D:\Organized\Videos` (base_destination)

---

## Retry Queue for Cloud/Network

Network and cloud paths may be temporarily unavailable. The retry queue handles this automatically.

### Configuration

```json
{
  "retry_queue": {
    "enabled": true,
    "interval_seconds": 600,
    "max_retries": 10
  }
}
```

**Behavior:**
- If move fails (network down, cloud syncing, etc.)
- File is queued for retry
- Retries every 10 minutes
- Up to 10 retry attempts
- Logs success/failure

### When Retries Trigger

- Network drive temporarily unavailable
- Cloud sync in progress
- Permission issues (temporary)
- File locked by another process

---

## Use Cases

### 1. Photographer Workflow

```json
{
  "watch_folders": ["C:\\Users\\Photo\\Downloads"],
  "category_destinations": {
    "Images": "C:\\Users\\Photo\\OneDrive\\Photos\\RAW",
    "Videos": "D:\\Videos",
    "Other": "C:\\Users\\Photo\\Downloads\\Other"
  },
  "size_rules": [
    {
      "min_mb": 50,
      "destination": "D:\\LargeFiles"
    }
  ]
}
```

### 2. Business Document Management

```json
{
  "watch_folders": ["C:\\Users\\Manager\\Downloads"],
  "category_destinations": {
    "Documents": "\\\\CompanyNAS\\Documents",
    "Images": "\\\\CompanyNAS\\Marketing",
    "Archives": "\\\\CompanyNAS\\Backups"
  },
  "tag_routes": {
    "invoice": "\\\\CompanyNAS\\Finance\\Invoices",
    "contract": "\\\\CompanyNAS\\Legal\\Contracts"
  }
}
```

### 3. Family Shared Storage

```json
{
  "watch_folders": [
    "C:\\Users\\Dad\\Downloads",
    "C:\\Users\\Mom\\Downloads",
    "C:\\Users\\Kids\\Downloads"
  ],
  "base_destination": "C:\\Users\\Public\\OneDrive\\FamilyFiles",
  "routes": {
    "Photos": [".jpg", ".png", ".heic"],
    "Videos": [".mp4", ".mov"],
    "Documents": [".pdf", ".docx"]
  }
}
```

---

## Troubleshooting

### Cloud Sync Issues

**Problem:** Files not appearing in cloud after move

**Solutions:**
1. Ensure cloud client is running (OneDrive, Dropbox, etc.)
2. Check cloud sync status
3. Verify destination path is within synced folder
4. Enable retry queue for temporary sync delays

### Network Path Issues

**Problem:** Files not moving to UNC path

**Solutions:**
1. Test UNC path in File Explorer
2. Verify network credentials
3. Enable retry queue
4. Check network connectivity
5. Map network drive if credentials needed

### Permission Issues

**Problem:** Access denied errors

**Solutions:**
1. Run organizer with proper permissions
2. Check folder permissions
3. Verify cloud sync permissions
4. Check antivirus exclusions

### Performance Issues

**Problem:** Slow file operations

**Solutions:**
1. Use local paths when possible
2. Increase retry queue interval
3. Limit number of watch folders
4. Check network/cloud bandwidth

---

## Best Practices

1. **Test First** - Start with local paths, then add cloud/network
2. **Enable Retry Queue** - Essential for cloud/network destinations
3. **Monitor Logs** - Check `organizer.log` for issues
4. **Use Absolute Paths** - Always use full paths in config
5. **Backup Config** - Keep config backup before changes
6. **Check Sync Status** - Ensure cloud clients are running
7. **Network Reliability** - Use retry queue for unreliable networks

---

## Configuration Validation

Before deploying, validate your configuration:

```bash
# Check paths exist
C:\Users\You\OneDrive\Documents  ✓
\\NAS\Media\Videos               ✓

# Test write permissions
# Try creating a test file in each destination

# Verify cloud sync
# Check cloud client status icon
```

---

## Summary

**SortNStore Destination Modes:**

| Mode | Config | Use Case |
|------|--------|----------|
| **Subfolder** | `destination_mode: "subfolder"` | Simple local organization |
| **Custom Base** | `base_destination: "path"` | All categories to one location |
| **Per-Category** | `category_destinations: {...}` | Maximum flexibility |
| **Mixed** | All three combined | Enterprise setups |

**Supported Destinations:**
- ✅ Local folders (C:\, D:\, etc.)
- ✅ Network UNC paths (\\\\server\\share)
- ✅ OneDrive
- ✅ Google Drive
- ✅ Dropbox
- ✅ iCloud
- ✅ Any mounted cloud storage

**Key Features:**
- Automatic retry for temporary failures
- Cloud storage detection and handling
- Network path support with retry queue
- Per-category custom destinations
- 100% backward compatible

---

For more details, see:
- `ADVANCED_ROUTING_GUIDE.md` - All routing methods
- `organizer_config.json` - Your configuration
- `C:\SortNStore\logs\organizer.log` - Operation logs
