from flask import Blueprint, jsonify, request
from SortNStoreDashboard.auth.auth import requires_auth
import bcrypt

routes_change_password = Blueprint('routes_change_password', __name__)

@routes_change_password.route("/change_password", methods=["POST"])
@requires_auth
def change_password():
    import SortNStoreDashboard
    from SortNStoreDashboard.config_runtime import get_config, get_dashboard_config, save_config, save_dashboard_config
    ADMIN_USER = SortNStoreDashboard.ADMIN_USER
    config = get_config()
    
    # Only works for basic auth
    if config.get('auth_method', 'basic') != 'basic':
        return jsonify({
            "status": "error", 
            "message": "Password change only available for basic authentication. Current method: " + config.get('auth_method', 'basic')
        }), 400
    
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    new = data.get("new_password") if isinstance(data, dict) else None
    if not new:
        return jsonify({"status": "error", "message": "Missing new_password"}), 400
    try:
        hashed = bcrypt.hashpw(new.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        config['dashboard_user'] = ADMIN_USER
        config['dashboard_pass_hash'] = hashed
        config['password_change_required'] = False
        if 'dashboard_pass' in config:
            del config['dashboard_pass']

        dash_cfg = get_dashboard_config()
        found = False
        for u in dash_cfg.get('users', []):
            if u.get('username') == ADMIN_USER:
                u['password_hash'] = hashed
                found = True
                break
        if not found:
            dash_cfg.setdefault('users', []).append({
                'username': ADMIN_USER,
                'role': 'admin',
                'password_hash': hashed
            })
        dash_cfg['password_change_required'] = False

        save_config()
        save_dashboard_config()

        SortNStoreDashboard.ADMIN_PASS_HASH = hashed.encode('utf-8')

        # Reinitialize auth manager with new password
        from SortNStoreDashboard.auth.auth import initialize_auth_manager
        initialize_auth_manager()

        return jsonify({"status": "success", "message": "Password changed"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to save password: {e}"}), 500
