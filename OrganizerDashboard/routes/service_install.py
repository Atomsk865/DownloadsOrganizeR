"""Service installation management routes."""

from flask import Blueprint, jsonify, request
import sys
import os
import platform
import subprocess

routes_service_install = Blueprint('routes_service_install', __name__)


@routes_service_install.route('/api/service/install', methods=['POST'])
def install_service():
    """Install the Organizer service using PowerShell script."""
    from OrganizerDashboard.auth.auth import requires_right
    
    @requires_right('manage_service')
    def _install():
        if platform.system() != 'Windows':
            return jsonify({'error': 'Service installation only available on Windows'}), 400
        
        data = request.get_json() or {}
        service_name = data.get('service_name', 'DownloadsOrganizer')
        scripts_root = data.get('scripts_root', r'C:\Scripts')
        memory_threshold = data.get('memory_threshold_mb', 200)
        cpu_threshold = data.get('cpu_threshold_percent', 60)
        
        # Find the installer script
        main = sys.modules['__main__']
        script_dir = os.path.dirname(os.path.abspath(main.__file__))
        installer_path = os.path.join(script_dir, 'Install-And-Monitor-OrganizerService.ps1')
        
        if not os.path.exists(installer_path):
            return jsonify({'error': 'Installer script not found'}), 404
        
        try:
            # Build PowerShell command
            ps_args = [
                'powershell.exe',
                '-NoProfile',
                '-ExecutionPolicy', 'Bypass',
                '-File', installer_path,
                '-ServiceName', service_name,
                '-ScriptsRoot', scripts_root,
                '-MemoryThresholdMB', str(memory_threshold),
                '-CpuThresholdPercent', str(cpu_threshold)
            ]
            
            # Run as admin (requires UAC prompt)
            result = subprocess.run(
                ps_args,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': f'Service {service_name} installed successfully',
                    'output': result.stdout
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Installation failed',
                    'output': result.stdout,
                    'error_output': result.stderr
                }), 500
                
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Installation timed out'}), 500
        except Exception as e:
            return jsonify({'error': f'Installation failed: {str(e)}'}), 500
    
    return _install()


@routes_service_install.route('/api/service/uninstall', methods=['POST'])
def uninstall_service():
    """Uninstall the Organizer service."""
    from OrganizerDashboard.auth.auth import requires_right
    
    @requires_right('manage_service')
    def _uninstall():
        if platform.system() != 'Windows':
            return jsonify({'error': 'Service management only available on Windows'}), 400
        
        data = request.get_json() or {}
        service_name = data.get('service_name', 'DownloadsOrganizer')
        
        try:
            # Use NSSM to remove the service
            result = subprocess.run(
                ['nssm', 'remove', service_name, 'confirm'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': f'Service {service_name} uninstalled successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Uninstallation failed: {result.stderr}'
                }), 500
                
        except FileNotFoundError:
            return jsonify({'error': 'NSSM not found. Is it installed?'}), 404
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Uninstallation timed out'}), 500
        except Exception as e:
            return jsonify({'error': f'Uninstallation failed: {str(e)}'}), 500
    
    return _uninstall()


@routes_service_install.route('/api/service/reinstall', methods=['POST'])
def reinstall_service():
    """Reinstall the Organizer service (uninstall then install)."""
    from OrganizerDashboard.auth.auth import requires_right
    
    @requires_right('manage_service')
    def _reinstall():
        if platform.system() != 'Windows':
            return jsonify({'error': 'Service management only available on Windows'}), 400
        
        data = request.get_json() or {}
        service_name = data.get('service_name', 'DownloadsOrganizer')
        
        # First uninstall
        try:
            subprocess.run(
                ['nssm', 'remove', service_name, 'confirm'],
                capture_output=True,
                text=True,
                timeout=30,
                check=False  # Don't fail if service doesn't exist
            )
        except Exception:
            pass  # Continue even if uninstall fails
        
        # Then install
        main = sys.modules['__main__']
        script_dir = os.path.dirname(os.path.abspath(main.__file__))
        installer_path = os.path.join(script_dir, 'Install-And-Monitor-OrganizerService.ps1')
        
        if not os.path.exists(installer_path):
            return jsonify({'error': 'Installer script not found'}), 404
        
        try:
            scripts_root = data.get('scripts_root', r'C:\Scripts')
            memory_threshold = data.get('memory_threshold_mb', 200)
            cpu_threshold = data.get('cpu_threshold_percent', 60)
            
            ps_args = [
                'powershell.exe',
                '-NoProfile',
                '-ExecutionPolicy', 'Bypass',
                '-File', installer_path,
                '-ServiceName', service_name,
                '-ScriptsRoot', scripts_root,
                '-MemoryThresholdMB', str(memory_threshold),
                '-CpuThresholdPercent', str(cpu_threshold)
            ]
            
            result = subprocess.run(
                ps_args,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': f'Service {service_name} reinstalled successfully',
                    'output': result.stdout
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Reinstallation failed',
                    'output': result.stdout,
                    'error_output': result.stderr
                }), 500
                
        except Exception as e:
            return jsonify({'error': f'Reinstallation failed: {str(e)}'}), 500
    
    return _reinstall()


@routes_service_install.route('/api/service/installation-config', methods=['GET'])
def get_installation_config():
    """Get current service installation configuration."""
    from OrganizerDashboard.auth.auth import requires_right
    
    @requires_right('manage_service')
    def _get_config():
        main = sys.modules['__main__']
        config = main.config
        
        return jsonify({
            'service_name': config.get('service_name', 'DownloadsOrganizer'),
            'scripts_root': r'C:\Scripts',
            'memory_threshold_mb': config.get('memory_threshold_mb', 200),
            'cpu_threshold_percent': config.get('cpu_threshold_percent', 60),
            'is_windows': platform.system() == 'Windows'
        })
    
    return _get_config()
