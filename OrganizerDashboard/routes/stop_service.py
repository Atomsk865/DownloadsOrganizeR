from flask import Blueprint, jsonify, request
from OrganizerDashboard.auth.auth import requires_auth
import sys
import subprocess

routes_stop_service = Blueprint('routes_stop_service', __name__)

SERVICE_NAME = "DownloadsOrganizer"

@routes_stop_service.route("/stop", methods=["POST"])
@requires_auth
def stop_service():
    if sys.platform != "win32":
        return jsonify({"status": "error", "message": "Service control unsupported on this platform"}), 400
    try:
        subprocess.run(["sc", "stop", SERVICE_NAME], capture_output=True, text=True)
        return jsonify({"status": "success", "message": "Service stopped"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Stop failed: {e}"}), 500
