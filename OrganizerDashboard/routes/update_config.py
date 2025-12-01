from flask import Blueprint, request, jsonify
from OrganizerDashboard.auth.auth import requires_auth
import json
import os

routes_update_config = Blueprint('routes_update_config', __name__)

CONFIG_FILE = "organizer_config.json"

@routes_update_config.route("/update", methods=["POST"])
@requires_auth
def update_config():
    from OrganizerDashboard.helpers.helpers import update_log_paths
    from OrganizerDashboard.OrganizerDashboard import config
    new_routes = {}
    i = 1
    while True:
        folder_key = f"folder_{i}"
        exts_key = f"exts_{i}"
        if folder_key in request.form and exts_key in request.form:
            folder = request.form[folder_key].strip()
            exts = [e.strip() for e in request.form[exts_key].split(",") if e.strip()]
            if folder:
                new_routes[folder] = exts
            i += 1
        else:
            break
    new_folder = request.form.get("folder_new", "").strip()
    new_exts = request.form.get("exts_new", "").strip()
    if new_folder:
        new_routes[new_folder] = [e.strip() for e in new_exts.split(",") if e.strip()]
    mem = request.form.get("memory_threshold", str(config['memory_threshold_mb'])).strip()
    cpu = request.form.get("cpu_threshold", str(config['cpu_threshold_percent'])).strip()
    logs = request.form.get("logs_dir", config['logs_dir']).strip()
    try:
        config['memory_threshold_mb'] = int(mem)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid memory threshold value"}), 400
    try:
        config['cpu_threshold_percent'] = int(cpu)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid CPU threshold value"}), 400
    if logs:
        config['logs_dir'] = logs
    config['routes'] = new_routes
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    update_log_paths()
    return jsonify({"status": "success", "message": "Configuration saved"}), 200
