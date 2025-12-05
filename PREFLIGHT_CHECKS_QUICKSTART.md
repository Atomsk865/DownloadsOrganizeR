# Preflight Checks Feature - Quick Reference

## What Was Added

✅ **Comprehensive preflight validation system** that checks:
- Python version
- Required and optional dependencies
- Configuration files
- Template files
- Static assets
- File permissions
- Network ports
- Application package structure

## Files Modified/Created

### Modified:
- **SortNStoreDashboard.py** - Added `run_preflight_checks()` function and command-line arguments
- **readme.md** - Updated troubleshooting section and documentation index

### Created:
- **preflight_check.py** - Standalone preflight check script
- **docs/PREFLIGHT_CHECKS.md** - Comprehensive documentation

## Usage

### Start Dashboard with Preflight Checks (Default)
```bash
python SortNStoreDashboard.py
```

### Skip Preflight Checks
```bash
python SortNStoreDashboard.py --skip-preflight
```

### Run Only Preflight Checks (No Server)
```bash
python preflight_check.py
```

### Custom Port/Host
```bash
python SortNStoreDashboard.py --port 8080 --host 127.0.0.1
```

## Output Format

- ✅ **PASS** - Component working correctly
- ⚠️ **WARN** - Optional feature missing or degraded
- ❌ **FAIL** - Critical component missing (server won't start)

## Categories Checked

1. Python Version (3.8+)
2. Core Flask Dependencies (Flask, Flask-Login, Flask-WTF)
3. Authentication Modules (bcrypt, ldap3, pyasn1)
4. System Monitoring (psutil, gputil, requests)
5. File System Monitoring (watchdog)
6. Windows Modules (pywin32 - Windows only)
7. Configuration Files (JSON validation)
8. Template Files (dash/*.html)
9. Static Assets (static/css, static/js, static/img)
10. File System Permissions (write test)
11. Network Port Availability (default: 5000)
12. Application Package Structure (SortNStoreDashboard/)

## Benefits

- **Early Problem Detection**: Find missing dependencies before server starts
- **Clear Diagnostics**: Know exactly what's wrong and what's optional
- **Automation Friendly**: Exit codes for CI/CD integration
- **User Friendly**: Emoji indicators and helpful messages
- **Standalone Validation**: Check environment without starting server

## Exit Codes

- `0` - All checks passed or warnings only (server can start)
- `1` - Critical failure (server cannot start)

## Example Output

```
============================================================
🔍 Running Preflight Checks...
============================================================

📌 Python Version Check:
   ✅ PASS - Python 3.12.1

📌 Core Flask Dependencies:
   ✅ PASS - Flask
   ✅ PASS - Flask-Login
   ✅ PASS - Flask-WTF

... (more checks)

============================================================
📊 Preflight Check Summary:
============================================================
   ✅ Passed:  27
   ⚠️  Warned:  1
   ❌ Failed:  0
============================================================

✅ All checks passed! Starting server...
```

## Troubleshooting

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Invalid Config Files
- Check JSON syntax at jsonlint.com
- Or delete file and let server recreate defaults

### Port Already in Use
```bash
python SortNStoreDashboard.py --port 8080
```

## Documentation

See **docs/PREFLIGHT_CHECKS.md** for complete documentation including:
- Detailed check descriptions
- Troubleshooting guide
- CI/CD integration examples
- Best practices

