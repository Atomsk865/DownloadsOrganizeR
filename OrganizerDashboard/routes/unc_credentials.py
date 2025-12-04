"""UNC path credential management routes."""

from flask import Blueprint, jsonify, request
import sys
import os
import subprocess
import json
from OrganizerDashboard.auth.auth import requires_right

routes_unc_creds = Blueprint('routes_unc_creds', __name__)


@routes_unc_creds.route('/api/unc/validate-syntax', methods=['POST'])
@requires_right('manage_config')
def validate_unc_syntax():
    """Validate UNC path syntax and check if it's reachable."""
    data = request.get_json() or {}
    unc_path = data.get('path', '').strip()
    
    if not unc_path:
        return jsonify({'error': 'UNC path required'}), 400
    
    # Basic UNC syntax validation
    if not (unc_path.startswith('\\\\') or unc_path.startswith('\\\\')):
        return jsonify({'error': 'Invalid UNC path format. Must start with \\\\ (e.g., \\\\server\\share)'}), 400
    
    # Try to check if path is reachable
    try:
        if os.path.exists(unc_path):
            return jsonify({'success': True, 'reachable': True, 'message': 'UNC path is reachable'})
        else:
            return jsonify({'success': False, 'reachable': False, 'message': 'UNC path not reachable. May require authentication.'}), 200
    except Exception as e:
        return jsonify({'success': False, 'reachable': False, 'message': f'Path check failed: {str(e)}'}), 200


@routes_unc_creds.route('/api/unc/test-credentials', methods=['POST'])
@requires_right('manage_config')
def test_credentials():
    """Test UNC path credentials before saving."""
    data = request.get_json() or {}
    unc_path = data.get('path', '').strip()
    auth_type = data.get('auth_type', 'windows').lower()
    hostname = data.get('hostname', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    domain = data.get('domain', '').strip()
    
    if not unc_path:
        return jsonify({'error': 'UNC path required'}), 400
    
    # Basic syntax check
    if not (unc_path.startswith('\\\\') or unc_path.startswith('\\\\')):
        return jsonify({'error': 'Invalid UNC path format. Must start with \\\\ (e.g., \\\\server\\share)'}), 400
    
    if auth_type == 'windows':
        if not username or not password:
            return jsonify({'error': 'Windows auth requires username and password'}), 400
        
        # Attempt to mount/test on Windows
        try:
            if os.name == 'nt':  # Windows only
                # Try to access the path with credentials
                # On Windows, we can try to map a temporary drive or just test access
                test_result = test_unc_access_windows(unc_path, username, password, domain)
                if test_result['success']:
                    return jsonify({'success': True, 'message': 'Credentials verified successfully'})
                else:
                    return jsonify({'error': f"Authentication failed: {test_result.get('error', 'Unknown error')}"}), 401
            else:
                return jsonify({'error': 'Windows auth only available on Windows'}), 400
        except Exception as e:
            return jsonify({'error': f'Credential test failed: {str(e)}'}), 401
    
    elif auth_type == 'ldap':
        if not username or not password:
            return jsonify({'error': 'LDAP auth requires username and password'}), 400
        
        # For LDAP, we can at least validate the path is reachable
        try:
            if os.path.exists(unc_path):
                return jsonify({'success': True, 'message': 'UNC path is reachable with LDAP configuration'})
            else:
                return jsonify({'error': 'UNC path not reachable'}), 401
        except Exception as e:
            return jsonify({'error': f'Path access failed: {str(e)}'}), 401
    
    else:
        return jsonify({'error': 'Invalid auth type. Must be "windows" or "ldap"'}), 400


def test_unc_access_windows(unc_path: str, username: str, password: str, domain: str = '') -> dict:
    """Test UNC access on Windows using net use command."""
    try:
        # Construct username with domain if provided
        full_username = f"{domain}\\{username}" if domain else username
        
        # Try to list the path to verify access
        if os.path.exists(unc_path):
            # Path is accessible
            return {'success': True, 'message': 'Path is accessible'}
        
        # If path doesn't exist, try via net use command
        cmd = f'net use "{unc_path}" "{password}" /user:{full_username} /persistent:no'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            # Disconnect
            subprocess.run(f'net use "{unc_path}" /delete', shell=True, capture_output=True, timeout=5)
            return {'success': True, 'message': 'Credentials verified'}
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            return {'success': False, 'error': error_msg}
    
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Connection timed out'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


@routes_unc_creds.route('/api/unc/save-credentials', methods=['POST'])
@requires_right('manage_config')
def save_credentials():
    """Save UNC path credentials to config."""
    data = request.get_json() or {}
    unc_path = data.get('path', '').strip()
    auth_type = data.get('auth_type', 'windows').lower()
    hostname = data.get('hostname', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    domain = data.get('domain', '').strip()
    
    if not unc_path or not username or not password:
        return jsonify({'error': 'UNC path, username, and password are required'}), 400
    
    try:
        main = sys.modules['__main__']
        config = getattr(main, 'config', {})
        
        # Initialize unc_credentials if not present
        if 'unc_credentials' not in config:
            config['unc_credentials'] = {}
        
        # Only store non-empty fields
        cred_entry = {
            'auth_type': auth_type,
            'path': unc_path
        }
        
        if username:
            cred_entry['username'] = username
        if password:
            cred_entry['password'] = password
        if domain:
            cred_entry['domain'] = domain
        if hostname:
            cred_entry['hostname'] = hostname
        
        # Use path as key (URL-encode for safety)
        path_key = unc_path.replace('\\', '/').lower()
        config['unc_credentials'][path_key] = cred_entry
        
        # Persist to file
        from OrganizerDashboard.config_runtime import get_config_path
        config_path = get_config_path()
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
        main.config = config
        return jsonify({'success': True, 'message': 'Credentials saved successfully'})
    
    except Exception as e:
        return jsonify({'error': f'Failed to save credentials: {str(e)}'}), 500


@routes_unc_creds.route('/api/unc/get-credentials/<path:unc_path>', methods=['GET'])
@requires_right('manage_config')
def get_credentials(unc_path):
    """Get saved credentials for a UNC path."""
    try:
        main = sys.modules['__main__']
        config = getattr(main, 'config', {})
        
        path_key = unc_path.replace('\\', '/').lower()
        creds = config.get('unc_credentials', {}).get(path_key, {})
        
        # Don't return password in GET
        safe_creds = {k: v for k, v in creds.items() if k != 'password'}
        safe_creds['has_password'] = 'password' in creds
        
        return jsonify(safe_creds)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
