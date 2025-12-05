#!/usr/bin/env python3
"""
Standalone Preflight Check Script for SortNStore Dashboard

Run this script to validate your environment without starting the server:
    python preflight_check.py

This checks:
- Python version compatibility
- Required and optional dependencies
- Configuration files
- Template files
- File system permissions
- Network port availability
"""

import os
import sys
import json

# Configuration
CONFIG_FILE = "sortnstore_config.json"
DASHBOARD_CONFIG_FILE = "dashboard_config.json"

def run_preflight_checks():
    """
    Run preflight checks to validate environment and dependencies.
    Returns True if all critical checks pass, False otherwise.
    """
    print("\n" + "="*60)
    print("🔍 Running Preflight Checks...")
    print("="*60 + "\n")
    
    checks_passed = 0
    checks_warned = 0
    checks_failed = 0
    critical_failure = False
    
    # Check 1: Python Version
    print("📌 Python Version Check:")
    try:
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            print(f"   ✅ PASS - Python {version.major}.{version.minor}.{version.micro}")
            checks_passed += 1
        else:
            print(f"   ⚠️  WARN - Python {version.major}.{version.minor}.{version.micro} (3.8+ recommended)")
            checks_warned += 1
    except Exception as e:
        print(f"   ❌ FAIL - Could not determine Python version: {e}")
        checks_failed += 1
    
    # Check 2: Core Flask Dependencies
    print("\n📌 Core Flask Dependencies:")
    core_modules = {
        'flask': 'Flask',
        'flask_login': 'Flask-Login',
        'flask_wtf': 'Flask-WTF',
        'flask_caching': 'Flask-Caching (optional)',
        'flask_compress': 'Flask-Compress (optional)'
    }
    
    for module, name in core_modules.items():
        try:
            __import__(module)
            print(f"   ✅ PASS - {name}")
            checks_passed += 1
        except ImportError:
            if 'optional' in name.lower():
                print(f"   ⚠️  WARN - {name} not found (performance may be degraded)")
                checks_warned += 1
            else:
                print(f"   ❌ FAIL - {name} not found")
                checks_failed += 1
                critical_failure = True
    
    # Check 3: Authentication Modules
    print("\n📌 Authentication Modules:")
    auth_modules = {
        'bcrypt': ('Password Hashing', False),
        'ldap3': ('LDAP Authentication', True),
        'pyasn1': ('LDAP Support', True)
    }
    
    for module, (name, optional) in auth_modules.items():
        try:
            __import__(module)
            print(f"   ✅ PASS - {name}")
            checks_passed += 1
        except ImportError:
            if optional:
                print(f"   ⚠️  WARN - {name} not available (LDAP auth disabled)")
                checks_warned += 1
            else:
                print(f"   ❌ FAIL - {name} not found")
                checks_failed += 1
                critical_failure = True
    
    # Check 4: System Monitoring Dependencies
    print("\n📌 System Monitoring Dependencies:")
    monitoring_modules = {
        'psutil': ('Process & System Info', False),
        'gputil': ('GPU Monitoring', True),
        'requests': ('HTTP Requests', False)
    }
    
    for module, (name, optional) in monitoring_modules.items():
        try:
            __import__(module)
            print(f"   ✅ PASS - {name}")
            checks_passed += 1
        except ImportError:
            if optional:
                print(f"   ⚠️  WARN - {name} not available (feature disabled)")
                checks_warned += 1
            else:
                print(f"   ❌ FAIL - {name} not found")
                checks_failed += 1
                critical_failure = True
    
    # Check 5: File System Monitoring
    print("\n📌 File System Monitoring:")
    try:
        import watchdog
        print(f"   ✅ PASS - Watchdog")
        checks_passed += 1
    except ImportError:
        print(f"   ⚠️  WARN - Watchdog not available (file watching may not work)")
        checks_warned += 1
    
    # Check 6: Windows-specific modules (if on Windows)
    if sys.platform == 'win32':
        print("\n📌 Windows-specific Modules:")
        try:
            import win32serviceutil
            print(f"   ✅ PASS - pywin32 (Windows service support)")
            checks_passed += 1
        except ImportError:
            print(f"   ⚠️  WARN - pywin32 not available (Windows service features disabled)")
            checks_warned += 1
    
    # Check 7: Configuration Files
    print("\n📌 Configuration Files:")
    config_files = [
        (CONFIG_FILE, 'Main Config', False),
        (DASHBOARD_CONFIG_FILE, 'Dashboard Config', True),
        ('dashboard_branding.json', 'Branding Config', True)
    ]
    
    for filename, description, optional in config_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    json.load(f)
                print(f"   ✅ PASS - {description} ({filename})")
                checks_passed += 1
            except json.JSONDecodeError:
                print(f"   ❌ FAIL - {description} is invalid JSON ({filename})")
                checks_failed += 1
        else:
            if optional:
                print(f"   ⚠️  WARN - {description} not found (using defaults)")
                checks_warned += 1
            else:
                print(f"   ⚠️  WARN - {description} not found (will be created)")
                checks_warned += 1
    
    # Check 8: Template Files
    print("\n📌 Template Files:")
    template_dir = 'dash'
    required_templates = ['dashboard.html', 'login.html']
    
    if os.path.isdir(template_dir):
        for template in required_templates:
            template_path = os.path.join(template_dir, template)
            if os.path.exists(template_path):
                print(f"   ✅ PASS - {template}")
                checks_passed += 1
            else:
                print(f"   ❌ FAIL - {template} not found in {template_dir}/")
                checks_failed += 1
                critical_failure = True
    else:
        print(f"   ❌ FAIL - Template directory '{template_dir}/' not found")
        checks_failed += 1
        critical_failure = True
    
    # Check 9: Static Assets
    print("\n📌 Static Assets:")
    static_dir = 'static'
    if os.path.isdir(static_dir):
        subdirs = ['css', 'js', 'img']
        for subdir in subdirs:
            path = os.path.join(static_dir, subdir)
            if os.path.isdir(path):
                print(f"   ✅ PASS - {subdir}/ directory exists")
                checks_passed += 1
            else:
                print(f"   ⚠️  WARN - {subdir}/ directory not found")
                checks_warned += 1
    else:
        print(f"   ⚠️  WARN - Static directory not found (UI may not load correctly)")
        checks_warned += 1
    
    # Check 10: Write Permissions
    print("\n📌 File System Permissions:")
    test_files = ['test_write.tmp']
    for test_file in test_files:
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"   ✅ PASS - Write permissions in current directory")
            checks_passed += 1
            break
        except (OSError, PermissionError) as e:
            print(f"   ❌ FAIL - Cannot write to current directory: {e}")
            checks_failed += 1
            critical_failure = True
    
    # Check 11: Port Availability
    print("\n📌 Network Port Check:")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        
        if result != 0:
            print(f"   ✅ PASS - Port 5000 is available")
            checks_passed += 1
        else:
            print(f"   ⚠️  WARN - Port 5000 appears to be in use")
            checks_warned += 1
    except Exception as e:
        print(f"   ⚠️  WARN - Could not check port availability: {e}")
        checks_warned += 1
    
    # Check 12: SortNStoreDashboard Package
    print("\n📌 Application Package:")
    package_dir = 'SortNStoreDashboard'
    if os.path.isdir(package_dir):
        required_modules = ['__init__.py', 'config_runtime.py']
        required_dirs = ['routes', 'helpers', 'auth']
        
        for module in required_modules:
            module_path = os.path.join(package_dir, module)
            if os.path.exists(module_path):
                print(f"   ✅ PASS - {module}")
                checks_passed += 1
            else:
                print(f"   ❌ FAIL - {module} not found")
                checks_failed += 1
                critical_failure = True
        
        for subdir in required_dirs:
            subdir_path = os.path.join(package_dir, subdir)
            if os.path.isdir(subdir_path):
                print(f"   ✅ PASS - {subdir}/ directory exists")
                checks_passed += 1
            else:
                print(f"   ❌ FAIL - {subdir}/ directory not found")
                checks_failed += 1
                critical_failure = True
    else:
        print(f"   ❌ FAIL - Package directory '{package_dir}/' not found")
        checks_failed += 1
        critical_failure = True
    
    # Summary
    print("\n" + "="*60)
    print("📊 Preflight Check Summary:")
    print("="*60)
    print(f"   ✅ Passed:  {checks_passed}")
    print(f"   ⚠️  Warned:  {checks_warned}")
    print(f"   ❌ Failed:  {checks_failed}")
    print("="*60 + "\n")
    
    if critical_failure:
        print("❌ CRITICAL: Cannot start server due to failed checks")
        print("   Please install missing dependencies: pip install -r requirements.txt\n")
        return False
    elif checks_warned > 0:
        print("⚠️  WARNING: Some optional features may not be available")
        print("   Server can start but may have degraded functionality\n")
        return True
    else:
        print("✅ All checks passed! Ready to start server.\n")
        return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run preflight checks for SortNStore Dashboard')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show verbose output')
    args = parser.parse_args()
    
    result = run_preflight_checks()
    sys.exit(0 if result else 1)
