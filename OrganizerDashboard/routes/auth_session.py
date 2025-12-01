from flask import Blueprint, jsonify, request
from OrganizerDashboard.auth.auth import check_auth
import sys

routes_auth_session = Blueprint('routes_auth_session', __name__)

@routes_auth_session.route('/auth/session')
def auth_session():
    """Return current authenticated user's role, rights, and config_version.
    Uses Basic Auth each call; lightweight and cache-friendly on client.
    """
    auth = request.authorization
    if not auth or not check_auth(str(auth.username), str(auth.password)):
        return jsonify({"valid": False}), 401
    main = sys.modules['__main__']
    dashboard_config = getattr(main, 'dashboard_config', {})
    roles = dashboard_config.get('roles', {})
    role_name = 'admin' if auth.username == getattr(main, 'ADMIN_USER', 'admin') else 'viewer'
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
