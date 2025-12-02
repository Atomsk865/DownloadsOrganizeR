from flask import Blueprint, jsonify, request
from OrganizerDashboard.auth.auth import check_auth
from flask_login import current_user
from OrganizerDashboard.config_runtime import get_dashboard_config

routes_auth_check = Blueprint('routes_auth_check', __name__)

@routes_auth_check.route('/auth_check')
def auth_check():
    """Lightweight endpoint to validate Basic credentials sent in the Authorization header."""
    auth = request.authorization
    # Prefer session if available
    if (not auth) and current_user.is_authenticated:
        username = current_user.get_id()
        # Resolve role & rights from dashboard_config
        dashboard_config = get_dashboard_config()
        roles = dashboard_config.get('roles', {})
        role_name = None
        for u in dashboard_config.get('users', []):
            if u.get('username') == username:
                role_name = u.get('role') or 'viewer'
                break
        rights = roles.get(role_name or 'viewer', {})
        return jsonify({"valid": True, "username": username, "role": role_name or 'viewer', "rights": rights}), 200
    if auth and check_auth(str(auth.username), str(auth.password)):
        # Resolve role & rights
        dashboard_config = get_dashboard_config()
        from OrganizerDashboard.config_runtime import get_config
        roles = dashboard_config.get('roles', {})
        admin_user = get_config().get('dashboard_user', 'admin')
        role_name = 'admin' if auth.username == admin_user else 'viewer'
        for u in dashboard_config.get('users', []):
            if u.get('username') == auth.username:
                role_name = u.get('role') or role_name
                break
        rights = roles.get(role_name, {})
        return jsonify({"valid": True, "username": auth.username, "role": role_name, "rights": rights}), 200
    return jsonify({"valid": False, "message": "Invalid credentials"}), 401
