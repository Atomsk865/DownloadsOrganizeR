"""
DownloadsOrganizeR System Tray Application

A lightweight system tray application for managing the DownloadsOrganizeR service and dashboard.
Provides quick access to start/stop service, launch dashboard, and update from GitHub.
"""

import sys
import os
import subprocess
import webbrowser
from pathlib import Path
import json

try:
    from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, 
                                  QMessageBox, QWidget)
    from PyQt6.QtGui import QIcon, QAction
    from PyQt6.QtCore import QTimer, Qt
    PYQT_VERSION = 6
except ImportError:
    try:
        from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, 
                                      QMessageBox, QWidget)
        from PyQt5.QtGui import QIcon
        from PyQt5.QtCore import QTimer, Qt
        from PyQt5.QtWidgets import QAction
        PYQT_VERSION = 5
    except ImportError:
        print("Error: PyQt6 or PyQt5 is required. Install with:")
        print("  pip install PyQt6")
        print("  or")
        print("  pip install PyQt5")
        sys.exit(1)


class OrganizerTrayApp(QWidget):
    def __init__(self):
        super().__init__()
        self.service_name = "DownloadsOrganizer"
        self.dashboard_process = None
        self.dashboard_port = 5000
        
        # Get installation paths
        self.install_dir = self.get_install_dir()
        
        # Initialize system tray
        self.init_tray()
        
        # Check service status periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_service_status)
        self.timer.start(5000)  # Update every 5 seconds
        
        # Initial status update
        self.update_service_status()
    
    def get_install_dir(self):
        """Get installation directory from marker file or script location."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        marker_file = os.path.join(script_dir, ".install_path")
        
        if os.path.exists(marker_file):
            try:
                with open(marker_file, 'r') as f:
                    paths = json.loads(f.read().strip())
                    return paths.get('install_dir', script_dir)
            except Exception:
                pass
        
        return script_dir
    
    def init_tray(self):
        """Initialize system tray icon and menu."""
        # Create tray icon (use default for now, can be customized)
        self.tray_icon = QSystemTrayIcon(self)
        
        # Try to load custom icon, fallback to default
        icon_path = os.path.join(self.install_dir, "static", "img", "logo.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Use a default system icon
            self.tray_icon.setIcon(self.style().standardIcon(
                self.style().StandardPixmap.SP_ComputerIcon if PYQT_VERSION == 6
                else self.style().SP_ComputerIcon
            ))
        
        # Create menu
        menu = QMenu()
        
        # Service controls
        self.service_status_action = QAction("Service: Checking...", self)
        self.service_status_action.setEnabled(False)
        menu.addAction(self.service_status_action)
        
        menu.addSeparator()
        
        self.start_service_action = QAction("▶ Start Service", self)
        self.start_service_action.triggered.connect(self.start_service)
        menu.addAction(self.start_service_action)
        
        self.stop_service_action = QAction("■ Stop Service", self)
        self.stop_service_action.triggered.connect(self.stop_service)
        menu.addAction(self.stop_service_action)
        
        self.restart_service_action = QAction("⟲ Restart Service", self)
        self.restart_service_action.triggered.connect(self.restart_service)
        menu.addAction(self.restart_service_action)
        
        menu.addSeparator()
        
        # Dashboard controls
        self.dashboard_action = QAction("🌐 Open Dashboard", self)
        self.dashboard_action.triggered.connect(self.open_dashboard)
        menu.addAction(self.dashboard_action)
        
        self.launch_dashboard_action = QAction("▶ Start Dashboard Server", self)
        self.launch_dashboard_action.triggered.connect(self.launch_dashboard)
        menu.addAction(self.launch_dashboard_action)
        
        self.stop_dashboard_action = QAction("■ Stop Dashboard Server", self)
        self.stop_dashboard_action.triggered.connect(self.stop_dashboard)
        self.stop_dashboard_action.setEnabled(False)
        menu.addAction(self.stop_dashboard_action)
        
        menu.addSeparator()
        
        # Update action
        update_action = QAction("⬇ Update from GitHub", self)
        update_action.triggered.connect(self.update_system)
        menu.addAction(update_action)
        
        menu.addSeparator()
        
        # Exit action
        exit_action = QAction("✕ Exit", self)
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        
        # Double-click opens dashboard
        self.tray_icon.activated.connect(self.tray_activated)
    
    def tray_activated(self, reason):
        """Handle tray icon activation (clicks)."""
        if PYQT_VERSION == 6:
            from PyQt6.QtWidgets import QSystemTrayIcon
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
                self.open_dashboard()
        else:
            from PyQt5.QtWidgets import QSystemTrayIcon
            if reason == QSystemTrayIcon.DoubleClick:
                self.open_dashboard()
    
    def update_service_status(self):
        """Check service status and update UI."""
        try:
            result = subprocess.run(
                ["nssm", "status", self.service_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            status = result.stdout.strip()
            
            if "SERVICE_RUNNING" in status:
                self.service_status_action.setText("Service: ✓ Running")
                self.start_service_action.setEnabled(False)
                self.stop_service_action.setEnabled(True)
                self.restart_service_action.setEnabled(True)
            elif "SERVICE_STOPPED" in status:
                self.service_status_action.setText("Service: ✗ Stopped")
                self.start_service_action.setEnabled(True)
                self.stop_service_action.setEnabled(False)
                self.restart_service_action.setEnabled(False)
            else:
                self.service_status_action.setText(f"Service: {status}")
                self.start_service_action.setEnabled(True)
                self.stop_service_action.setEnabled(True)
                self.restart_service_action.setEnabled(True)
        
        except subprocess.TimeoutExpired:
            self.service_status_action.setText("Service: ⚠ Timeout")
        except FileNotFoundError:
            self.service_status_action.setText("Service: ⚠ NSSM not found")
        except Exception as e:
            self.service_status_action.setText(f"Service: ⚠ Error")
    
    def start_service(self):
        """Start the organizer service."""
        try:
            result = subprocess.run(
                ["nssm", "start", self.service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.show_notification("Service Started", 
                                      "DownloadsOrganizer service started successfully")
                self.update_service_status()
            else:
                self.show_error("Failed to start service", result.stderr)
        
        except Exception as e:
            self.show_error("Error starting service", str(e))
    
    def stop_service(self):
        """Stop the organizer service."""
        try:
            result = subprocess.run(
                ["nssm", "stop", self.service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.show_notification("Service Stopped", 
                                      "DownloadsOrganizer service stopped successfully")
                self.update_service_status()
            else:
                self.show_error("Failed to stop service", result.stderr)
        
        except Exception as e:
            self.show_error("Error stopping service", str(e))
    
    def restart_service(self):
        """Restart the organizer service."""
        try:
            result = subprocess.run(
                ["nssm", "restart", self.service_name],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                self.show_notification("Service Restarted", 
                                      "DownloadsOrganizer service restarted successfully")
                self.update_service_status()
            else:
                self.show_error("Failed to restart service", result.stderr)
        
        except Exception as e:
            self.show_error("Error restarting service", str(e))
    
    def open_dashboard(self):
        """Open dashboard in default web browser."""
        url = f"http://localhost:{self.dashboard_port}"
        webbrowser.open(url)
        self.show_notification("Opening Dashboard", 
                              f"Dashboard opening at {url}")
    
    def launch_dashboard(self):
        """Launch the dashboard server."""
        try:
            # Check if dashboard is already running
            if self.dashboard_process and self.dashboard_process.poll() is None:
                self.show_notification("Dashboard Running", 
                                      "Dashboard server is already running")
                return
            
            # Launch dashboard
            dashboard_script = os.path.join(self.install_dir, "OrganizerDashboard.py")
            
            if not os.path.exists(dashboard_script):
                self.show_error("Dashboard not found", 
                               f"Could not find {dashboard_script}")
                return
            
            # Start dashboard in background
            self.dashboard_process = subprocess.Popen(
                [sys.executable, dashboard_script],
                cwd=self.install_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            self.stop_dashboard_action.setEnabled(True)
            self.show_notification("Dashboard Started", 
                                  f"Dashboard server started on port {self.dashboard_port}")
            
            # Open in browser after short delay
            QTimer.singleShot(2000, self.open_dashboard)
        
        except Exception as e:
            self.show_error("Error launching dashboard", str(e))
    
    def stop_dashboard(self):
        """Stop the dashboard server."""
        if self.dashboard_process and self.dashboard_process.poll() is None:
            self.dashboard_process.terminate()
            try:
                self.dashboard_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.dashboard_process.kill()
            
            self.dashboard_process = None
            self.stop_dashboard_action.setEnabled(False)
            self.show_notification("Dashboard Stopped", 
                                  "Dashboard server stopped")
        else:
            self.show_notification("Dashboard Not Running", 
                                  "Dashboard server is not running")
    
    def update_system(self):
        """Pull latest updates from GitHub."""
        reply = QMessageBox.question(
            None,
            "Update System",
            "Pull latest updates from GitHub main branch?\n\n"
            "Config files will be backed up automatically.\n"
            "Service will be restarted after update.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.chdir(self.install_dir)
                
                # Check if git repository
                if not os.path.exists(os.path.join(self.install_dir, ".git")):
                    self.show_error("Not a Git Repository", 
                                   "Installation directory is not a git repository.\n"
                                   "Please reinstall using the installer.")
                    return
                
                # Git fetch
                result = subprocess.run(
                    ["git", "fetch", "origin", "main"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    self.show_error("Git Fetch Failed", result.stderr)
                    return
                
                # Git pull
                result = subprocess.run(
                    ["git", "pull", "origin", "main"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    self.show_error("Git Pull Failed", result.stderr)
                    return
                
                # Restart service
                subprocess.run(
                    ["nssm", "restart", self.service_name],
                    capture_output=True,
                    timeout=15
                )
                
                self.show_notification("Update Complete", 
                                      "System updated successfully!\n"
                                      "Service has been restarted.")
                self.update_service_status()
            
            except subprocess.TimeoutExpired:
                self.show_error("Update Timeout", 
                               "Git operation timed out. Check network connection.")
            except Exception as e:
                self.show_error("Update Failed", str(e))
    
    def show_notification(self, title, message):
        """Show system tray notification."""
        self.tray_icon.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information if PYQT_VERSION == 6
            else QSystemTrayIcon.Information,
            3000
        )
    
    def show_error(self, title, message):
        """Show error message box."""
        QMessageBox.critical(None, title, message)
    
    def exit_app(self):
        """Exit the application."""
        # Stop dashboard if running
        if self.dashboard_process and self.dashboard_process.poll() is None:
            self.dashboard_process.terminate()
        
        QApplication.quit()


def main():
    """Main entry point for the tray application."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when windows close
    
    # Check if already running (simple check)
    app.setApplicationName("DownloadsOrganizerTray")
    
    tray_app = OrganizerTrayApp()
    
    sys.exit(app.exec() if PYQT_VERSION == 6 else app.exec_())


if __name__ == "__main__":
    main()
