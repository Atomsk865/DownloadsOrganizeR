from flask import Blueprint, jsonify, request
from OrganizerDashboard.auth.auth import check_auth
from OrganizerDashboard.config_runtime import get_dashboard_config, get_config
from flask_login import current_user

routes_auth_session = Blueprint('routes_auth_session', __name__)

@routes_auth_session.route('/auth/session')
def auth_session():
    """Return current authenticated user's role, rights, and config_version.
    Uses Basic Auth each call; lightweight and cache-friendly on client.
    """
    auth = request.authorization
    if (not auth) and current_user.is_authenticated:
        username = current_user.get_id()
        dashboard_config = get_dashboard_config()
        roles = dashboard_config.get('roles', {})
        role_name = None
        for u in dashboard_config.get('users', []):
            if u.get('username') == username:
                role_name = u.get('role') or 'viewer'
                break
        rights = roles.get(role_name or 'viewer', {})
        return jsonify({
            "valid": True,
            "username": username,
            "role": role_name or 'viewer',
            "rights": rights,
            "config_version": dashboard_config.get('config_version', 1)
        })
    if not auth or not check_auth(str(auth.username), str(auth.password)):
        return jsonify({"valid": False}), 401
    dashboard_config = get_dashboard_config()
    roles = dashboard_config.get('roles', {})
    admin_user = get_config().get('dashboard_user', 'admin')
    role_name = 'admin' if auth.username == admin_user else 'viewer'
    for u in dashboard_config.get('users', []):
        if u.get('username') == auth.username:
            role_name = u.get('role') or role_name
            break
    rights = roles.get(role_name, {})
    return jsonify({
        "valid": True,
        "username": auth.username,
        "role": role_name,
        "rights": rights,
        "config_version": dashboard_config.get('config_version', 1)
    })
