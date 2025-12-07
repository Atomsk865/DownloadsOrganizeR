from flask import Blueprint, jsonify, request
from OrganizerDashboard.auth.auth import requires_auth
import subprocess
import os
import shutil
import json
from pathlib import Path
from datetime import datetime

routes_system_update = Blueprint('routes_system_update', __name__)

def get_install_paths():
    """Get installation directories from marker file or defaults."""
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    marker_file = os.path.join(script_dir, ".install_path")
    
    install_dir = script_dir
    data_dir = script_dir
    config_dir = script_dir
    
    if os.path.exists(marker_file):
        try:
            with open(marker_file, 'r') as f:
                content = f.read().strip()
                try:
                    paths = json.loads(content)
                    install_dir = paths.get('install_dir', script_dir)
                    data_dir = paths.get('data_dir', install_dir)
                    config_dir = paths.get('config_dir', data_dir)
                except (json.JSONDecodeError, ValueError):
                    pass
        except Exception:
            pass
    
    return install_dir, data_dir, config_dir

def backup_config_files(config_dir, install_dir):
    """Backup all config JSON files to InstallRoot/Backups/Configs/ with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(install_dir, "Backups", "Configs", timestamp)
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Config files to backup
        config_files = [
            os.path.join(config_dir, "organizer_config.json"),
            os.path.join(config_dir, "dashboard_config.json"),
            os.path.join(install_dir, "dashboard_branding.json"),
            os.path.join(install_dir, "sortnstore_config.json"),
        ]
        
        backed_up = []
        for config_file in config_files:
            if os.path.exists(config_file):
                filename = os.path.basename(config_file)
                backup_path = os.path.join(backup_dir, filename)
                shutil.copy2(config_file, backup_path)
                backed_up.append(filename)
        
        return {"success": True, "backup_dir": backup_dir, "files": backed_up, "timestamp": timestamp}
    except Exception as e:
        return {"success": False, "error": str(e)}

@routes_system_update.route("/api/system/update", methods=["POST"])
@requires_auth
def system_update():
    """Pull latest updates from GitHub main branch and restart service."""
    install_dir, data_dir, config_dir = get_install_paths()
    
    # Step 1: Backup configs
    backup_result = backup_config_files(config_dir, install_dir)
    if not backup_result["success"]:
        return jsonify({
            "success": False,
            "error": f"Config backup failed: {backup_result['error']}"
        }), 500
    
    # Step 2: Git pull
    try:
        os.chdir(install_dir)
        
        # Check if it's a git repository
        if not os.path.exists(os.path.join(install_dir, ".git")):
            return jsonify({
                "success": False,
                "error": "Not a git repository. Please reinstall using the installer."
            }), 400
        
        # Fetch and pull latest from main
        result = subprocess.run(
            ["git", "fetch", "origin", "main"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return jsonify({
                "success": False,
                "error": f"Git fetch failed: {result.stderr}"
            }), 500
        
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return jsonify({
                "success": False,
                "error": f"Git pull failed: {result.stderr}"
            }), 500
        
        # Step 3: Restart service (Windows NSSM)
        service_restart_success = False
        try:
            restart_result = subprocess.run(
                ["nssm", "restart", "DownloadsOrganizer"],
                capture_output=True,
                text=True,
                timeout=10
            )
            service_restart_success = restart_result.returncode == 0
        except Exception as e:
            service_restart_success = False
        
        return jsonify({
            "success": True,
            "message": "Update completed successfully",
            "backup": {
                "timestamp": backup_result["timestamp"],
                "location": backup_result["backup_dir"],
                "files": backup_result["files"]
            },
            "git_output": result.stdout,
            "service_restarted": service_restart_success,
            "notice": "⚠️ Config files may need updates for new features. Use Config Import to restore settings if needed."
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "Git operation timed out"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@routes_system_update.route("/api/system/backups", methods=["GET"])
@requires_auth
def list_backups():
    """List all available config backups."""
    install_dir, _, _ = get_install_paths()
    backup_base = os.path.join(install_dir, "Backups", "Configs")
    
    if not os.path.exists(backup_base):
        return jsonify({"backups": []})
    
    backups = []
    try:
        for timestamp_dir in sorted(os.listdir(backup_base), reverse=True):
            dir_path = os.path.join(backup_base, timestamp_dir)
            if os.path.isdir(dir_path):
                files = [f for f in os.listdir(dir_path) if f.endswith('.json')]
                if files:
                    backups.append({
                        "timestamp": timestamp_dir,
                        "path": dir_path,
                        "files": files,
                        "date": datetime.strptime(timestamp_dir, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
                    })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"backups": backups})

@routes_system_update.route("/api/system/import-config", methods=["POST"])
@requires_auth
def import_config():
    """Import config from a backup timestamp."""
    data = request.get_json()
    timestamp = data.get("timestamp")
    config_file = data.get("config_file")  # e.g., "organizer_config.json"
    
    if not timestamp or not config_file:
        return jsonify({"success": False, "error": "Missing timestamp or config_file"}), 400
    
    install_dir, data_dir, config_dir = get_install_paths()
    backup_path = os.path.join(install_dir, "Backups", "Configs", timestamp, config_file)
    
    if not os.path.exists(backup_path):
        return jsonify({"success": False, "error": "Backup file not found"}), 404
    
    # Determine target path
    if config_file in ["organizer_config.json", "dashboard_config.json"]:
        target_path = os.path.join(config_dir, config_file)
    else:
        target_path = os.path.join(install_dir, config_file)
    
    try:
        # Create backup of current config before overwriting
        if os.path.exists(target_path):
            current_backup = target_path + ".before_import"
            shutil.copy2(target_path, current_backup)
        
        # Import the backed up config
        shutil.copy2(backup_path, target_path)
        
        return jsonify({
            "success": True,
            "message": f"{config_file} imported successfully",
            "notice": "Service restart recommended for changes to take effect"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
