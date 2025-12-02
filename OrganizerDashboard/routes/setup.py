"""First-time setup wizard routes."""

from flask import Blueprint, render_template, request, jsonify
import sys
import json
import bcrypt

routes_setup = Blueprint('routes_setup', __name__)

@routes_setup.route('/setup', methods=['GET'])
def setup_page():
    """Render setup page if not completed; otherwise redirect to login."""
    # Use runtime config accessors
    from OrganizerDashboard.config_runtime import get_dashboard_config
    dash_cfg = get_dashboard_config()
    if dash_cfg.get('setup_completed', False):
        from flask import redirect
        return redirect('/login')
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
    return render_template('dashboard_setup.html', available_methods=available_methods)

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

@routes_setup.route('/api/setup/initialize', methods=['POST'])
def setup_initialize():
    """Perform initial setup or re-run, writing organizer_config.json and dashboard_config.json."""
    from OrganizerDashboard.config_runtime import get_dashboard_config, get_config, save_config, save_dashboard_config
    dash_cfg = get_dashboard_config()
    if dash_cfg.get('setup_completed', False):
        return jsonify({'error': 'Setup already completed'}), 400

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

    return jsonify({'success': True, 'message': 'Setup completed. Redirecting to login...'})

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
