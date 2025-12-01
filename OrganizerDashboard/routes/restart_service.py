from flask import Blueprint, jsonify, request
from OrganizerDashboard.auth.auth import requires_auth
import sys
import subprocess

routes_restart_service = Blueprint('routes_restart_service', __name__)

SERVICE_NAME = "DownloadsOrganizer"

@routes_restart_service.route("/restart", methods=["POST"])
@requires_auth
def restart_service():
    if sys.platform != "win32":
        return jsonify({"status": "error", "message": "Service control unsupported on this platform"}), 400
    try:
        subprocess.run(["sc", "stop", SERVICE_NAME], capture_output=True, text=True)
        subprocess.run(["sc", "start", SERVICE_NAME], capture_output=True, text=True)
        return jsonify({"status": "success", "message": "Service restarted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Restart failed: {e}"}), 500
