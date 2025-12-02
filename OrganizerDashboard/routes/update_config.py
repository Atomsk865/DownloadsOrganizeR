from flask import Blueprint, request, jsonify
from OrganizerDashboard.auth.auth import requires_right
import json
import os

routes_update_config = Blueprint('routes_update_config', __name__)

CONFIG_FILE = "organizer_config.json"

@routes_update_config.route("/update", methods=["POST"])
@requires_right('manage_config')
def update_config():
    from OrganizerDashboard.helpers.helpers import update_log_paths
    import OrganizerDashboard
    config = OrganizerDashboard.config

    if request.is_json:
        data = request.get_json() or {}
        # thresholds and logs
        mem = str(data.get("memory_threshold_mb", config.get('memory_threshold_mb'))).strip()
        cpu = str(data.get("cpu_threshold_percent", config.get('cpu_threshold_percent'))).strip()
        logs_val = data.get("logs_dir") or config.get('logs_dir')
        logs = logs_val.strip() if isinstance(logs_val, str) else config.get('logs_dir')
        try:
            config['memory_threshold_mb'] = int(mem)
        except Exception:
            return jsonify({"status": "error", "message": "Invalid memory_threshold_mb"}), 400
        try:
            config['cpu_threshold_percent'] = int(cpu)
        except Exception:
            return jsonify({"status": "error", "message": "Invalid cpu_threshold_percent"}), 400
        if logs:
            config['logs_dir'] = logs
        # routes and custom_routes
        routes = data.get('routes')
        if isinstance(routes, dict):
            config['routes'] = routes
        custom_routes = data.get('custom_routes')
        if isinstance(custom_routes, dict):
            config['custom_routes'] = custom_routes
        # network_targets and credentials
        network_targets = data.get('network_targets')
        if isinstance(network_targets, dict):
            config['network_targets'] = network_targets
        credentials = data.get('credentials')
        if isinstance(credentials, dict):
            config['credentials'] = credentials
        # smtp settings
        smtp = data.get('smtp')
        if isinstance(smtp, dict):
            config['smtp'] = smtp
    else:
        # Legacy form support
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
