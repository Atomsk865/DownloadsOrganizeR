# EXE Installer Build Instructions

This directory contains tools to build a Windows executable installer for DownloadsOrganizeR.

## Prerequisites

Install PyInstaller:
```bash
pip install pyinstaller
```

## Building the EXE

Run the builder script:
```bash
python installer_builder.py
```

This will:
1. Create an installer GUI script with tkinter
2. Bundle the v1.0-beta release package
3. Use PyInstaller to create a single-file executable
4. Output to `dist/exe/DownloadsOrganizeR-Setup.exe`

## What the EXE Does

The executable provides a graphical installer that:
- Shows a user-friendly GUI with installation options
- Extracts the embedded release package
- Creates Python virtual environment
- Installs dependencies
- Initializes configurations
- Optionally installs Windows service via NSSM
- Starts the dashboard

## Testing

After building:
1. Copy `dist/exe/DownloadsOrganizeR-Setup.exe` to a test Windows machine
2. Double-click to run (may need "Run as Administrator")
3. Follow the GUI prompts
4. Verify installation in chosen directory
5. Access dashboard at http://localhost:5000

## Distribution

The final EXE can be distributed:
- Via GitHub Releases
- Direct download
- Internal file shares

No Python required on target machine for running the installer (but Python 3.12+ must be installed on the system for the application to work).

## Customization

Edit `installer_builder.py` to:
- Change installer GUI appearance
- Modify default installation options
- Add custom pre/post-install steps
- Update version information

## Troubleshooting

**PyInstaller errors:**
- Ensure all dependencies are installed
- Try updating PyInstaller: `pip install --upgrade pyinstaller`

**Large EXE size:**
- Expected, includes full release package (~2-5 MB compressed)
- Consider using UPX compression with `--upx-dir` flag

**Antivirus false positives:**
- Common with PyInstaller executables
- Sign the EXE with a code signing certificate for production
