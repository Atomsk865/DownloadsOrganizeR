# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec for SortNStore Dashboard
Builds a standalone executable with all dependencies bundled.

Generate with: pyinstaller SortNStore.spec
"""

import sys
import os
from pathlib import Path

block_cipher = None
# Get project root from environment or current directory
project_root = Path(os.getcwd())

# --- Data Files to Bundle ---
datas = [
    # HTML Templates
    (str(project_root / 'dash'), 'dash'),
    # Static Assets (CSS, JS, Images)
    (str(project_root / 'static'), 'static'),
    # Configuration Examples
    (str(project_root / 'examples'), 'examples'),
    # Documentation
    (str(project_root / 'DEPLOYMENT_CHECKLIST.md'), '.'),
    (str(project_root / 'BACKEND_OPTIMIZATIONS.md'), '.'),
    (str(project_root / 'JAVASCRIPT_MODULARIZATION.md'), '.'),
    (str(project_root / 'OPTIMIZATION_CAMPAIGN_COMPLETE.md'), '.'),
]

# --- Python Modules to Bundle ---
hiddenimports = [
    'flask',
    'flask_wtf',
    'flask_caching',
    'flask_compress',
    'flask_login',
    'psutil',
    'bcrypt',
    'watchdog',
    'watchdog.observers',
    'gputil',
    'ldap3',
    'pyasn1',
]

# Add Windows-specific imports if on Windows
if sys.platform == 'win32':
    hiddenimports.extend([
        'pywin32',
        'win32com',
    ])

# --- Binary Hooks ---
binaries = []

# --- Analysis ---
a = Analysis(
    [str(project_root / 'SortNStoreDashboard.py')],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[
        'matplotlib',
        'scipy',
        'numpy',
        'pandas',
        'tensorflow',
        'torch',
        'pytest',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# --- PYZ Creation ---
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# --- EXE Creation ---
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SortNStore',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here: icon='path/to/icon.ico'
)

# --- Collection for Single-File Distribution ---
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DownloadsOrganizeR',
)
