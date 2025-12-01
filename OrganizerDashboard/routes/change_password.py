from flask import Blueprint, jsonify, request
from OrganizerDashboard.auth.auth import requires_auth
import bcrypt
import json

routes_change_password = Blueprint('routes_change_password', __name__)

CONFIG_FILE = "organizer_config.json"

@routes_change_password.route("/change_password", methods=["POST"])
@requires_auth
def change_password():
    import OrganizerDashboard
    ADMIN_USER = OrganizerDashboard.ADMIN_USER
    config = OrganizerDashboard.config
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
        if 'dashboard_pass' in config:
            del config['dashboard_pass']
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        OrganizerDashboard.ADMIN_PASS_HASH = hashed.encode('utf-8')
        return jsonify({"status": "success", "message": "Password changed"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to save password: {e}"}), 500
