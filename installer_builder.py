#!/usr/bin/env python3
"""
DownloadsOrganizeR EXE Installer Builder

Creates a Windows executable installer using PyInstaller.
Run this script to build the .exe installer.
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DIST_DIR = SCRIPT_DIR / 'dist'
BUILD_DIR = SCRIPT_DIR / 'build'
INSTALLER_DIR = SCRIPT_DIR / 'installer_build'

INSTALLER_SCRIPT = """
import os
import sys
import subprocess
import tempfile
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import threading

# Embedded release package data will be added by PyInstaller
RELEASE_ZIP = 'DownloadsOrganizeR-v1.0-beta.zip'

class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('DownloadsOrganizeR Installer - v1.0-beta')
        self.root.geometry('600x450')
        self.root.resizable(False, False)
        
        self.target_dir = tk.StringVar(value='C:\\\\Scripts')
        self.install_service = tk.BooleanVar(value=False)
        self.start_dashboard = tk.BooleanVar(value=True)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', height=80)
        header.pack(fill='x')
        title = tk.Label(header, text='DownloadsOrganizeR', 
                        font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50')
        title.pack(pady=10)
        subtitle = tk.Label(header, text='Automated File Organization for Windows',
                           font=('Arial', 10), fg='#ecf0f1', bg='#2c3e50')
        subtitle.pack()
        
        # Content
        content = tk.Frame(self.root, padx=20, pady=20)
        content.pack(fill='both', expand=True)
        
        # Installation directory
        tk.Label(content, text='Installation Directory:', 
                font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5))
        dir_frame = tk.Frame(content)
        dir_frame.grid(row=1, column=0, sticky='ew', pady=(0,15))
        tk.Entry(dir_frame, textvariable=self.target_dir, 
                font=('Arial', 10), width=50).pack(side='left', fill='x', expand=True)
        
        # Options
        tk.Label(content, text='Installation Options:', 
                font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(0,5))
        tk.Checkbutton(content, text='Install Windows Service (requires NSSM)', 
                      variable=self.install_service, 
                      font=('Arial', 9)).grid(row=3, column=0, sticky='w')
        tk.Checkbutton(content, text='Start Dashboard after installation', 
                      variable=self.start_dashboard,
                      font=('Arial', 9)).grid(row=4, column=0, sticky='w', pady=(0,15))
        
        # Requirements
        tk.Label(content, text='Requirements:', 
                font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky='w', pady=(0,5))
        req_text = tk.Text(content, height=6, width=70, font=('Arial', 9), wrap='word')
        req_text.grid(row=6, column=0, sticky='ew', pady=(0,15))
        req_text.insert('1.0', 
            '• Python 3.12+ installed and added to PATH\\n'
            '• Administrator privileges\\n'
            '• NSSM (optional, for Windows service)\\n'
            '• Port 5000 available for dashboard\\n'
            '• Internet connection for package installation')
        req_text.config(state='disabled')
        
        # Progress
        self.progress_label = tk.Label(content, text='', font=('Arial', 9), fg='blue')
        self.progress_label.grid(row=7, column=0, sticky='w', pady=(0,5))
        self.progress = ttk.Progressbar(content, mode='indeterminate')
        self.progress.grid(row=8, column=0, sticky='ew', pady=(0,15))
        
        # Buttons
        btn_frame = tk.Frame(content)
        btn_frame.grid(row=9, column=0, sticky='e')
        self.install_btn = tk.Button(btn_frame, text='Install', 
                                     command=self.start_install,
                                     font=('Arial', 10, 'bold'),
                                     bg='#27ae60', fg='white',
                                     padx=20, pady=5)
        self.install_btn.pack(side='left', padx=5)
        tk.Button(btn_frame, text='Exit', command=self.root.quit,
                 font=('Arial', 10), padx=20, pady=5).pack(side='left')
        
        content.columnconfigure(0, weight=1)
        
    def start_install(self):
        self.install_btn.config(state='disabled')
        self.progress.start()
        thread = threading.Thread(target=self.run_install, daemon=True)
        thread.start()
        
    def run_install(self):
        try:
            target = self.target_dir.get()
            
            # Extract embedded package
            self.update_progress('Extracting files...')
            temp_dir = Path(tempfile.mkdtemp())
            zip_path = Path(sys._MEIPASS) / RELEASE_ZIP
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Copy files to target
            self.update_progress(f'Installing to {target}...')
            os.makedirs(target, exist_ok=True)
            
            for item in temp_dir.iterdir():
                dest = Path(target) / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            
            # Create venv
            self.update_progress('Creating Python virtual environment...')
            subprocess.run([sys.executable, '-m', 'venv', 
                          str(Path(target) / 'venv')], check=True,
                          capture_output=True)
            
            # Install requirements
            self.update_progress('Installing Python packages...')
            venv_python = str(Path(target) / 'venv' / 'Scripts' / 'python.exe')
            subprocess.run([venv_python, '-m', 'pip', 'install', '--upgrade', 'pip'],
                         check=True, capture_output=True)
            subprocess.run([venv_python, '-m', 'pip', 'install', '-r',
                          str(Path(target) / 'requirements.txt')],
                         check=True, capture_output=True)
            
            # Initialize configs
            self.update_progress('Initializing configuration...')
            for cfg in ['organizer_config.json', 'dashboard_config.json']:
                cfg_path = Path(target) / cfg
                if not cfg_path.exists():
                    if cfg == 'organizer_config.json':
                        cfg_path.write_text('{}')
                    else:
                        cfg_path.write_text('{"setup_completed": false, "users": [], '
                                          '"roles": {"admin": {"manage_config": true}, "viewer": {}}}')
            
            # Install service if requested
            if self.install_service.get():
                self.update_progress('Installing Windows service...')
                try:
                    subprocess.run(['nssm', 'install', 'DownloadsOrganizer',
                                  venv_python, str(Path(target) / 'Organizer.py')],
                                 check=True, capture_output=True)
                    logs_dir = Path(target) / 'service-logs'
                    logs_dir.mkdir(exist_ok=True)
                    subprocess.run(['nssm', 'set', 'DownloadsOrganizer', 'AppDirectory', target],
                                 check=True, capture_output=True)
                    subprocess.run(['nssm', 'set', 'DownloadsOrganizer', 'AppStdout',
                                  str(logs_dir / 'organizer_stdout.log')],
                                 check=True, capture_output=True)
                    subprocess.run(['nssm', 'set', 'DownloadsOrganizer', 'AppStderr',
                                  str(logs_dir / 'organizer_stderr.log')],
                                 check=True, capture_output=True)
                    subprocess.run(['nssm', 'start', 'DownloadsOrganizer'],
                                 check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    messagebox.showwarning('Service Installation',
                                         'NSSM service installation failed. You can install manually later.')
            
            # Start dashboard if requested
            if self.start_dashboard.get():
                self.update_progress('Starting dashboard...')
                subprocess.Popen([venv_python, str(Path(target) / 'OrganizerDashboard.py')],
                               cwd=target, creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            self.update_progress('Installation complete!')
            self.progress.stop()
            messagebox.showinfo('Success', 
                              f'DownloadsOrganizeR installed successfully!\\n\\n'
                              f'Location: {target}\\n'
                              f'Dashboard: http://localhost:5000\\n\\n'
                              f'Open the dashboard to complete first-time setup.')
            self.root.quit()
            
        except Exception as e:
            self.progress.stop()
            messagebox.showerror('Installation Error', f'Installation failed:\\n{str(e)}')
            self.install_btn.config(state='normal')
    
    def update_progress(self, text):
        self.progress_label.config(text=text)
        self.root.update()

if __name__ == '__main__':
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()
"""

def create_installer_script():
    """Create the installer Python script."""
    print("Creating installer script...")
    INSTALLER_DIR.mkdir(exist_ok=True)
    script_path = INSTALLER_DIR / 'installer.py'
    script_path.write_text(INSTALLER_SCRIPT)
    return script_path

def copy_release_package():
    """Copy release package to installer directory."""
    print("Copying release package...")
    release_zip = SCRIPT_DIR / 'releases' / 'v1.0-beta' / 'DownloadsOrganizeR-v1.0-beta.zip'
    if not release_zip.exists():
        raise FileNotFoundError(f"Release package not found: {release_zip}")
    dest = INSTALLER_DIR / 'DownloadsOrganizeR-v1.0-beta.zip'
    shutil.copy2(release_zip, dest)
    return dest

def build_exe():
    """Build the EXE using PyInstaller."""
    print("Building EXE with PyInstaller...")
    
    installer_script = create_installer_script()
    release_zip = copy_release_package()
    
    # PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'DownloadsOrganizeR-Setup',
        '--icon', 'NONE',
        '--add-data', f'{release_zip};.',
        '--distpath', str(DIST_DIR / 'exe'),
        '--workpath', str(BUILD_DIR / 'installer'),
        '--specpath', str(INSTALLER_DIR),
        str(installer_script)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        raise RuntimeError(f"PyInstaller failed with code {result.returncode}")
    
    exe_path = DIST_DIR / 'exe' / 'DownloadsOrganizeR-Setup.exe'
    if exe_path.exists():
        print(f"\n✓ EXE installer created: {exe_path}")
        print(f"  Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")
        return exe_path
    else:
        raise FileNotFoundError("EXE not found after build")

def create_build_readme():
    """Create README for the EXE installer."""
    readme = DIST_DIR / 'exe' / 'README.md'
    readme.write_text("""# DownloadsOrganizeR - Windows EXE Installer

## Quick Start

1. Double-click `DownloadsOrganizeR-Setup.exe`
2. Choose installation directory (default: C:\\Scripts)
3. Select options:
   - Install Windows Service (optional, requires NSSM)
   - Start Dashboard after installation
4. Click **Install**
5. Open http://localhost:5000 to complete setup wizard

## Requirements

- Windows 10/11 or Windows Server 2016+
- Python 3.12+ (must be in system PATH)
- Administrator privileges
- NSSM (optional, for Windows service)

## What It Does

- Extracts DownloadsOrganizeR files to your chosen directory
- Creates Python virtual environment
- Installs required packages
- Initializes configuration files
- Optionally installs Windows service
- Starts web dashboard

## Troubleshooting

**Python not found:**
- Install Python 3.12+ from python.org
- Ensure "Add to PATH" is checked during installation

**Permission denied:**
- Right-click installer → "Run as Administrator"

**NSSM service failed:**
- Install NSSM from nssm.cc
- Add to system PATH
- Or skip service install and run manually

## Manual Service Installation

If you skipped service installation, you can install it later:

```powershell
cd C:\\Scripts
.\\Install-And-Monitor-OrganizerService.ps1
```

## Support

GitHub: https://github.com/Atomsk865/DownloadsOrganizeR
""")
    print(f"Created: {readme}")

if __name__ == '__main__':
    try:
        print("=" * 60)
        print("DownloadsOrganizeR EXE Installer Builder")
        print("=" * 60)
        
        # Check PyInstaller
        try:
            import PyInstaller
        except ImportError:
            print("\nERROR: PyInstaller not installed")
            print("Install with: pip install pyinstaller")
            sys.exit(1)
        
        exe_path = build_exe()
        create_build_readme()
        
        print("\n" + "=" * 60)
        print("BUILD COMPLETE!")
        print("=" * 60)
        print(f"\nInstaller location: {exe_path}")
        print("\nNext steps:")
        print("1. Test the installer on a clean Windows machine")
        print("2. Copy to releases/v1.0-beta/ for distribution")
        print("3. Upload to GitHub releases")
        
    except Exception as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)
