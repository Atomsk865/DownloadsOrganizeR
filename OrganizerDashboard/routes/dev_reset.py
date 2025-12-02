"""Developer-only reset endpoint for testing first-time setup flow.
WARNING: This endpoint has NO authentication and DELETES all config/state.
Only enable in development environments.
"""

from flask import Blueprint, jsonify
import os
import json
from pathlib import Path

routes_dev_reset = Blueprint('routes_dev_reset', __name__)

@routes_dev_reset.route('/dev/reset-to-setup', methods=['POST'])
def dev_reset_to_setup():
    """
    Nuclear reset: delete all config/state files and force setup wizard.
    NO AUTH REQUIRED - FOR DEVELOPMENT ONLY.
    """
    try:
        # Get root directory
        ROOT = Path(__file__).parent.parent.parent
        
        deleted = []
        errors = []
        
        # 1. Remove organizer_config.json (main config with routes, credentials, etc.)
        organizer_config = ROOT / 'organizer_config.json'
        if organizer_config.exists():
            try:
                organizer_config.unlink()
                deleted.append(str(organizer_config))
            except Exception as e:
                errors.append(f"Failed to delete {organizer_config}: {e}")
        
        # 2. Remove dashboard_config.json (users, roles, layout)
        dashboard_config = ROOT / 'dashboard_config.json'
        if dashboard_config.exists():
            try:
                dashboard_config.unlink()
                deleted.append(str(dashboard_config))
            except Exception as e:
                errors.append(f"Failed to delete {dashboard_config}: {e}")
        
        # 3. Remove all JSON state files in ./config/json/
        config_json_dir = ROOT / 'config' / 'json'
        if config_json_dir.exists():
            for json_file in config_json_dir.glob('*.json'):
                try:
                    json_file.unlink()
                    deleted.append(str(json_file))
                except Exception as e:
                    errors.append(f"Failed to delete {json_file}: {e}")
        
        # 4. Remove logs directory
        logs_dir = ROOT / 'logs'
        if logs_dir.exists():
            import shutil
            try:
                shutil.rmtree(logs_dir)
                deleted.append(str(logs_dir))
            except Exception as e:
                errors.append(f"Failed to remove {logs_dir}: {e}")
        
        # 5. Force-reload runtime config with defaults (no stored state)
        try:
            from OrganizerDashboard.config_runtime import initialize as rt_init
            # Re-init with defaults, no existing files
            default_config = {
                "routes": {
                    "Images": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "svg", "webp", "heic"],
                    "Music": ["mp3", "wav", "flac", "aac", "ogg", "wma", "m4a"],
                    "Videos": ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm"],
                    "Documents": ["pdf", "doc", "docx", "txt", "rtf", "odt", "xls", "xlsx", "ppt", "pptx", "csv"],
                    "Archives": ["zip", "rar", "7z", "tar", "gz", "bz2"],
                    "Executables": ["exe", "msi", "bat", "cmd", "ps1"],
                    "Shortcuts": ["lnk", "url"],
                    "Scripts": ["py", "js", "html", "css", "json", "xml", "sh", "ts", "php"],
                    "Fonts": ["ttf", "otf", "woff", "woff2"],
                    "Logs": ["log"],
                    "Other": []
                },
                "memory_threshold_mb": 200,
                "cpu_threshold_percent": 60,
                "logs_dir": "./logs",
                "auth_method": "basic",
                "auth_fallback_enabled": True,
                "custom_routes": {},
                "watch_folders": [],
                "features": {
                    "virustotal_enabled": False,
                    "duplicates_enabled": True,
                    "reports_enabled": True
                }
            }
            default_dash = {
                "config_version": 1,
                "users": [],
                "setup_completed": False
            }
            rt_init(str(organizer_config), str(dashboard_config), default_config, default_dash)
        except Exception as e:
            errors.append(f"Failed to reinitialize runtime config: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Reset complete. All config/state deleted. Navigate to / to start setup wizard.',
            'deleted_files': deleted,
            'errors': errors
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
