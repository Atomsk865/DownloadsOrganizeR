# Phase 1: Cross-Platform Implementation Guide

**Making Organizer.py work on Windows, macOS, and Linux**

**Duration:** 2-3 months  
**Team:** 2-3 developers  
**Effort:** ~162 hours  
**Outcome:** Single codebase supporting all three platforms

---

## Overview

This guide provides step-by-step implementation instructions for Phase 1 of the cross-platform expansion. By the end, your service will run identically on Windows, macOS, and Linux.

### Current State Analysis

Your code is in good shape! It already:
- ✅ Uses `pathlib` (cross-platform file paths)
- ✅ Uses `watchdog` (cross-platform file monitoring)
- ✅ Has platform detection in `auth.py`
- ✅ Has graceful fallbacks for non-Windows systems

**What needs to change:**
- ❌ Hardcoded Windows paths (C:\Users\, C:\Scripts\)
- ❌ Windows-only service management (NSSM)
- ❌ Windows-only authentication (win32security)
- ❌ Hardcoded file paths in config discovery

---

## Task 1: Refactor File Path Handling (Week 1-2)

### 1.1 Understand Current Path Usage

**Current code in Organizer.py:**

```python
# Line 43-44: Config path discovery (Windows-only)
config_paths = [
    "C:/Scripts/organizer_config.json",
    "C:/ProgramData/SortNStore/organizer_config.json",
    "organizer_config.json",
]

# Line 140: Downloads folder detection
downloads_path = Path(f"C:\\Users\\{username}\\Downloads")

# Line 142: Fallback (good, but we need to standardize)
if not downloads_path.exists():
    downloads_path = Path.home() / "Downloads"
```

**Files to modify:**
1. `Organizer.py` - Path discovery and resolution
2. `SortNStoreDashboard.py` - Config file paths
3. `organizer_config.json` - Update with platform notes

### 1.2 Create `platform_paths.py` Module

**New file: `SortNStoreDashboard/helpers/platform_paths.py`**

```python
"""
Cross-platform path resolution for SortNStore.

Provides platform-specific locations for config, logs, and data files.
"""

import platform
from pathlib import Path
from typing import List
import os


class PlatformPaths:
    """Manage platform-specific file paths."""
    
    PLATFORM = platform.system()
    
    @classmethod
    def get_platform(cls) -> str:
        """Get current platform: 'Windows', 'Darwin', 'Linux'."""
        return cls.PLATFORM
    
    @classmethod
    def is_windows(cls) -> bool:
        return cls.PLATFORM == 'Windows'
    
    @classmethod
    def is_macos(cls) -> bool:
        return cls.PLATFORM == 'Darwin'
    
    @classmethod
    def is_linux(cls) -> bool:
        return cls.PLATFORM == 'Linux'
    
    @classmethod
    def get_downloads_folder(cls, username: str = None) -> Path:
        """
        Get the Downloads folder for current platform.
        
        Args:
            username: Windows-specific username (optional)
        
        Returns:
            Path to Downloads folder
        
        Examples:
            - Windows: C:\\Users\\alice\\Downloads
            - macOS: /Users/alice/Downloads
            - Linux: /home/alice/Downloads
        """
        if cls.is_windows() and username:
            # Windows: explicit path
            downloads = Path(f"C:\\Users\\{username}\\Downloads")
            if downloads.exists():
                return downloads
        
        # Cross-platform fallback (macOS, Linux, or Windows if user not found)
        downloads = Path.home() / "Downloads"
        if downloads.exists():
            return downloads
        
        # Last resort: create Downloads if it doesn't exist
        downloads.mkdir(parents=True, exist_ok=True)
        return downloads
    
    @classmethod
    def get_config_paths(cls) -> List[Path]:
        """
        Get list of config file paths to search, in order of priority.
        
        Platform-specific locations + cross-platform fallbacks.
        """
        if cls.is_windows():
            return [
                # Windows: Program Files and ProgramData
                Path("C:/Scripts/organizer_config.json"),
                Path("C:/ProgramData/SortNStore/organizer_config.json"),
                # User home directory
                Path.home() / ".config" / "sortnstore" / "config.json",
                # Current directory (development)
                Path.cwd() / "organizer_config.json",
            ]
        
        elif cls.is_macos():
            return [
                # macOS: Application Support
                Path.home() / "Library" / "Application Support" / 
                    "SortNStore" / "config.json",
                # System-wide
                Path("/etc/sortnstore/config.json"),
                # User home directory
                Path.home() / ".config" / "sortnstore" / "config.json",
                # Current directory (development)
                Path.cwd() / "organizer_config.json",
            ]
        
        elif cls.is_linux():
            return [
                # Linux: Standard locations
                Path("/etc/sortnstore/config.json"),
                Path.home() / ".config" / "sortnstore" / "config.json"),
                Path("/opt/sortnstore/config.json"),
                # User home directory
                Path.home() / ".sortnstore" / "config.json",
                # Current directory (development)
                Path.cwd() / "organizer_config.json",
            ]
        
        else:
            # Unknown platform: try common locations
            return [
                Path.home() / ".config" / "sortnstore" / "config.json",
                Path.cwd() / "organizer_config.json",
            ]
    
    @classmethod
    def find_config_file(cls) -> Path:
        """
        Find the first existing config file from search paths.
        
        Returns:
            Path to config file
        
        Raises:
            FileNotFoundError: If no config file found
        """
        for config_path in cls.get_config_paths():
            if config_path.exists():
                return config_path
        
        # No config found - create default in user's home
        default_config = Path.home() / ".config" / "sortnstore" / "config.json"
        default_config.parent.mkdir(parents=True, exist_ok=True)
        return default_config
    
    @classmethod
    def get_logs_directory(cls) -> Path:
        """
        Get logs directory for current platform.
        
        Platform-specific locations:
        - Windows: C:\\Scripts\\service-logs
        - macOS: ~/Library/Logs/SortNStore
        - Linux: /var/log/sortnstore or ~/.local/share/sortnstore/logs
        """
        if cls.is_windows():
            logs_dir = Path("C:/Scripts/service-logs")
        elif cls.is_macos():
            logs_dir = Path.home() / "Library" / "Logs" / "SortNStore"
        elif cls.is_linux():
            # Try /var/log first (requires sudo for install)
            logs_dir = Path("/var/log/sortnstore")
            # Fallback to user home
            if not logs_dir.parent.exists() or not os.access(logs_dir.parent, os.W_OK):
                logs_dir = Path.home() / ".local" / "share" / "sortnstore" / "logs"
        else:
            logs_dir = Path.home() / ".sortnstore" / "logs"
        
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir
    
    @classmethod
    def get_downloads_organizer_log(cls, username: str = None) -> Path:
        """Get path to organizer.log in downloads folder."""
        downloads = cls.get_downloads_folder(username)
        return downloads / "organizer.log"
    
    @classmethod
    def get_cache_directory(cls) -> Path:
        """
        Get cache directory for current platform.
        
        Used for temporary files, hashes, etc.
        """
        if cls.is_windows():
            cache_dir = Path.home() / "AppData" / "Local" / "SortNStore" / "cache"
        elif cls.is_macos():
            cache_dir = Path.home() / "Library" / "Caches" / "SortNStore"
        elif cls.is_linux():
            cache_dir = Path.home() / ".cache" / "sortnstore"
        else:
            cache_dir = Path.home() / ".sortnstore" / "cache"
        
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    @classmethod
    def get_data_directory(cls) -> Path:
        """
        Get data directory for current platform.
        
        Used for persistent data files, databases, etc.
        """
        if cls.is_windows():
            data_dir = Path.home() / "AppData" / "Local" / "SortNStore" / "data"
        elif cls.is_macos():
            data_dir = Path.home() / "Library" / "Application Support" / \
                "SortNStore" / "data"
        elif cls.is_linux():
            data_dir = Path.home() / ".local" / "share" / "sortnstore"
        else:
            data_dir = Path.home() / ".sortnstore" / "data"
        
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    @classmethod
    def print_paths(cls):
        """Print all paths for current platform (useful for debugging)."""
        print(f"\n=== SortNStore Paths ({cls.get_platform()}) ===")
        print(f"Config paths to search:")
        for path in cls.get_config_paths():
            status = "✓ EXISTS" if path.exists() else "  missing"
            print(f"  {status}: {path}")
        print(f"\nConfig file: {cls.find_config_file()}")
        print(f"Downloads: {cls.get_downloads_folder()}")
        print(f"Logs: {cls.get_logs_directory()}")
        print(f"Cache: {cls.get_cache_directory()}")
        print(f"Data: {cls.get_data_directory()}")


# Convenient aliases
Paths = PlatformPaths
is_windows = PlatformPaths.is_windows
is_macos = PlatformPaths.is_macos
is_linux = PlatformPaths.is_linux
```

**Installation:**
```python
# In Organizer.py, replace old path code:

# OLD:
# config_paths = ["C:/Scripts/...", ...]
# downloads_path = Path(f"C:\\Users\\{username}\\Downloads")

# NEW:
from SortNStoreDashboard.helpers.platform_paths import Paths

config_file = Paths.find_config_file()
downloads_path = Paths.get_downloads_folder(username)
logs_dir = Paths.get_logs_directory()
```

### 1.3 Update Organizer.py

**File: `Organizer.py` (major refactoring)**

**Changes:**

```python
# At top of file, add:
from SortNStoreDashboard.helpers.platform_paths import Paths
import platform

# Replace lines 43-44 (old CONFIG_PATHS):
# OLD:
# CONFIG_PATHS = [
#     "C:/Scripts/organizer_config.json",
#     "C:/ProgramData/SortNStore/organizer_config.json",
#     "organizer_config.json",
# ]

# NEW:
def load_config_file():
    """Load config from first available location."""
    config_file = Paths.find_config_file()
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG

# Replace lines 140-142 (Downloads path detection):
# OLD:
# downloads_path = Path(f"C:\\Users\\{username}\\Downloads")
# if not downloads_path.exists():
#     downloads_path = Path.home() / "Downloads"

# NEW:
downloads_path = Paths.get_downloads_folder(username)

# Add at top of OrganizeHandler.__init__:
self.logs_dir = Paths.get_logs_directory()
self.config_file = Paths.find_config_file()
self.cache_dir = Paths.get_cache_directory()
```

### 1.4 Update SortNStoreDashboard.py

**File: `SortNStoreDashboard.py` (config loading)**

```python
# Add at top:
from SortNStoreDashboard.helpers.platform_paths import Paths
import platform

# In app initialization (find where config is loaded):
# OLD:
# config_path = "organizer_config.json"

# NEW:
config_path = Paths.find_config_file()

# In any route that references config paths:
@app.route('/api/config/paths')
def get_config_paths():
    """Return platform-specific paths for debugging."""
    return {
        'platform': Paths.get_platform(),
        'config_file': str(Paths.find_config_file()),
        'logs_directory': str(Paths.get_logs_directory()),
        'downloads_folder': str(Paths.get_downloads_folder()),
        'cache_directory': str(Paths.get_cache_directory()),
        'all_config_search_paths': [str(p) for p in Paths.get_config_paths()],
    }
```

### 1.5 Testing Path Resolution

**Create: `tests/test_platform_paths.py`**

```python
import pytest
from pathlib import Path
import platform
from SortNStoreDashboard.helpers.platform_paths import Paths


class TestPlatformPaths:
    """Test platform-specific path resolution."""
    
    def test_get_platform(self):
        """Test platform detection."""
        platform_name = Paths.get_platform()
        assert platform_name in ['Windows', 'Darwin', 'Linux']
    
    def test_is_platform_checks(self):
        """Test platform check methods."""
        if Paths.get_platform() == 'Windows':
            assert Paths.is_windows()
            assert not Paths.is_macos()
            assert not Paths.is_linux()
    
    def test_get_downloads_folder(self):
        """Test downloads folder detection."""
        downloads = Paths.get_downloads_folder()
        assert isinstance(downloads, Path)
        # Should have created if missing
        assert downloads.exists() or downloads.parent.exists()
    
    def test_get_downloads_folder_with_username(self):
        """Test downloads folder with username (Windows)."""
        downloads = Paths.get_downloads_folder(username="testuser")
        assert isinstance(downloads, Path)
    
    def test_config_paths_are_paths(self):
        """Test that config paths are Path objects."""
        config_paths = Paths.get_config_paths()
        assert isinstance(config_paths, list)
        assert all(isinstance(p, Path) for p in config_paths)
        assert len(config_paths) > 0
    
    def test_find_config_file(self):
        """Test config file discovery."""
        config_file = Paths.find_config_file()
        assert isinstance(config_file, Path)
        # Should return something (created if necessary)
        assert config_file.parent.exists() or config_file.parent.parent.exists()
    
    def test_get_logs_directory(self):
        """Test logs directory creation."""
        logs_dir = Paths.get_logs_directory()
        assert isinstance(logs_dir, Path)
        assert logs_dir.exists()
    
    def test_get_cache_directory(self):
        """Test cache directory creation."""
        cache_dir = Paths.get_cache_directory()
        assert isinstance(cache_dir, Path)
        assert cache_dir.exists()
    
    def test_get_data_directory(self):
        """Test data directory creation."""
        data_dir = Paths.get_data_directory()
        assert isinstance(data_dir, Path)
        assert data_dir.exists()
    
    def test_paths_are_writable(self):
        """Test that paths are writable."""
        import os
        
        logs_dir = Paths.get_logs_directory()
        assert os.access(logs_dir, os.W_OK), f"Cannot write to {logs_dir}"
        
        cache_dir = Paths.get_cache_directory()
        assert os.access(cache_dir, os.W_OK), f"Cannot write to {cache_dir}"
```

**Run tests:**
```bash
pytest tests/test_platform_paths.py -v
```

---

## Task 2: Refactor Service Management (Week 2-3)

### 2.1 Create Service Manager Abstraction

**New file: `SortNStoreDashboard/services/service_manager.py`**

```python
"""
Cross-platform service management.

Abstracts Windows (NSSM), macOS (launchctl), and Linux (systemd) service management.
"""

import platform
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import json


class ServiceManager(ABC):
    """Abstract base class for service managers."""
    
    def __init__(self, service_name: str = "SortNStore"):
        self.service_name = service_name
        self.platform = platform.system()
    
    @abstractmethod
    def install(self, python_script_path: str, description: str = None) -> bool:
        """Install service."""
        pass
    
    @abstractmethod
    def uninstall(self) -> bool:
        """Uninstall service."""
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """Start service."""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Stop service."""
        pass
    
    @abstractmethod
    def restart(self) -> bool:
        """Restart service."""
        pass
    
    @abstractmethod
    def get_status(self) -> str:
        """Get service status: 'running', 'stopped', 'not_found'."""
        pass
    
    @abstractmethod
    def enable_autostart(self) -> bool:
        """Enable service to start on boot."""
        pass
    
    @abstractmethod
    def disable_autostart(self) -> bool:
        """Disable service autostart."""
        pass


class WindowsServiceManager(ServiceManager):
    """Windows service management via NSSM."""
    
    def install(self, python_script_path: str, description: str = None) -> bool:
        """Install as Windows service via NSSM."""
        try:
            # Check if NSSM is installed
            subprocess.run(['nssm', '--version'], 
                         capture_output=True, check=True)
        except FileNotFoundError:
            raise RuntimeError("NSSM not found. Install from nssm.cc")
        
        try:
            # Get python executable path
            python_exe = Path(sys.__executable__)
            
            # Install service
            subprocess.run([
                'nssm', 'install', self.service_name,
                str(python_exe),
                python_script_path
            ], check=True)
            
            # Set description
            if description:
                subprocess.run([
                    'nssm', 'set', self.service_name,
                    'Description', description
                ], check=True)
            
            # Set to restart on failure
            subprocess.run([
                'nssm', 'set', self.service_name,
                'AppRestartDelay', '5000'
            ], check=True)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install service: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall Windows service."""
        try:
            subprocess.run([
                'nssm', 'remove', self.service_name, 'confirm'
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def start(self) -> bool:
        """Start Windows service."""
        try:
            subprocess.run([
                'net', 'start', self.service_name
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def stop(self) -> bool:
        """Stop Windows service."""
        try:
            subprocess.run([
                'net', 'stop', self.service_name
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def restart(self) -> bool:
        """Restart Windows service."""
        return self.stop() and self.start()
    
    def get_status(self) -> str:
        """Get Windows service status."""
        try:
            result = subprocess.run([
                'sc', 'query', self.service_name
            ], capture_output=True, text=True)
            
            if 'RUNNING' in result.stdout:
                return 'running'
            elif 'STOPPED' in result.stdout:
                return 'stopped'
            else:
                return 'unknown'
        except Exception:
            return 'not_found'
    
    def enable_autostart(self) -> bool:
        """Enable Windows service autostart."""
        try:
            subprocess.run([
                'sc', 'config', self.service_name,
                'start=', 'auto'
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def disable_autostart(self) -> bool:
        """Disable Windows service autostart."""
        try:
            subprocess.run([
                'sc', 'config', self.service_name,
                'start=', 'manual'
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False


class LinuxSystemdManager(ServiceManager):
    """Linux service management via systemd."""
    
    def get_service_file_path(self) -> Path:
        """Get systemd service file path."""
        return Path(f"/etc/systemd/system/{self.service_name}.service")
    
    def get_service_content(self, python_script_path: str) -> str:
        """Generate systemd service file content."""
        return f"""[Unit]
Description=SortNStore File Organization Service
After=network.target

[Service]
Type=simple
User=sortnstore
WorkingDirectory={Path(python_script_path).parent}
ExecStart=/usr/bin/python3 {python_script_path}
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/log/sortnstore/service.log
StandardError=append:/var/log/sortnstore/service-error.log

[Install]
WantedBy=multi-user.target
"""
    
    def install(self, python_script_path: str, description: str = None) -> bool:
        """Install as systemd service."""
        try:
            # Create service file
            service_file = self.get_service_file_path()
            service_content = self.get_service_content(python_script_path)
            
            # Write service file (requires sudo)
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            # Reload systemd
            subprocess.run(['systemctl', 'daemon-reload'], 
                         check=True, capture_output=True)
            
            # Enable service
            self.enable_autostart()
            
            return True
        except (PermissionError, subprocess.CalledProcessError) as e:
            print(f"Failed to install service: {e}")
            print("Hint: Run with sudo or as root")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall systemd service."""
        try:
            self.stop()
            self.disable_autostart()
            
            service_file = self.get_service_file_path()
            if service_file.exists():
                service_file.unlink()
            
            subprocess.run(['systemctl', 'daemon-reload'], 
                         check=True, capture_output=True)
            return True
        except (PermissionError, subprocess.CalledProcessError):
            return False
    
    def start(self) -> bool:
        """Start systemd service."""
        try:
            subprocess.run([
                'systemctl', 'start', self.service_name
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def stop(self) -> bool:
        """Stop systemd service."""
        try:
            subprocess.run([
                'systemctl', 'stop', self.service_name
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def restart(self) -> bool:
        """Restart systemd service."""
        try:
            subprocess.run([
                'systemctl', 'restart', self.service_name
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_status(self) -> str:
        """Get systemd service status."""
        try:
            result = subprocess.run([
                'systemctl', 'is-active', self.service_name
            ], capture_output=True, text=True)
            
            status = result.stdout.strip()
            if status == 'active':
                return 'running'
            elif status == 'inactive':
                return 'stopped'
            else:
                return status
        except Exception:
            return 'not_found'
    
    def enable_autostart(self) -> bool:
        """Enable systemd service autostart."""
        try:
            subprocess.run([
                'systemctl', 'enable', self.service_name
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def disable_autostart(self) -> bool:
        """Disable systemd service autostart."""
        try:
            subprocess.run([
                'systemctl', 'disable', self.service_name
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False


class MacOSLaunchctlManager(ServiceManager):
    """macOS service management via launchctl."""
    
    def get_plist_path(self) -> Path:
        """Get plist file path."""
        return Path.home() / "Library" / "LaunchAgents" / \
            f"com.sortnstore.{self.service_name}.plist"
    
    def get_plist_content(self, python_script_path: str, description: str = None) -> str:
        """Generate launchctl plist content."""
        import plistlib
        
        plist_dict = {
            'Label': f'com.sortnstore.{self.service_name}',
            'ProgramArguments': [
                '/usr/local/bin/python3',
                python_script_path
            ],
            'RunAtLoad': True,
            'KeepAlive': True,
            'StandardOutPath': str(Path.home() / f".local/share/sortnstore/{self.service_name}.log"),
            'StandardErrorPath': str(Path.home() / f".local/share/sortnstore/{self.service_name}-error.log"),
        }
        
        if description:
            plist_dict['Description'] = description
        
        return plistlib.dumps(plist_dict).decode('utf-8')
    
    def install(self, python_script_path: str, description: str = None) -> bool:
        """Install as launchctl service."""
        try:
            # Create plist file
            plist_path = self.get_plist_path()
            plist_path.parent.mkdir(parents=True, exist_ok=True)
            
            plist_content = self.get_plist_content(python_script_path, description)
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            # Load service
            subprocess.run([
                'launchctl', 'load', str(plist_path)
            ], check=True, capture_output=True)
            
            return True
        except (PermissionError, subprocess.CalledProcessError) as e:
            print(f"Failed to install service: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall launchctl service."""
        try:
            plist_path = self.get_plist_path()
            
            # Unload service
            subprocess.run([
                'launchctl', 'unload', str(plist_path)
            ], check=False, capture_output=True)
            
            # Remove plist
            if plist_path.exists():
                plist_path.unlink()
            
            return True
        except Exception:
            return False
    
    def start(self) -> bool:
        """Start launchctl service."""
        try:
            service_label = f'com.sortnstore.{self.service_name}'
            subprocess.run([
                'launchctl', 'start', service_label
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def stop(self) -> bool:
        """Stop launchctl service."""
        try:
            service_label = f'com.sortnstore.{self.service_name}'
            subprocess.run([
                'launchctl', 'stop', service_label
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def restart(self) -> bool:
        """Restart launchctl service."""
        return self.stop() and self.start()
    
    def get_status(self) -> str:
        """Get launchctl service status."""
        try:
            service_label = f'com.sortnstore.{self.service_name}'
            result = subprocess.run([
                'launchctl', 'list'
            ], capture_output=True, text=True)
            
            if service_label in result.stdout:
                return 'running'
            else:
                return 'stopped'
        except Exception:
            return 'not_found'
    
    def enable_autostart(self) -> bool:
        """macOS launchctl always autostarts if loaded."""
        return True
    
    def disable_autostart(self) -> bool:
        """Disable autostart by unloading plist."""
        plist_path = self.get_plist_path()
        try:
            subprocess.run([
                'launchctl', 'unload', str(plist_path)
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False


def get_service_manager(service_name: str = "SortNStore") -> ServiceManager:
    """Get platform-specific service manager."""
    platform_name = platform.system()
    
    if platform_name == 'Windows':
        return WindowsServiceManager(service_name)
    elif platform_name == 'Darwin':
        return MacOSLaunchctlManager(service_name)
    elif platform_name == 'Linux':
        return LinuxSystemdManager(service_name)
    else:
        raise NotImplementedError(f"Platform {platform_name} not supported")
```

### 2.2 Testing Service Management

**Create: `tests/test_service_manager.py`**

```python
import pytest
import platform
from SortNStoreDashboard.services.service_manager import get_service_manager


class TestServiceManager:
    """Test service manager abstraction."""
    
    def test_get_service_manager(self):
        """Test getting correct service manager for platform."""
        manager = get_service_manager()
        assert manager is not None
        
        platform_name = platform.system()
        if platform_name == 'Windows':
            from SortNStoreDashboard.services.service_manager import WindowsServiceManager
            assert isinstance(manager, WindowsServiceManager)
        elif platform_name == 'Darwin':
            from SortNStoreDashboard.services.service_manager import MacOSLaunchctlManager
            assert isinstance(manager, MacOSLaunchctlManager)
        elif platform_name == 'Linux':
            from SortNStoreDashboard.services.service_manager import LinuxSystemdManager
            assert isinstance(manager, LinuxSystemdManager)
    
    def test_service_manager_has_methods(self):
        """Test that service manager has all required methods."""
        manager = get_service_manager()
        
        assert hasattr(manager, 'install')
        assert hasattr(manager, 'uninstall')
        assert hasattr(manager, 'start')
        assert hasattr(manager, 'stop')
        assert hasattr(manager, 'restart')
        assert hasattr(manager, 'get_status')
        assert hasattr(manager, 'enable_autostart')
        assert hasattr(manager, 'disable_autostart')
    
    def test_get_status(self):
        """Test getting service status."""
        manager = get_service_manager()
        status = manager.get_status()
        
        # Should return one of these values
        assert status in ['running', 'stopped', 'unknown', 'not_found']
```

---

## Task 3: Refactor Authentication (Week 3-4)

### 3.1 Review Current Authentication Code

**Current auth.py:**
- Already has platform detection ✅
- Already has graceful fallbacks ✅
- Just needs enhancement

### 3.2 Create Authentication Abstraction

**New file: `SortNStoreDashboard/auth/auth_backends.py`**

```python
"""
Multi-platform authentication backends.

Supports:
- Windows Active Directory (Windows)
- Unix PAM (macOS, Linux)
- LDAP (all platforms)
- Local file auth (all platforms, fallback)
"""

import platform
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
import bcrypt
import json
from pathlib import Path


class AuthBackend(ABC):
    """Abstract base class for authentication backends."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.platform = platform.system()
    
    @abstractmethod
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """
        Authenticate user.
        
        Returns:
            (success: bool, user_info: Optional[Dict])
        """
        pass
    
    @abstractmethod
    def get_user_groups(self, username: str) -> list:
        """Get list of groups user belongs to."""
        pass


class LocalFileAuth(AuthBackend):
    """
    File-based authentication using bcrypt hashes.
    
    Works on all platforms. Stores users in JSON file.
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.users_file = Path.home() / ".sortnstore" / "users.json"
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_users(self) -> Dict:
        """Load users from file."""
        if not self.users_file.exists():
            return {}
        
        with open(self.users_file, 'r') as f:
            return json.load(f)
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """Authenticate against local password file."""
        users = self.load_users()
        
        if username not in users:
            return False, None
        
        user_data = users[username]
        password_hash = user_data.get('password_hash')
        
        if not password_hash:
            return False, None
        
        # Verify password
        if bcrypt.checkpw(password.encode(), password_hash.encode()):
            return True, {
                'username': username,
                'groups': user_data.get('groups', []),
                'email': user_data.get('email'),
            }
        
        return False, None
    
    def get_user_groups(self, username: str) -> list:
        """Get user groups from file."""
        users = self.load_users()
        if username in users:
            return users[username].get('groups', [])
        return []
    
    @classmethod
    def create_user(cls, username: str, password: str, groups: list = None):
        """Create a new user (admin setup)."""
        users_file = Path.home() / ".sortnstore" / "users.json"
        users_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing users
        if users_file.exists():
            with open(users_file, 'r') as f:
                users = json.load(f)
        else:
            users = {}
        
        # Hash password
        password_hash = bcrypt.hashpw(
            password.encode(), 
            bcrypt.gensalt(rounds=12)
        ).decode()
        
        # Add/update user
        users[username] = {
            'password_hash': password_hash,
            'groups': groups or [],
        }
        
        # Save
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)


class LDAPAuth(AuthBackend):
    """
    LDAP authentication backend.
    
    Works on all platforms. Requires LDAP server.
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        try:
            import ldap3
            self.ldap3 = ldap3
        except ImportError:
            raise ImportError("ldap3 package required for LDAP auth")
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """Authenticate against LDAP server."""
        if not self.config.get('server'):
            return False, None
        
        try:
            server = self.ldap3.Server(
                self.config['server'],
                port=self.config.get('port', 389),
                use_ssl=self.config.get('use_ssl', False)
            )
            
            # Try to bind with user credentials
            user_dn = self.config.get('user_dn_template', 
                                     f"uid={username},ou=people,dc=example,dc=com")
            user_dn = user_dn.replace('{username}', username)
            
            conn = self.ldap3.Connection(server, user_dn, password)
            
            if conn.bind():
                # Get user groups
                groups = self.get_user_groups(username)
                return True, {
                    'username': username,
                    'groups': groups,
                }
            else:
                return False, None
        
        except Exception as e:
            print(f"LDAP auth error: {e}")
            return False, None
    
    def get_user_groups(self, username: str) -> list:
        """Get user groups from LDAP."""
        # Implementation depends on LDAP schema
        return []


class WindowsActiveDirectoryAuth(AuthBackend):
    """
    Windows Active Directory authentication.
    
    Windows-only. Uses win32security.
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        if self.platform != 'Windows':
            raise RuntimeError("Windows AD auth only on Windows")
        
        try:
            import win32security
            self.win32security = win32security
        except ImportError:
            raise ImportError("pywin32 package required for Windows AD auth")
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """Authenticate against Windows AD."""
        try:
            # Try SSPI authentication
            handle = self.win32security.GetUserHandle(username, password)
            groups = self.get_user_groups(username)
            
            return True, {
                'username': username,
                'groups': groups,
            }
        except Exception as e:
            print(f"Windows AD auth error: {e}")
            return False, None
    
    def get_user_groups(self, username: str) -> list:
        """Get user groups from Windows AD."""
        try:
            import win32api
            import win32con
            
            # Get user SID and groups
            # Implementation depends on AD configuration
            return []
        except Exception:
            return []


class UnixPAMAuth(AuthBackend):
    """
    Unix PAM authentication (macOS, Linux).
    
    Uses system PAM for authentication.
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        if self.platform not in ['Darwin', 'Linux']:
            raise RuntimeError("Unix PAM auth only on macOS/Linux")
        
        try:
            import pam
            self.pam = pam
        except ImportError:
            raise ImportError("python-pam package required for Unix PAM auth")
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """Authenticate using Unix PAM."""
        try:
            pam_auth = self.pam.pam()
            if pam_auth.authenticate(username, password):
                groups = self.get_user_groups(username)
                return True, {
                    'username': username,
                    'groups': groups,
                }
            else:
                return False, None
        except Exception as e:
            print(f"PAM auth error: {e}")
            return False, None
    
    def get_user_groups(self, username: str) -> list:
        """Get user groups (macOS/Linux)."""
        try:
            import grp
            import pwd
            
            # Get user info
            user_info = pwd.getpwnam(username)
            user_gid = user_info.pw_gid
            
            # Get group names
            groups = [grp.getgrgid(user_gid).gr_name]
            
            # Get additional groups
            for group in grp.getall():
                if username in group.gr_mem:
                    groups.append(group.gr_name)
            
            return groups
        except Exception:
            return []


def get_auth_backend(config: Dict = None) -> AuthBackend:
    """
    Get appropriate authentication backend for platform.
    
    Priority:
    1. LDAP (if configured)
    2. Windows AD (if on Windows and configured)
    3. Unix PAM (if on macOS/Linux)
    4. Local file auth (fallback)
    """
    config = config or {}
    platform_name = platform.system()
    
    # LDAP (all platforms)
    if config.get('auth_method') == 'ldap':
        try:
            return LDAPAuth(config)
        except ImportError:
            print("Warning: LDAP requested but ldap3 not installed")
    
    # Windows AD (Windows only)
    if platform_name == 'Windows':
        if config.get('auth_method') == 'windows_ad':
            try:
                return WindowsActiveDirectoryAuth(config)
            except (ImportError, RuntimeError):
                print("Warning: Windows AD requested but unavailable")
    
    # Unix PAM (macOS/Linux)
    if platform_name in ['Darwin', 'Linux']:
        if config.get('auth_method') == 'pam':
            try:
                return UnixPAMAuth(config)
            except (ImportError, RuntimeError):
                print("Warning: PAM requested but unavailable")
    
    # Fallback: local file auth
    return LocalFileAuth(config)
```

### 3.3 Update Authentication Usage

**In SortNStoreDashboard.py:**

```python
from SortNStoreDashboard.auth.auth_backends import get_auth_backend

# In authentication route
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Get auth backend for platform
    auth_backend = get_auth_backend(load_auth_config())
    
    # Authenticate
    success, user_info = auth_backend.authenticate(username, password)
    
    if success:
        # Create session/token
        return jsonify({'token': create_token(user_info)})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
```

---

## Task 4: Update Dashboard Templates (Week 4)

### 4.1 Add Platform Info to Templates

**In SortNStoreDashboard.py:**

```python
import platform

@app.context_processor
def inject_platform_info():
    """Make platform info available to all templates."""
    return {
        'platform': platform.system(),
        'platform_version': platform.release(),
        'python_version': platform.python_version(),
        'is_windows': platform.system() == 'Windows',
        'is_mac': platform.system() == 'Darwin',
        'is_linux': platform.system() == 'Linux',
    }
```

### 4.2 Update Dashboard HTML

**In dash/dashboard.html:**

```html
<!-- Platform-specific sections -->
<div class="platform-info">
    <p>Running on <strong>{{ platform }}</strong> {{ platform_version }}</p>
</div>

<!-- Platform-specific controls -->
{% if is_windows %}
    <div class="windows-controls">
        <button onclick="restartWindowsService()">Restart Service (Windows)</button>
    </div>
{% elif is_mac %}
    <div class="macos-controls">
        <button onclick="restartMacService()">Restart Service (macOS)</button>
    </div>
{% elif is_linux %}
    <div class="linux-controls">
        <button onclick="restartLinuxService()">Restart Service (Linux)</button>
    </div>
{% endif %}
```

---

## Summary of Changes

| Component | Change | Effort |
|-----------|--------|--------|
| **platform_paths.py** | New module for path resolution | 15 hrs |
| **Organizer.py** | Use platform paths module | 10 hrs |
| **Dashboard.py** | Use platform paths module | 5 hrs |
| **service_manager.py** | New abstraction layer | 35 hrs |
| **auth_backends.py** | New authentication abstraction | 30 hrs |
| **Update auth.py** | Integrate new backends | 10 hrs |
| **Templates** | Platform-specific UI | 10 hrs |
| **Testing** | Comprehensive test suite | 40 hrs |
| **Documentation** | Installation guides, etc. | 15 hrs |
| **Integration/QA** | Testing on all platforms | 40 hrs |
| **TOTAL** | | **210 hrs** |

---

## Next Steps After Phase 1

Once Phase 1 is complete:

1. **Create platform-specific installers** (Phase 2)
2. **Design and build mobile apps** (Phase 3)
3. **Comprehensive security audit** across all platforms
4. **Performance benchmarking** on all platforms
5. **User documentation** for multi-platform setup

This foundation enables everything else!
