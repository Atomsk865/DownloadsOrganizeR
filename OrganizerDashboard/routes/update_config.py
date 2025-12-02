from flask import Blueprint, request, jsonify
from OrganizerDashboard.auth.auth import requires_right
import json
import os

routes_update_config = Blueprint('routes_update_config', __name__)

# Try to save to the same locations the Organizer checks
CONFIG_FILES = ["organizer_config.json", "C:/Scripts/organizer_config.json"]

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
        watch_folder_val = data.get("watch_folder")
        watch_folder = watch_folder_val.strip() if isinstance(watch_folder_val, str) else None
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
        if watch_folder is not None:
            config['watch_folder'] = watch_folder
        # routes and custom_routes
        routes = data.get('routes')
        if isinstance(routes, dict):
            config['routes'] = routes
        custom_routes = data.get('custom_routes')
        if isinstance(custom_routes, dict):
            config['custom_routes'] = custom_routes
        tag_routes = data.get('tag_routes')
        if isinstance(tag_routes, dict):
            config['tag_routes'] = tag_routes
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
        # VirusTotal API key
        vt_api_key = data.get('vt_api_key')
        if isinstance(vt_api_key, str):
            config['vt_api_key'] = vt_api_key.strip()
        # Feature toggles
        features = data.get('features')
        if isinstance(features, dict):
            feats = config.get('features') or {}
            feats['virustotal_enabled'] = bool(features.get('virustotal_enabled', feats.get('virustotal_enabled', True)))
            feats['duplicates_enabled'] = bool(features.get('duplicates_enabled', feats.get('duplicates_enabled', True)))
            feats['reports_enabled'] = bool(features.get('reports_enabled', feats.get('reports_enabled', True)))
            config['features'] = feats
    else:
        # Legacy form support (including feature toggles and vt_api_key)
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
        mem = (request.form.get("memory_threshold", str(config.get('memory_threshold_mb', '')) ) or "").strip()
        cpu = (request.form.get("cpu_threshold", str(config.get('cpu_threshold_percent', '')) ) or "").strip()
        logs = (request.form.get("logs_dir", config.get('logs_dir', '')) or "").strip()
        watch_folder = (request.form.get("watch_folder", config.get('watch_folder', '')) or "").strip()
        try:
            config['memory_threshold_mb'] = int(mem)
        except ValueError:
            pass
        try:
            config['cpu_threshold_percent'] = int(cpu)
        except ValueError:
            pass
        if logs:
            config['logs_dir'] = logs
        if watch_folder:
            config['watch_folder'] = watch_folder
        config['routes'] = new_routes

        # vt_api_key and feature toggles (checkboxes submit 'on' or values)
        vt_api_key = request.form.get('vt_api_key', '').strip()
        if vt_api_key:
            config['vt_api_key'] = vt_api_key
        feats = config.get('features') or {}
        # Interpret truthy presence for checkboxes
        def _truthy(val):
            if val is None:
                return False
            return str(val).lower() in ('1', 'true', 'on', 'yes')
        virustotal_enabled = request.form.get('virustotal_enabled')
        duplicates_enabled = request.form.get('duplicates_enabled')
        reports_enabled = request.form.get('reports_enabled')
        if virustotal_enabled is not None:
            feats['virustotal_enabled'] = _truthy(virustotal_enabled)
        if duplicates_enabled is not None:
            feats['duplicates_enabled'] = _truthy(duplicates_enabled)
        if reports_enabled is not None:
            feats['reports_enabled'] = _truthy(reports_enabled)
        config['features'] = feats

    # Save to all config file locations to ensure service picks it up
    saved_count = 0
    errors = []
    for config_path in CONFIG_FILES:
        try:
            # Create directory if it doesn't exist
            config_dir = os.path.dirname(config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            saved_count += 1
        except Exception as e:
            errors.append(f"{config_path}: {str(e)}")
    
    update_log_paths()
    
    if saved_count > 0:
        msg = f"Configuration saved to {saved_count} location(s). Restart the Organizer service for changes to take effect."
        if errors:
            msg += f" Some locations failed: {'; '.join(errors)}"
        return jsonify({"status": "success", "message": msg}), 200
    else:
        return jsonify({"status": "error", "message": f"Failed to save config: {'; '.join(errors)}"}), 500
