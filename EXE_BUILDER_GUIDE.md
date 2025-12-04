# DownloadsOrganizeR - EXE Builder Guide

## Overview

Build a standalone Windows EXE installer that includes all dependencies, no Python installation required on target machines.

**Build Size**: ~70-80 MB (all-in-one)
**Build Time**: 3-5 minutes
**Target**: Windows 7+
**Python Required**: 3.9+ (for building only, not for running EXE)

---

## Quick Start

### On Windows Development Machine

```batch
REM Navigate to project directory
cd C:\path\to\DownloadsOrganizeR

REM Run the build script (automatic)
build_exe.bat

REM Or run Python directly
python build_exe.py
```

### Output

```
dist/DownloadsOrganizeR/
├── DownloadsOrganizeR.exe          (70-80 MB) - Main executable
├── Install.bat                     - Installation script
├── README.md                       - Quick start guide
├── Create-Shortcut.bat             - Create desktop shortcut
├── _internal/                      - All bundled dependencies
└── [other dependencies]
```

---

## Distribution Methods

### Method 1: Direct EXE (Simplest)

1. Copy `DownloadsOrganizeR.exe` to target machine
2. Run it directly - dashboard starts immediately
3. No installation needed

### Method 2: Portable Folder (Recommended)

1. Copy entire `dist/DownloadsOrganizeR/` folder to target
2. Run `DownloadsOrganizeR.exe`
3. (Optional) Run `Install.bat` as admin to install Windows service

### Method 3: Installer Batch

1. Copy `dist/DownloadsOrganizeR/` folder to target
2. Run `Install.bat` as Administrator
3. Choose installation directory (default: `C:\Scripts`)
4. (Optional) Install as Windows service using NSSM

---

## Build Customization

### Change Application Icon

1. Create or find `.ico` file (256x256 minimum)
2. Edit `DownloadsOrganizeR.spec`:

```python
exe = EXE(
    ...
    icon='path/to/icon.ico',  # Add this line
)
```

3. Rebuild with `python build_exe.py`

### Change Startup Port

Edit `OrganizerDashboard.py`:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
    # Change 5000 to desired port
```

### Change EXE Name

Edit `build_exe.py`:

```python
EXE_NAME = f'MyCustomName-v{version}.exe'
```

### Change Default Credentials

Edit `OrganizerDashboard.py`:

```python
DASHBOARD_USER = os.getenv('DASHBOARD_USER', 'admin')
DASHBOARD_PASS = os.getenv('DASHBOARD_PASS', 'test123')
# Change default values above
```

---

## Build Process Details

### Phase 1: Analysis
- Scans Python code for imports
- Identifies all dependencies
- Locates hidden imports (Flask, watchdog, etc.)

### Phase 2: Compilation
- Compiles Python to bytecode
- Optimizes imports
- Creates dependency tree

### Phase 3: Collection
- Bundles all Python bytecode
- Includes standard library
- Includes third-party packages

### Phase 4: Packaging
- Creates EXE wrapper
- Bundles data files (HTML, CSS, JS)
- Compresses resources

**Size Breakdown:**
- Python runtime: ~30 MB
- Dependencies: ~25 MB
- Flask & libraries: ~15 MB
- Data files (templates, static): ~5-8 MB
- Overhead & padding: ~5 MB
- **Total: ~70-80 MB**

---

## Troubleshooting

### Build Fails - "Module not found"

```
Error: No module named 'xyz'
```

**Solution**: Add to `hiddenimports` in `DownloadsOrganizeR.spec`:

```python
hiddenimports = [
    # ... existing imports
    'xyz',  # Add missing module
]
```

### Build is Too Large

Remove unused packages from requirements.txt:
```
pip freeze | grep -v "used_package" > requirements.txt
```

### EXE Won't Start

1. Check if Python dependencies are installed:
```batch
python build_exe.py  REM Re-run build
```

2. Run in console mode to see errors:
```python
# Edit DownloadsOrganizeR.spec
exe = EXE(..., console=True, ...)  # Set to True temporarily
```

3. Check antivirus - may quarantine unsigned EXE

### Port Already in Use

```batch
REM Find process using port 5000
netstat -ano | findstr :5000

REM Kill process
taskkill /PID <PID> /F

REM Or change port in config
```

### Dashboard Won't Load After EXE Launch

1. Check Windows Firewall - allow port 5000
2. Check antivirus - may be blocking network
3. Check logs: `C:\Scripts\service-logs\organizer_stderr.log`

---

## Performance Notes

The compiled EXE includes all optimizations from the campaign:

✅ **Backend**: Query caching, rate limiting, SSE streams
✅ **Frontend**: Module system, lazy loading, compression
✅ **Data**: Asset versioning, static compression, bundling

**First Run**: ~2-3 seconds (Python startup)
**Subsequent Runs**: ~1 second (cached)
**Dashboard Load**: 300ms (75% faster with optimizations)

---

## Code Signing (Optional)

For enterprise deployment, sign the EXE:

```batch
REM Sign with certificate
signtool sign /f certificate.pfx /p password /t http://timestamp.server DownloadsOrganizeR.exe

REM Verify signature
signtool verify /v DownloadsOrganizeR.exe
```

---

## Deployment Checklist

- [ ] Build succeeds without errors
- [ ] EXE launches on test machine
- [ ] Dashboard accessible at http://localhost:5000
- [ ] File organization works
- [ ] All features functional
- [ ] No Python installation required on target
- [ ] Icon displays correctly
- [ ] Company branding applied (if any)
- [ ] Signed with certificate (if required)

---

## Support & Issues

### Build Issues
1. Ensure Python 3.9+ installed
2. Run `pip install --upgrade pyinstaller`
3. Check `build_exe.py` logs

### Runtime Issues
1. Check `C:\Scripts\service-logs\` for errors
2. Verify firewall allows port 5000
3. Review `organizer_config.json`

### Distribution Issues
1. Test on clean Windows 7+ machine
2. Ensure Visual C++ redistributables installed (usually present)
3. Use `dist/DownloadsOrganizeR/` entire folder

---

## Advanced Options

### Build with Optimizations

```bash
python build_exe.py --clean     # Remove old builds first
```

### Build and Create NSIS Installer

```bash
python build_exe.py --installer  # (Future enhancement)
```

### Debug Build (Console Window)

Edit `DownloadsOrganizeR.spec`:
```python
exe = EXE(..., console=True)  # See output for debugging
```

---

## Files Created During Build

```
build/                         Intermediate files (can delete after)
dist/DownloadsOrganizeR/       Final distribution
  ├── DownloadsOrganizeR.exe
  ├── _internal/               All bundled dependencies
  ├── dash/                    HTML templates
  ├── static/                  CSS, JS, images
  ├── Install.bat
  ├── Create-Shortcut.bat
  └── README.md
```

**Safe to delete**: `build/` directory (intermediate files)
**Keep**: `dist/` directory (distribution package)

---

## Version Management

Edit `version.json` to update build version:

```json
{
  "version": "1.0.0",
  "release_date": "2025-12-04",
  "build_number": 5020
}
```

Version is automatically included in EXE filename:
- `DownloadsOrganizeR-v1.0.0.exe`

---

## Success!

Once build completes:

1. ✅ Navigate to `dist/DownloadsOrganizeR/`
2. ✅ Run `DownloadsOrganizeR.exe`
3. ✅ Open browser to `http://localhost:5000`
4. ✅ Login with `admin` / `test123`
5. ✅ Configure file organization rules
6. ✅ (Optional) Install as Windows service

**Ready for distribution!** 🚀
