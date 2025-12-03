#!/usr/bin/env python3
"""
Diagnostic script to check if DownloadsOrganizeR environment is properly configured.
Run this on your Windows machine to verify the setup.
"""

import sys
import os

print("=" * 60)
print("DownloadsOrganizeR Environment Check")
print("=" * 60)
print(f"\nPython version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")

print("\n" + "=" * 60)
print("Checking required dependencies...")
print("=" * 60)

required_packages = [
    'flask',
    'requests',
    'bcrypt',
    'psutil',
    'watchdog',
    'ldap3',
    'flask_login',
    'gputil'
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package)
        print(f"✓ {package:20} installed")
    except ImportError:
        print(f"✗ {package:20} MISSING")
        missing_packages.append(package)

print("\n" + "=" * 60)
print("Checking project structure...")
print("=" * 60)

required_files = [
    'OrganizerDashboard.py',
    'Organizer.py',
    'organizer_config.json',
    'requirements.txt',
    'OrganizerDashboard/routes/api_recent_files.py'
]

for file in required_files:
    exists = os.path.exists(file)
    status = "✓" if exists else "✗"
    print(f"{status} {file:50} {'exists' if exists else 'MISSING'}")

print("\n" + "=" * 60)
print("Testing api_recent_files import...")
print("=" * 60)

try:
    from OrganizerDashboard.routes.api_recent_files import routes_api_recent_files
    print("✓ api_recent_files imported successfully")
    print(f"  Blueprint name: {routes_api_recent_files.name}")
    print(f"  Number of routes: {len(routes_api_recent_files.deferred_functions)}")
except Exception as e:
    print(f"✗ Failed to import api_recent_files:")
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)

if missing_packages:
    print(f"\n❌ {len(missing_packages)} package(s) missing: {', '.join(missing_packages)}")
    print("\nTo install missing packages, run:")
    print(f"  pip install {' '.join(missing_packages)}")
else:
    print("\n✓ All required packages are installed")

print("\nIf all checks pass, restart OrganizerDashboard.py and check for:")
print("  1. '✓ api_recent_files imported successfully' in console")
print("  2. '✓ routes_api_recent_files registered' in console")
print("  3. '/api/recent_files/virustotal' in registered routes list")
print("\n")
