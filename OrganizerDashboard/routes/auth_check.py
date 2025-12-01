from flask import Blueprint, jsonify, request
from OrganizerDashboard.auth.auth import check_auth
import sys

routes_auth_check = Blueprint('routes_auth_check', __name__)

@routes_auth_check.route('/auth_check')
def auth_check():
    """Lightweight endpoint to validate Basic credentials sent in the Authorization header."""
    auth = request.authorization
    if not auth:
        return jsonify({"valid": False, "message": "No credentials provided"}), 401
    if check_auth(str(auth.username), str(auth.password)):
        # Resolve role & rights
        main = sys.modules['__main__']
        dashboard_config = getattr(main, 'dashboard_config', {})
        roles = dashboard_config.get('roles', {})
        role_name = 'admin' if auth.username == getattr(main, 'ADMIN_USER', 'admin') else 'viewer'
        for u in dashboard_config.get('users', []):
            if u.get('username') == auth.username:
                role_name = u.get('role') or role_name
                break
        rights = roles.get(role_name, {})
        return jsonify({"valid": True, "username": auth.username, "role": role_name, "rights": rights}), 200
    return jsonify({"valid": False, "message": "Invalid credentials"}), 401
