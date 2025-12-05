# Preflight Checks Guide

## Overview

The SortNStore Dashboard now includes comprehensive preflight checks that validate your environment before starting the server. These checks help identify missing dependencies, configuration issues, and potential problems before they impact server operation.

## What Gets Checked

### 1. **Python Version** ✅
- Verifies Python 3.8 or higher is installed
- Shows current version information

### 2. **Core Flask Dependencies** ✅
- Flask (required)
- Flask-Login (required)
- Flask-WTF (required)
- Flask-Caching (optional - performance)
- Flask-Compress (optional - performance)

### 3. **Authentication Modules** ✅
- bcrypt (required - password hashing)
- ldap3 (optional - LDAP authentication)
- pyasn1 (optional - LDAP support)

### 4. **System Monitoring Dependencies** ✅
- psutil (required - process and system info)
- gputil (optional - GPU monitoring)
- requests (required - HTTP requests for VirusTotal, etc.)

### 5. **File System Monitoring** ✅
- watchdog (optional - file watching features)

### 6. **Windows-specific Modules** ✅ (Windows only)
- pywin32 (optional - Windows service support)

### 7. **Configuration Files** ✅
- `sortnstore_config.json` (main config)
- `dashboard_config.json` (dashboard settings)
- `dashboard_branding.json` (branding customization)
- Validates JSON syntax

### 8. **Template Files** ✅
- `dash/dashboard.html` (required)
- `dash/login.html` (required)

### 9. **Static Assets** ✅
- `static/css/` directory
- `static/js/` directory
- `static/img/` directory

### 10. **File System Permissions** ✅
- Tests write permissions in current directory

### 11. **Network Port Check** ✅
- Verifies port 5000 (or custom port) is available

### 12. **Application Package** ✅
- `SortNStoreDashboard/` directory structure
- Core module files (`__init__.py`, `config_runtime.py`)
- Required subdirectories (`routes/`, `helpers/`, `auth/`)

## Usage

### Running with the Dashboard

By default, preflight checks run automatically when you start the dashboard:

```bash
python SortNStoreDashboard.py
```

**Skip preflight checks** (not recommended):
```bash
python SortNStoreDashboard.py --skip-preflight
```

**Custom port/host**:
```bash
python SortNStoreDashboard.py --port 8080 --host 127.0.0.1
```

### Standalone Preflight Check

Run checks without starting the server:

```bash
python preflight_check.py
```

This is useful for:
- Validating environment after fresh install
- Troubleshooting issues before deployment
- CI/CD pipeline validation
- Quick health checks

## Understanding Results

### ✅ PASS
- Component is working correctly
- No action needed

### ⚠️ WARN
- Component is missing or degraded
- Server can start but some features may not work
- **Optional features** - can be ignored if not needed
- **Configuration issues** - server will create defaults

### ❌ FAIL
- Critical component is missing
- **Server will not start** if any checks fail
- Requires immediate attention

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
   ✅ PASS - Flask-Caching (optional)
   ✅ PASS - Flask-Compress (optional)

📌 Authentication Modules:
   ✅ PASS - Password Hashing
   ✅ PASS - LDAP Authentication
   ⚠️  WARN - LDAP Support not available (LDAP auth disabled)

... (more checks)

============================================================
📊 Preflight Check Summary:
============================================================
   ✅ Passed:  25
   ⚠️  Warned:  2
   ❌ Failed:  0
============================================================

⚠️  WARNING: Some optional features may not be available
   Server can start but may have degraded functionality
```

## Troubleshooting Failed Checks

### Missing Python Dependencies

If you see multiple `❌ FAIL` messages for Python modules:

```bash
pip install -r requirements.txt
```

### Invalid Configuration Files

If a config file shows `❌ FAIL - invalid JSON`:

1. Open the file in a text editor
2. Validate JSON syntax at [jsonlint.com](https://jsonlint.com)
3. Fix syntax errors or delete and let server recreate defaults

### Missing Template Files

If template files are missing:

```bash
# Verify you're in the correct directory
ls -la dash/

# If dash/ directory is missing, you may need to re-clone the repository
```

### Permission Issues

If write permission checks fail:

```bash
# Check current directory permissions
ls -la

# On Linux/Mac:
chmod u+w .

# On Windows:
# Right-click folder → Properties → Security → Edit permissions
```

### Port Already in Use

If port 5000 is already in use:

```bash
# Use a different port
python SortNStoreDashboard.py --port 8080

# Or find and stop the process using port 5000
# Linux/Mac:
lsof -ti:5000 | xargs kill -9

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## Exit Codes

The scripts use standard exit codes:

- `0` - All critical checks passed (or warnings only)
- `1` - One or more critical checks failed

This makes them suitable for use in scripts and automation:

```bash
if python preflight_check.py; then
    echo "Environment validated, starting server..."
    python SortNStoreDashboard.py
else
    echo "Preflight checks failed, cannot start server"
    exit 1
fi
```

## Command-Line Options

### SortNStoreDashboard.py

```
usage: SortNStoreDashboard.py [-h] [--skip-preflight] [--port PORT] [--host HOST]

SortNStore Dashboard Server

options:
  -h, --help        show this help message and exit
  --skip-preflight  Skip preflight checks and start immediately
  --port PORT       Port to run the server on (default: 5000)
  --host HOST       Host to bind to (default: 0.0.0.0)
```

### preflight_check.py

```
usage: preflight_check.py [-h] [--verbose]

Run preflight checks for SortNStore Dashboard

options:
  -h, --help     show this help message and exit
  --verbose, -v  Show verbose output (currently not implemented)
```

## Best Practices

1. **Always run preflight checks** after:
   - Fresh installation
   - Updating dependencies
   - Changing configuration
   - Moving to a new environment

2. **Don't skip preflight checks** in production environments

3. **Monitor warnings** - they indicate degraded functionality that may need attention

4. **Use standalone check** (`preflight_check.py`) for validation without starting the server

5. **Check exit codes** in automated scripts to ensure environment is valid

## Integration with CI/CD

Example GitHub Actions workflow:

```yaml
- name: Validate Environment
  run: python preflight_check.py

- name: Start Dashboard
  run: |
    python SortNStoreDashboard.py --port 8080 &
    sleep 5
    curl http://localhost:8080/metrics
```

Example PowerShell script:

```powershell
# Validate environment
python preflight_check.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Preflight checks failed"
    exit 1
}

# Start server
python SortNStoreDashboard.py --port 5000
```

