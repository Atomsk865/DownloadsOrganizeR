from flask import Blueprint, jsonify, request
from SortNStoreDashboard.auth.auth import requires_right
import bcrypt

routes_admin_tools = Blueprint('routes_admin_tools', __name__)

@routes_admin_tools.route('/api/admin/repair_auth', methods=['POST'])
@requires_right('manage_config')
def repair_auth():
    """Align organizer and dashboard configs for admin credentials.
    Body: { username?: str, password?: str, force_basic?: bool }
    """
    from SortNStoreDashboard.config_runtime import get_config, get_dashboard_config, save_config, save_dashboard_config
    data = request.get_json(silent=True) or {}
    target_user = (data.get('username') or get_config().get('dashboard_user') or 'admin').strip()
    password = data.get('password')
    cfg = get_config()
    dash = get_dashboard_config()

    if not password:
        # Use existing hash or default
        existing_hash = cfg.get('dashboard_pass_hash')
        if not existing_hash:
            # Create a temporary hash for default (blank) password
            default_pw = ''
            existing_hash = bcrypt.hashpw(default_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cfg['dashboard_pass_hash'] = existing_hash
        cfg['password_change_required'] = True
    else:
        cfg['dashboard_pass_hash'] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cfg['password_change_required'] = False

    cfg['dashboard_user'] = target_user

    # Optionally force basic auth to guarantee admin access
    if bool(data.get('force_basic', True)):
        cfg['auth_method'] = 'basic'
        cfg['auth_fallback_enabled'] = True

    # Upsert user in dashboard_config with password_hash
    found = False
    for u in dash.get('users', []):
        if u.get('username') == target_user:
            u['role'] = u.get('role') or 'admin'
            u['password_hash'] = cfg['dashboard_pass_hash']
            found = True
            break
    if not found:
        dash.setdefault('users', []).append({
            'username': target_user,
            'role': 'admin',
            'password_hash': cfg['dashboard_pass_hash']
        })

    dash['password_change_required'] = cfg.get('password_change_required', False)

    dash['setup_completed'] = True

    try:
        save_config()
        save_dashboard_config()
        # Reinitialize auth manager
        from SortNStoreDashboard.auth.auth import initialize_auth_manager
        initialize_auth_manager()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    return jsonify({'success': True, 'username': target_user})

@routes_admin_tools.route('/api/admin/auth_state', methods=['GET'])
@requires_right('manage_config')
def auth_state():
    """Return sanitized auth-related state for diagnostics."""
    from SortNStoreDashboard.config_runtime import get_config, get_dashboard_config
    cfg = get_config()
    dash = get_dashboard_config()
    return jsonify({
        'dashboard_user': cfg.get('dashboard_user'),
        'auth_method': cfg.get('auth_method'),
        'auth_fallback_enabled': cfg.get('auth_fallback_enabled'),
        'users': [
            { 'username': u.get('username'), 'role': u.get('role'), 'has_hash': bool(u.get('password_hash')) }
            for u in dash.get('users', [])
        ],
        'setup_completed': dash.get('setup_completed', False)
    })
