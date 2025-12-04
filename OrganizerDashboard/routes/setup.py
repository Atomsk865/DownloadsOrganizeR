"""First-time setup wizard routes."""

from flask import Blueprint, render_template, request, jsonify, current_app
import sys
import json
import bcrypt
import os
import subprocess
from pathlib import Path

routes_setup = Blueprint('routes_setup', __name__)

@routes_setup.route('/setup', methods=['GET'])
def setup_page():
    """Render setup page if not completed; otherwise redirect to login."""
    # Use runtime config accessors
    from OrganizerDashboard.config_runtime import get_dashboard_config
    dash_cfg = get_dashboard_config()
    # Always allow accessing the setup page to support reconfiguration
    # Provide initial data (available auth methods based on platform / libraries)
    available_methods = ['basic']
    try:
        from OrganizerDashboard.auth.auth import LDAP_AVAILABLE, WINDOWS_AUTH_AVAILABLE
        if LDAP_AVAILABLE:
            available_methods.append('ldap')
        if WINDOWS_AUTH_AVAILABLE:
            available_methods.append('windows')
    except Exception:
        pass
    # Detect host OS: prefer client User-Agent when available to avoid container/codespace mismatch
    import platform
    sys_platform = platform.system().lower()  # 'windows', 'linux', 'darwin'
    host_os = 'windows' if 'windows' in sys_platform else ('linux' if 'linux' in sys_platform else 'other')
    try:
        ua = (request.headers.get('User-Agent') or '').lower()
        if 'windows nt' in ua or 'windows' in ua:
            host_os = 'windows'
        elif 'linux' in ua:
            host_os = 'linux'
        elif 'mac os' in ua or 'macintosh' in ua or 'darwin' in ua:
            host_os = 'other'
    except Exception:
        pass
    # Recommend default folders based on host OS
    recommended = []
    import os
    default_download = ''
    if host_os == 'windows':
        recommended = [
            'C:/Users/%USERNAME%/Downloads'
        ]
        user = os.getenv('USERNAME') or '%USERNAME%'
        default_download = f'C:/Users/{user}/Downloads'
    elif host_os == 'linux':
        recommended = [
            '/home/%USER%/Downloads'
        ]
        user = os.getenv('USER') or '%USER%'
        default_download = f'/home/{user}/Downloads'
    # Load current organizer config for vt_api_key and features defaults
    try:
        from OrganizerDashboard.config_runtime import get_config
        cfg = get_config()
        vt_api_key = cfg.get('vt_api_key') or cfg.get('virustotal_api_key') or ''
        features = cfg.get('features') or { 'virustotal_enabled': False, 'duplicates_enabled': True, 'reports_enabled': True }
    except Exception:
        vt_api_key = ''
        features = { 'virustotal_enabled': False, 'duplicates_enabled': True, 'reports_enabled': True }

    return render_template(
        'dashboard_setup.html',
        available_methods=available_methods,
        host_os=host_os,
        recommended_watch_folders=recommended,
        default_download_path=default_download,
        vt_api_key=vt_api_key,
        features=features
    )

def _validate_username(name: str) -> str:
    import re
    if not name:
        return 'Username required'
    if len(name) < 3 or len(name) > 32:
        return 'Username length must be 3-32 characters'
    if not re.match(r'^[A-Za-z0-9_-]+$', name):
        return 'Username may only contain letters, numbers, underscore, hyphen'
    return ''

def _validate_password(pw: str) -> str:
    import re
    if len(pw) < 12:
        return 'Password must be at least 12 characters'
    if not re.search(r'[A-Z]', pw):
        return 'Password needs an uppercase letter'
    if not re.search(r'[a-z]', pw):
        return 'Password needs a lowercase letter'
    if not re.search(r'\d', pw):
        return 'Password needs a digit'
    if not re.search(r'[^A-Za-z0-9]', pw):
        return 'Password needs a special character'
    return ''

def _validate_ldap(data: dict) -> str:
    if not data.get('server'):
        return 'LDAP server required'
    if not (data['server'].startswith('ldap://') or data['server'].startswith('ldaps://')):
        return 'LDAP server must start with ldap:// or ldaps://'
    if not data.get('base_dn'):
        return 'LDAP base_dn required'
    templ = data.get('user_dn_template','')
    if templ and '{username}' not in templ:
        return 'LDAP user_dn_template must include {username}'
    return ''

def _validate_windows(data: dict) -> str:
    # Domain optional; allowed_groups must be a list if provided
    if 'allowed_groups' in data:
        groups = data.get('allowed_groups')
        if not isinstance(groups, list):
            return 'Windows allowed_groups must be a list'
        if any((not isinstance(g, str)) or (len(g.strip()) == 0) for g in groups):
            return 'Windows allowed_groups contains empty or non-string entry'
    return ''


@routes_setup.route('/api/setup/organizer-status', methods=['GET'])
def organizer_status():
    """Return whether the organizer process/service is currently running."""
    from OrganizerDashboard.helpers.helpers import find_organizer_proc, service_running

    proc = find_organizer_proc()
    payload = {
        'success': True,
        'running': bool(proc),
        'pid': proc.pid if proc else None
    }

    # On Windows include service_running to distinguish SCM state
    if sys.platform == 'win32':
        try:
            payload['service_running'] = bool(service_running())
        except Exception:
            payload['service_running'] = None

    return jsonify(payload)


@routes_setup.route('/api/setup/start-organizer', methods=['POST'])
def start_organizer_process():
        """Start the organizer service/process without requiring authentication."""
        from OrganizerDashboard.helpers.helpers import find_organizer_proc

        existing = find_organizer_proc()
        if existing:
            return jsonify({
                'success': True,
                'already_running': True,
                'pid': existing.pid
            })

        if sys.platform == 'win32':
            service_name = "DownloadsOrganizer"
            try:
                result = subprocess.run([
                    'sc', 'start', service_name
                ], capture_output=True, text=True, check=True)
                return jsonify({
                    'success': True,
                    'already_running': False,
                    'message': result.stdout.strip()
                })
            except subprocess.CalledProcessError as exc:
                # Fall through to Python process spawn if the Windows service cannot start
                error_msg = exc.stderr or exc.stdout or str(exc)
            except FileNotFoundError:
                error_msg = 'sc.exe not available to start Windows service'
            else:
                error_msg = ''
            if not error_msg:
                return jsonify({'success': False, 'error': 'Unknown error starting Windows service'}), 500
        else:
            error_msg = ''

        # Cross-platform fallback: spawn Organizer.py within the repo directory
        root = Path(__file__).resolve().parents[2]
        organizer_path = root / 'Organizer.py'
        if not organizer_path.exists():
            return jsonify({'success': False, 'error': 'Organizer.py not found'}), 404

        env = os.environ.copy()
        env.setdefault('PYTHONUNBUFFERED', '1')
        try:
            proc = subprocess.Popen(
                [sys.executable, str(organizer_path)],
                cwd=str(root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env
            )
            return jsonify({
                'success': True,
                'already_running': False,
                'pid': proc.pid
            })
        except Exception as exc:
            fallback_error = error_msg or str(exc)
            return jsonify({'success': False, 'error': fallback_error}), 500

@routes_setup.route('/api/setup/initialize', methods=['POST'])
def setup_initialize():
    """Perform initial setup or re-run, writing organizer_config.json and dashboard_config.json."""
    from OrganizerDashboard.config_runtime import get_dashboard_config, get_config, save_config, save_dashboard_config
    dash_cfg = get_dashboard_config()
    # Allow re-running setup to simplify test and recovery flows

    data = request.get_json() or {}
    required = ['admin_username', 'admin_password', 'auth_method']
    missing = [r for r in required if not data.get(r)]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    auth_method = data.get('auth_method')
    if auth_method not in ['basic', 'ldap', 'windows']:
        return jsonify({'error': 'Invalid auth_method'}), 400

    admin_username = data['admin_username'].strip()
    admin_password = data['admin_password']
    fallback_enabled = bool(data.get('auth_fallback_enabled', True))

    # Validation
    u_err = _validate_username(admin_username)
    if u_err:
        return jsonify({'error': u_err}), 400
    p_err = _validate_password(admin_password)
    if p_err:
        return jsonify({'error': p_err}), 400
    if auth_method == 'ldap':
        ldap_err = _validate_ldap(data)
        if ldap_err:
            return jsonify({'error': ldap_err}), 400
    if auth_method == 'windows':
        win_err = _validate_windows(data)
        if win_err:
            return jsonify({'error': win_err}), 400

    # Hash admin password
    try:
        password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except Exception as e:
        return jsonify({'error': f'Failed to hash password: {e}'}), 500

    # Update main.config (organizer_config.json contents)
    config = get_config()
    config['dashboard_user'] = admin_username
    config['dashboard_pass_hash'] = password_hash
    config['auth_method'] = auth_method
    config['auth_fallback_enabled'] = fallback_enabled

    # LDAP specifics
    if auth_method == 'ldap':
        ldap_cfg = config.get('ldap_config', {})
        for field in ['server','base_dn','user_dn_template','use_ssl','bind_dn','bind_password','search_filter','allowed_groups']:
            if field in data:
                ldap_cfg[field] = data[field]
        config['ldap_config'] = ldap_cfg
    # Windows specifics
    if auth_method == 'windows':
        win_cfg = config.get('windows_auth_config', {})
        for field in ['domain','allowed_groups']:
            if field in data:
                win_cfg[field] = data[field]
        config['windows_auth_config'] = win_cfg

    # Persist organizer_config.json
    try:
        save_config()
    except Exception as e:
        return jsonify({'error': f'Failed to save organizer config: {e}'}), 500

    # Prepare dashboard_config
    dash_cfg['users'] = [{ 
        'username': admin_username, 
        'role': 'admin',
        'password_hash': password_hash
    }]
    dash_cfg['setup_completed'] = True
    # Increment config version
    dash_cfg['config_version'] = int(dash_cfg.get('config_version', 1)) + 1
    
    # Ensure roles are defined (preserve existing or use defaults)
    if 'roles' not in dash_cfg:
        dash_cfg['roles'] = {
            "admin": {
                "manage_service": True,
                "manage_config": True,
                "view_metrics": True,
                "view_recent_files": True,
                "modify_layout": True
            },
            "operator": {
                "manage_service": True,
                "manage_config": False,
                "view_metrics": True,
                "view_recent_files": True,
                "modify_layout": False
            },
            "viewer": {
                "manage_service": False,
                "manage_config": False,
                "view_metrics": True,
                "view_recent_files": True,
                "modify_layout": False
            }
        }

    try:
        save_dashboard_config()
    except Exception as e:
        return jsonify({'error': f'Failed to save dashboard config: {e}'}), 500

    # Reinitialize auth manager
    try:
        from OrganizerDashboard.auth.auth import initialize_auth_manager
        initialize_auth_manager()
    except Exception as e:
        return jsonify({'error': f'Auth manager init failed: {e}'}), 500

    # Optionally auto-login the new admin user
    try:
        from flask_login import login_user, UserMixin
        class _SetupUser(UserMixin):
            def __init__(self, username, role='admin'):
                self.id = username
                self.role = role
        # Remember setup auto-login for convenience
        login_user(_SetupUser(admin_username, role='admin'), remember=True)
        return jsonify({'success': True, 'message': 'Setup completed. Logged in as admin.', 'auto_logged_in': True})
    except Exception:
        return jsonify({'success': True, 'message': 'Setup completed. Redirecting to login...', 'auto_logged_in': False})

@routes_setup.route('/api/setup/save', methods=['POST'])
def setup_save():
    """Save additional setup preferences like watch_folders, vt_api_key, features."""
    from OrganizerDashboard.config_runtime import get_config, save_config
    data = request.get_json() or {}
    
    # Extract preferences
    watch_folders = data.get('watch_folders', [])
    vt_api_key = data.get('vt_api_key', '').strip()
    features = data.get('features', {})
    
    # Update organizer_config.json
    config = get_config()
    if watch_folders:
        config['watch_folders'] = watch_folders
    if vt_api_key:
        config['vt_api_key'] = vt_api_key
    if features:
        config['features'] = features
    
    # Persist
    try:
        save_config()
        return jsonify({'success': True, 'message': 'Setup preferences saved'})
    except Exception as e:
        return jsonify({'error': f'Failed to save preferences: {e}'}), 500

@routes_setup.route('/api/setup/reset', methods=['POST'])
def setup_reset():
    """Allow an authenticated admin to re-run initial setup by flipping flag."""
    from OrganizerDashboard.auth.auth import requires_auth, requires_right
    @requires_auth
    @requires_right('manage_config')
    def _reset():
        from OrganizerDashboard.config_runtime import reload_dashboard_config, save_dashboard_config
        dash_cfg = reload_dashboard_config()
        if not dash_cfg.get('setup_completed', False):
            return jsonify({'error': 'Setup already pending'}), 400
        dash_cfg['setup_completed'] = False
        # Persist
        try:
            save_dashboard_config()
        except Exception as e:
            return jsonify({'error': f'Failed to save dashboard config: {e}'}), 500
        return jsonify({'success': True, 'message': 'Setup reset. Redirecting to wizard.'})
    return _reset()
