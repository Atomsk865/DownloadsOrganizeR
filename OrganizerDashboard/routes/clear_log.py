from flask import Blueprint, jsonify
from OrganizerDashboard.auth.auth import requires_auth
import os

routes_clear_log = Blueprint('routes_clear_log', __name__)

@routes_clear_log.route("/clear_log/<which>", methods=["POST"])
@requires_auth
def clear_log(which):
    if which not in ("stdout", "stderr"):
        return jsonify({"status": "error", "message": "Invalid log type"}), 400
    from OrganizerDashboard.OrganizerDashboard import STDOUT_LOG, STDERR_LOG
    path = STDOUT_LOG if which == "stdout" else STDERR_LOG
    try:
        with open(path, "w", encoding="utf-8"):
            pass
        return jsonify({"status": "success", "message": f"{which} log cleared"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to clear log: {e}"}), 500
