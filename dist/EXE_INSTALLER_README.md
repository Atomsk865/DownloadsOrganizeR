# Windows EXE Installer

## Quick Setup

**Option 1: Use Pre-built EXE (Recommended)**

1. Download `DownloadsOrganizeR-Setup.exe` from releases
2. Double-click to run (requires Administrator)
3. Follow the GUI wizard
4. Open http://localhost:5000 to complete setup

**Requirements:**
- Windows 10/11 or Windows Server 2016+
- Python 3.12+ installed and in PATH
- Administrator privileges

## Building Your Own EXE

If you want to build the installer yourself:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the builder:
   ```bash
   python installer_builder.py
   ```

3. Find the EXE in `dist/exe/DownloadsOrganizeR-Setup.exe`

## Installer Features

The EXE installer provides:
- **Graphical Interface**: User-friendly tkinter GUI
- **Embedded Package**: Contains complete v1.0-beta release
- **Automated Setup**: Creates venv, installs deps, initializes configs
- **Service Option**: Optional Windows service installation via NSSM
- **Dashboard Launch**: Auto-start dashboard after installation

## What Gets Installed

Location: `C:\Scripts` (configurable)

Contents:
- Python virtual environment (`venv/`)
- Application files (Organizer.py, OrganizerDashboard.py, etc.)
- Configuration files
- Templates and static assets
- All Python dependencies

## Troubleshooting

**"Python not found":**
- Install Python 3.12+ from https://python.org
- Check "Add Python to PATH" during installation
- Restart installer

**"Permission denied":**
- Right-click installer → "Run as Administrator"

**"NSSM service failed":**
- Download NSSM from https://nssm.cc
- Extract and add to PATH
- Or skip service installation

**Antivirus Warning:**
- PyInstaller executables may trigger false positives
- Add exception or use signed builds for production

## For Developers

See `installer_build_instructions.md` for detailed build process and customization options.
