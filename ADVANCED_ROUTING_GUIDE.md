# SortNStore Advanced Routing Guide

The rebuilt Organizer.py now features sophisticated, multi-tier file routing with support for multiple watch folders and advanced routing criteria. This guide demonstrates how to configure and use all new capabilities.

---

## Table of Contents

1. [Multiple Watch Folders](#multiple-watch-folders)
2. [Routing Priority System](#routing-priority-system)
3. [Extension-Based Routing](#extension-based-routing)
4. [Tag-Based Routing](#tag-based-routing)
5. [Pattern-Based Routing (Regex)](#pattern-based-routing)
6. [Size-Based Routing](#size-based-routing)
7. [Date-Based Routing](#date-based-routing)
8. [Custom Per-Extension Routes](#custom-per-extension-routes)
9. [Complete Configuration Examples](#complete-configuration-examples)
10. [Troubleshooting](#troubleshooting)

---

## Multiple Watch Folders

### Basic Setup

Monitor multiple folders simultaneously by configuring `watch_folders` as an array:

```json
{
  "watch_folders": [
    "C:\\Users\\YourUsername\\Downloads",
    "C:\\Users\\YourUsername\\Desktop",
    "D:\\Incoming\\Shared"
  ]
}
```

Or use the legacy single folder (for backward compatibility):

```json
{
  "watch_folder": "C:\\Users\\YourUsername\\Downloads"
}
```

**Note:** If `watch_folders` is configured, it takes precedence over `watch_folder`.

---

## Routing Priority System

Files are routed using this priority order:

1. **Custom per-extension routes** (highest priority)
2. **Filename tag routes**
3. **Regex pattern routes**
4. **File size rules**
5. **Date range rules**
6. **Extension-based categorization** (default)

The first matching rule wins. Files that don't match any rule fall through to the next level until reaching the default extension-based categorization.

---

## Extension-Based Routing

The default routing mechanism. Maps file extensions to category folders.

### Default Categories

```
Images   → .jpg, .jpeg, .png, .gif, .bmp, .tiff, .svg, .webp, .heic, .ico
Music    → .mp3, .wav, .flac, .aac, .ogg, .wma, .m4a, .aiff, .ape
Videos   → .mp4, .mkv, .avi, .mov, .wmv, .flv, .webm, .m4v, .ts
Documents → .pdf, .doc, .docx, .txt, .rtf, .odt, .xls, .xlsx, .ppt, .pptx, .csv
Archives → .zip, .rar, .7z, .tar, .gz, .bz2, .xz, .iso
Executables → .exe, .msi, .bat, .cmd, .ps1, .app, .dmg
Shortcuts → .lnk, .url, .webloc
Code     → .py, .js, .html, .css, .json, .xml, .sh, .ts, .php, .java, .cpp, .c, .h, .cs, .rb, .go
Fonts    → .ttf, .otf, .woff, .woff2, .eot
Data     → .sql, .db, .sqlite, .json, .yaml, .yml, .xml
Logs     → .log
Other    → (all unrecognized extensions)
```

### Customize Categories

Override or add custom categories in `organizer_config.json`:

```json
{
  "routes": {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Videos": [".mp4", ".mkv", ".avi"],
    "Documents": [".pdf", ".doc", ".docx"],
    "eBooks": [".epub", ".mobi", ".azw"],
    "Code": [".py", ".js", ".go", ".rust"],
    "Other": []
  }
}
```

**Files are placed in:** `{watch_folder}/{category}/`

Example: A file `vacation.jpg` → `C:\Users\You\Downloads\Images\vacation.jpg`

---

## Tag-Based Routing

Route files based on keywords in their filenames. Highest match priority after custom routes.

### Configuration

```json
{
  "tag_routes": {
    "invoice": "C:\\Accounting\\Invoices",
    "receipt": "C:\\Accounting\\Receipts",
    "contract": "C:\\Legal\\Contracts",
    "passport": "C:\\Important\\ID"
  }
}
```

### How It Works

- Check if the filename **contains** the tag (case-insensitive)
- If multiple tags match, the first one in the config wins
- Returns file to specified destination immediately

### Examples

| File | Tag Match | Destination |
|------|-----------|-------------|
| `invoice_2024_001.pdf` | `invoice` | `C:\Accounting\Invoices` |
| `My_Passport_Scan.pdf` | `passport` | `C:\Important\ID` |
| `contract_employment.docx` | `contract` | `C:\Legal\Contracts` |
| `invoice_receipt_2024.pdf` | `invoice` | `C:\Accounting\Invoices` (first match) |

---

## Pattern-Based Routing

Use regular expressions for sophisticated filename matching. More powerful than tag routing.

### Configuration

```json
{
  "pattern_routes": {
    "^invoice_\\d{4}": "C:\\Accounting\\Invoices",
    "(tax|w2|1040).*\\.pdf$": "C:\\Taxes",
    "\\[DRAFT\\].*": "C:\\WorkInProgress",
    "Screenshot_\\d{8}": "C:\\Screenshots",
    "resume.*\\.pdf$": "C:\\Jobs\\Resumes"
  }
}
```

### Regex Patterns Explained

| Pattern | Matches | Example |
|---------|---------|---------|
| `^invoice_\d{4}` | invoice_2024, invoice_2025 | `invoice_2024_details.pdf` |
| `(tax\|w2\|1040).*\.pdf$` | Any .pdf starting with tax, w2, or 1040 | `tax_return_2023.pdf` |
| `\[DRAFT\].*` | Files containing [DRAFT] prefix | `[DRAFT] Project Plan.docx` |
| `Screenshot_\d{8}` | Screenshot_YYYYMMDD | `Screenshot_20240115.png` |
| `resume.*\.pdf$` | Any .pdf containing "resume" | `resume_john_doe.pdf` |

### Common Regex Patterns

```regex
# Match all PDFs
.*\.pdf$

# Match files starting with a year (2024, 2025, etc.)
^20\d{2}.*

# Match files with numbers in sequence
.*_\d{3,}.*

# Match any file with parentheses
.*\(.*\).*

# Match backups
.*backup.*|.*\.bak$

# Match files in date format YYYY-MM-DD
.*\d{4}-\d{2}-\d{2}.*
```

---

## Size-Based Routing

Route files based on their file size. Useful for separating large media from documents.

### Configuration

```json
{
  "size_rules": [
    {
      "min_mb": 0,
      "max_mb": 1,
      "destination": "C:\\Files\\Small"
    },
    {
      "min_mb": 1,
      "max_mb": 100,
      "destination": "C:\\Files\\Medium"
    },
    {
      "min_mb": 100,
      "max_mb": 1000,
      "destination": "C:\\Files\\Large"
    },
    {
      "min_mb": 1000,
      "destination": "C:\\Files\\Huge"
    }
  ]
}
```

### Size Ranges

| min_mb | max_mb | Category | Use Case |
|--------|--------|----------|----------|
| 0 | 1 | Small | Documents, text files, small images |
| 1 | 50 | Medium | Videos clips, office files |
| 50 | 500 | Large | HD videos, backups |
| 500 | ∞ | Huge | 4K/8K videos, disk images |

### Example Sizes

```
1 KB            → 0.001 MB
500 KB          → 0.5 MB
5 MB            → 5 MB
100 MB          → 100 MB
1 GB            → 1024 MB
5 GB            → 5120 MB
```

### Advanced: Specific Size Thresholds

```json
{
  "size_rules": [
    {
      "min_mb": 0,
      "max_mb": 10,
      "destination": "C:\\Archive\\SmallFiles"
    },
    {
      "min_mb": 10,
      "max_mb": 50,
      "destination": "C:\\Archive\\MediumFiles"
    },
    {
      "min_mb": 50,
      "destination": "C:\\Archive\\LargeFiles"
    }
  ]
}
```

---

## Date-Based Routing

Route files based on creation or modification date. Useful for organizing by recency or archival.

### Configuration

```json
{
  "date_rules": [
    {
      "days_newer_than": 7,
      "destination": "C:\\Files\\Recent"
    },
    {
      "days_older_than": 365,
      "destination": "C:\\Archive\\Old"
    },
    {
      "days_older_than": 30,
      "days_newer_than": 1,
      "destination": "C:\\Files\\LastMonth"
    }
  ]
}
```

### Date Rule Fields

| Field | Type | Description |
|-------|------|-------------|
| `days_newer_than` | int | File modified within last N days |
| `days_older_than` | int | File not modified for at least N days |
| `destination` | string | Path to move file to |

### Examples

**Recent Files (Last 7 Days)**
```json
{
  "days_newer_than": 7,
  "destination": "C:\\Recent Downloads"
}
```

**Archive Old Files (Over 1 Year Old)**
```json
{
  "days_older_than": 365,
  "destination": "C:\\Archive\\2023"
}
```

**Last Month's Files**
```json
{
  "days_older_than": 30,
  "days_newer_than": 1,
  "destination": "C:\\Files\\LastMonth"
}
```

**Very Old Files (2+ Years)**
```json
{
  "days_older_than": 730,
  "destination": "C:\\Archive\\Old"
}
```

---

## Custom Per-Extension Routes

Override default category routing for specific extensions with absolute paths.

### Configuration

```json
{
  "custom_routes": {
    "docx": "C:\\Work\\Documents",
    "pdf": "C:\\Documents\\PDFs",
    "xlsx": "C:\\Spreadsheets",
    "mp4": "D:\\Videos",
    "psd": "C:\\Design\\Photoshop"
  }
}
```

### Examples

| Extension | Config | File | Destination |
|-----------|--------|------|-------------|
| `.docx` | `"C:\\Work\\Documents"` | `report.docx` | `C:\Work\Documents\report.docx` |
| `.pdf` | `"C:\\Documents\\PDFs"` | `invoice.pdf` | `C:\Documents\PDFs\invoice.pdf` |
| `.psd` | `"C:\\Design\\Photoshop"` | `mockup.psd` | `C:\Design\Photoshop\mockup.psd` |

**Note:** Custom routes take precedence over all other routing methods except being a duplicate/ignored file.

---

## Complete Configuration Examples

### Example 1: Small Home Setup

```json
{
  "watch_folders": [
    "C:\\Users\\John\\Downloads",
    "C:\\Users\\John\\Desktop"
  ],
  "routes": {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Videos": [".mp4", ".mkv"],
    "Documents": [".pdf", ".doc", ".docx", ".txt"],
    "Music": [".mp3", ".wav"],
    "Archives": [".zip", ".rar"],
    "Other": []
  },
  "tag_routes": {
    "invoice": "C:\\Home\\Finance\\Invoices",
    "receipt": "C:\\Home\\Finance\\Receipts",
    "important": "C:\\Home\\Important"
  },
  "logs_dir": "C:\\SortNStore\\logs"
}
```

### Example 2: Professional Setup with Advanced Rules

```json
{
  "watch_folders": [
    "C:\\Users\\alice\\Downloads",
    "C:\\Users\\alice\\Desktop",
    "\\\\NAS\\Incoming"
  ],
  "routes": {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".tiff"],
    "Videos": [".mp4", ".mov", ".mkv"],
    "Documents": [".pdf", ".doc", ".docx", ".xlsx"],
    "Code": [".py", ".js", ".go", ".cpp"],
    "Data": [".sql", ".db", ".json"],
    "Other": []
  },
  "custom_routes": {
    "psd": "C:\\Design\\Photoshop",
    "ai": "C:\\Design\\Illustrator",
    "mp4": "D:\\Projects\\Media"
  },
  "tag_routes": {
    "invoice": "C:\\Accounting\\Invoices",
    "contract": "C:\\Legal\\Contracts",
    "proposal": "C:\\Sales\\Proposals",
    "report": "C:\\Reports"
  },
  "pattern_routes": {
    "^\\d{4}-[A-Z]{3}-\\d{3}": "C:\\Projects\\Numbered",
    "backup.*": "C:\\Backups",
    "\\[CONFIDENTIAL\\]": "C:\\Secure\\Confidential"
  },
  "size_rules": [
    {
      "min_mb": 500,
      "destination": "D:\\LargeFiles"
    }
  ],
  "date_rules": [
    {
      "days_older_than": 365,
      "destination": "C:\\Archive\\2023"
    }
  ],
  "duplicate_detection": {
    "enabled": true
  },
  "retry_queue": {
    "enabled": true,
    "interval_seconds": 600,
    "max_retries": 10
  },
  "logs_dir": "C:\\SortNStore\\logs"
}
```

### Example 3: Media Organization

```json
{
  "watch_folders": ["C:\\Users\\Media\\Downloads"],
  "routes": {
    "Screenshots": [".png", ".jpg"],
    "Videos": [".mp4", ".mkv", ".mov"],
    "Audio": [".mp3", ".wav", ".flac"],
    "Archives": [".zip", ".rar"],
    "Other": []
  },
  "size_rules": [
    {
      "min_mb": 0,
      "max_mb": 10,
      "destination": "C:\\Media\\Thumbnails"
    },
    {
      "min_mb": 10,
      "max_mb": 500,
      "destination": "C:\\Media\\Processed"
    },
    {
      "min_mb": 500,
      "destination": "D:\\Media\\Raw"
    }
  ],
  "date_rules": [
    {
      "days_newer_than": 7,
      "destination": "C:\\Media\\Recent"
    }
  ]
}
```

### Example 4: Archive System

```json
{
  "watch_folders": ["C:\\Users\\You\\Downloads"],
  "routes": {
    "Documents": [".pdf", ".docx", ".txt"],
    "Projects": [".zip", ".7z"],
    "Other": []
  },
  "date_rules": [
    {
      "days_newer_than": 0,
      "days_older_than": 0,
      "destination": "C:\\Archive\\Current"
    },
    {
      "days_older_than": 30,
      "days_newer_than": 1,
      "destination": "C:\\Archive\\30Days"
    },
    {
      "days_older_than": 365,
      "destination": "C:\\Archive\\1Year"
    }
  ],
  "duplicate_detection": {
    "enabled": true
  }
}
```

---

## Troubleshooting

### File Not Being Organized

**Check:**
1. Is the file in an ignored list?
   - `IGNORE_FILES`: dashboard_config.json, organizer_config.json
   - `IGNORE_EXTENSIONS`: .crdownload, .part, .tmp, .downloading, .incomplete

2. Is the file still being written?
   - Files in use (locked) may need retry

3. Are there permission issues?
   - Check `C:\SortNStore\logs\organizer.log` for error messages

4. Does the destination exist and have write permissions?

### File Organization Applied Wrong Route

Check the routing priority:
1. Does it match a custom per-extension route?
2. Does it contain a tag keyword?
3. Does it match a regex pattern?
4. Does it match a size rule?
5. Does it match a date rule?
6. Falls back to extension-based

**Solution:** Check `organizer.log` for the "routing_reason" to see which rule matched.

### Regex Pattern Not Matching

**Test regex patterns at:** https://regex101.com

Common issues:
- Forgetting `^` and `$` anchors
- Not escaping special characters properly
- Case sensitivity (use `(?i)` for case-insensitive)

### Network Paths Not Working

Enable retry queue for network destinations:
```json
{
  "retry_queue": {
    "enabled": true,
    "interval_seconds": 600
  }
}
```

This automatically retries failed moves every 10 minutes.

### Duplicate Detection Issues

Enable logging to debug:
```json
{
  "duplicate_detection": {
    "enabled": true
  }
}
```

Check `file_hashes.json` to see tracked hashes.

---

## Best Practices

1. **Start Simple** → Begin with basic extension routing, then add advanced rules
2. **Test Patterns** → Test regex patterns at regex101.com before using
3. **Use Specific Paths** → Be explicit about destination paths
4. **Monitor Logs** → Check `organizer.log` to verify routing decisions
5. **Backup Config** → Keep a copy of your `organizer_config.json`
6. **Organize Hierarchically** → Use nested folders for better organization
7. **Consider Case** → Filenames are case-insensitive in routing

---

## Performance Considerations

- **Size rules** scan all new files (minimal impact)
- **Date rules** check file timestamps (minimal impact)
- **Pattern matching** uses regex (CPU-bound for complex patterns)
- **Duplicate detection** hashes files (I/O-bound, optional)
- **Network paths** retry intelligently (background thread)

For performance optimization:
- Limit regex complexity
- Only enable duplicate detection if needed
- Use specific watch folders rather than broad paths

---

For more help, check:
- `/workspaces/DownloadsOrganizeR/organizer_config.json` - Your configuration
- `C:\SortNStore\logs\organizer.log` - Service logs
- GitHub Issues - Community support
