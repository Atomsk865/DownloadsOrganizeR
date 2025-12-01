from flask import Blueprint, jsonify, request
from OrganizerDashboard.auth.auth import requires_right
import sys
import subprocess

routes_start_service = Blueprint('routes_start_service', __name__)

SERVICE_NAME = "DownloadsOrganizer"

@routes_start_service.route("/start", methods=["POST"])
@requires_right('manage_service')
def start_service():
    if sys.platform != "win32":
        return jsonify({"status": "error", "message": "Service control unsupported on this platform"}), 400
    try:
        subprocess.run(["sc", "start", SERVICE_NAME], capture_output=True, text=True)
        return jsonify({"status": "success", "message": "Service started"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Start failed: {e}"}), 500
