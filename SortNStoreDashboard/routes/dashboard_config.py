from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from flask_login import current_user
import json
import sys
import bcrypt

routes_dashboard_config = Blueprint('routes_dashboard_config', __name__)

@routes_dashboard_config.route('/config', methods=['GET'])
def config_page():
    """Render dashboard configuration UI (users, roles, layout)."""
    # Check both session auth (Flask-Login) and Basic Auth header
    from SortNStoreDashboard.auth.auth import check_auth
    auth = request.authorization
    is_authenticated = getattr(current_user, 'is_authenticated', False)
    has_basic_auth = auth and check_auth(str(auth.username), str(auth.password))
    
    if not is_authenticated and not has_basic_auth:
        return redirect(url_for('routes_login.login_page'))
    
    main = sys.modules['__main__']
    dash_cfg = getattr(main, 'dashboard_config', {})
    return render_template('dashboard_config.html', roles=dash_cfg.get('roles', {}))

@routes_dashboard_config.route('/api/dashboard/config', methods=['GET'])
def get_dashboard_config():
    from SortNStoreDashboard.auth.auth import requires_auth
    @requires_auth
    def _inner():
        main = sys.modules['__main__']
        dash_cfg = getattr(main, 'dashboard_config', {})
        org_cfg = getattr(main, 'config', {})
        # Do not expose password hashes directly (mask them)
        users = []
        for u in dash_cfg.get('users', []):
            sanitized = {k: v for k, v in u.items() if k != 'password_hash'}
            sanitized['has_password'] = 'password_hash' in u and bool(u['password_hash'])
            users.append(sanitized)
        # Organizer config excerpts for prefilling NAS and SMTP UI
        network_targets = org_cfg.get('network_targets', {})
        credentials = org_cfg.get('credentials', {})
        smtp = org_cfg.get('smtp', {})
        return jsonify({
            'users': users,
            'roles': dash_cfg.get('roles', {}),
            'layout': dash_cfg.get('layout', {}),
            'network_targets': network_targets,
            'credentials': credentials,
            'smtp': smtp
        })
    return _inner()

@routes_dashboard_config.route('/api/dashboard/users', methods=['POST'])
def add_or_update_user():
    from SortNStoreDashboard.auth.auth import requires_right
    @requires_right('manage_config')
    def _inner():
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        role = (data.get('role') or '').strip()
        password = data.get('password')  # optional plain password
        if not username or not role:
            return jsonify({'error': 'username and role required'}), 400
        main = sys.modules['__main__']
        dash_cfg = getattr(main, 'dashboard_config', {})
        roles = dash_cfg.get('roles', {})
        if role not in roles:
            return jsonify({'error': 'invalid role'}), 400
        # Prevent removing or overwriting the primary admin role via this endpoint
        if username == getattr(main, 'ADMIN_USER', 'admin') and role != 'admin':
            return jsonify({'error': 'cannot change primary admin role'}), 400
        users = dash_cfg.get('users', [])
        existing = None
        for u in users:
            if u.get('username') == username:
                existing = u
                break
        if existing is None:
            entry = {'username': username, 'role': role}
            if password:
                pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                entry['password_hash'] = pw_hash
            users.append(entry)
        else:
            existing['role'] = role
            if password and password != '***':
                pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                existing['password_hash'] = pw_hash
        dash_cfg['users'] = users
        _persist_dashboard_config(dash_cfg, main)
        return jsonify({'success': True, 'users': [u['username'] for u in users]})
    return _inner()

@routes_dashboard_config.route('/api/dashboard/users/<username>', methods=['DELETE'])
def delete_user(username: str):
    from SortNStoreDashboard.auth.auth import requires_right
    @requires_right('manage_config')
    def _inner(username=username):
        main = sys.modules['__main__']
        if username == getattr(main, 'ADMIN_USER', 'admin'):
            return jsonify({'error': 'cannot delete primary admin'}), 400
        dash_cfg = getattr(main, 'dashboard_config', {})
        users = dash_cfg.get('users', [])
        new_users = [u for u in users if u.get('username') != username]
        dash_cfg['users'] = new_users
        _persist_dashboard_config(dash_cfg, main)
        return jsonify({'success': True, 'removed': username})
    return _inner()

@routes_dashboard_config.route('/api/dashboard/layout', methods=['POST'])
def update_layout():
    from SortNStoreDashboard.auth.auth import requires_right
    @requires_right('modify_layout')
    def _inner():
        data = request.get_json() or {}
        sections_order = data.get('sections_order')
        hidden_sections = data.get('hidden_sections')
        custom_widgets = data.get('custom_widgets')
        if not isinstance(sections_order, list) or not isinstance(hidden_sections, list):
            return jsonify({'error': 'sections_order and hidden_sections must be lists'}), 400
        main = sys.modules['__main__']
        dash_cfg = getattr(main, 'dashboard_config', {})
        dash_cfg.setdefault('layout', {})
        dash_cfg['layout']['sections_order'] = sections_order
        dash_cfg['layout']['hidden_sections'] = hidden_sections
        if isinstance(custom_widgets, list):
            dash_cfg['layout']['custom_widgets'] = custom_widgets
        _persist_dashboard_config(dash_cfg, main)
        return jsonify({'success': True})
    return _inner()

def _persist_dashboard_config(dash_cfg, main_module):
    try:
        # Increment version
        current_version = dash_cfg.get('config_version', 1)
        dash_cfg['config_version'] = current_version + 1
        with open(getattr(main_module, 'DASHBOARD_CONFIG_FILE', 'dashboard_config.json'), 'w', encoding='utf-8') as f:
            json.dump(dash_cfg, f, indent=4)
        main_module.dashboard_config = dash_cfg
    except Exception:
        pass
