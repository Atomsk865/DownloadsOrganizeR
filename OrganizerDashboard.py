
from flask import Flask
import os
import json

"""OrganizerDashboard

Flask-based dashboard to monitor and control the DownloadsOrganizer service.
This module exposes JSON endpoints used by the UI (AJAX) and renders a
single-page dashboard with controls, logs, and configuration.
"""

# --- Service and Config ---
SERVICE_NAME = "DownloadsOrganizer"
CONFIG_FILE = "organizer_config.json"
DASHBOARD_CONFIG_FILE = "dashboard_config.json"

DEFAULT_CONFIG = {
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
    "logs_dir": r"C:\Scripts\service-logs",
    "auth_method": "basic",
    "auth_fallback_enabled": True,
    "ldap_config": {
        "server": "",
        "base_dn": "",
        "user_dn_template": "uid={username},{base_dn}",
        "use_ssl": True,
        "bind_dn": "",
        "bind_password": "",
        "search_filter": "(uid={username})",
        "allowed_groups": []
    },
    "windows_auth_config": {
        "domain": "",
        "allowed_groups": []
    }
}

config = DEFAULT_CONFIG.copy()
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            config.update(loaded)
    except Exception:
        pass

# --- Authentication Globals ---
ADMIN_USER = os.environ.get("DASHBOARD_USER", "admin")
ADMIN_PASS = os.environ.get("DASHBOARD_PASS", "change_this_password")
ADMIN_PASS_HASH = None

# If credentials are stored in the config file, prefer them
if isinstance(config, dict):
    dashboard_user = config.get("dashboard_user")
    dashboard_pass = config.get("dashboard_pass")
    dashboard_pass_hash = config.get("dashboard_pass_hash")
    if dashboard_user:
        ADMIN_USER = dashboard_user
    if dashboard_pass_hash:
        ADMIN_PASS_HASH = dashboard_pass_hash.encode('utf-8')
    elif dashboard_pass:
        ADMIN_PASS = dashboard_pass

# --- Log Paths ---
def update_log_paths():
    global LOGS_DIR, STDOUT_LOG, STDERR_LOG
    LOGS_DIR = config.get("logs_dir", DEFAULT_CONFIG["logs_dir"])
    STDOUT_LOG = os.path.join(LOGS_DIR, "organizer_stdout.log")
    STDERR_LOG = os.path.join(LOGS_DIR, "organizer_stderr.log")

update_log_paths()

# --- Dashboard (Users/Roles/Layout) Config ---
DASHBOARD_CONFIG_DEFAULT = {
    "users": [
        {"username": ADMIN_USER, "role": "admin"}
    ],
    "roles": {
        "admin": {
            "manage_service": True,
            "manage_config": True,
            "view_metrics": True,
            "view_recent_files": True,
            "modify_layout": True
        },
        "operator": {
            "manage_service": True,
            "manage_config": False,
            "view_metrics": True,
            "view_recent_files": True,
            "modify_layout": False
        },
        "viewer": {
            "manage_service": False,
            "manage_config": False,
            "view_metrics": True,
            "view_recent_files": True,
            "modify_layout": False
        }
    },
    "layout": {
        "sections_order": [
            "System Information",
            "Service Status & Resource Usage",
            "Task Manager (Top 5 by CPU)",
            "Drive Space",
            "Settings",
            "Recent File Movements",
            "File Categories",
            "Logs (real-time)"
        ],
        "hidden_sections": []
    }
}

dashboard_config = DASHBOARD_CONFIG_DEFAULT.copy()
if os.path.exists(DASHBOARD_CONFIG_FILE):
    try:
        with open(DASHBOARD_CONFIG_FILE, "r", encoding="utf-8") as f:
            loaded_dash = json.load(f)
        if isinstance(loaded_dash, dict):
            # Merge with defaults (shallow merge; roles preserved)
            for k, v in DASHBOARD_CONFIG_DEFAULT.items():
                if k not in loaded_dash:
                    loaded_dash[k] = v
            dashboard_config = loaded_dash
    except Exception:
        pass
else:
    # Persist initial default
    try:
        with open(DASHBOARD_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(dashboard_config, f, indent=4)
    except Exception:
        pass

# --- Flask App and Blueprint Registration ---
app = Flask(__name__, template_folder='dash')

# Import and register all blueprints from routes
from OrganizerDashboard.routes.dashboard import routes_dashboard
from OrganizerDashboard.routes.update_config import routes_update_config
from OrganizerDashboard.routes.metrics import routes_metrics
from OrganizerDashboard.routes.service_name import routes_service_name
from OrganizerDashboard.routes.auth_check import routes_auth_check
from OrganizerDashboard.routes.restart_service import routes_restart_service
from OrganizerDashboard.routes.stop_service import routes_stop_service
from OrganizerDashboard.routes.start_service import routes_start_service
from OrganizerDashboard.routes.tail import routes_tail
from OrganizerDashboard.routes.stream import routes_stream
from OrganizerDashboard.routes.clear_log import routes_clear_log
from OrganizerDashboard.routes.change_password import routes_change_password
from OrganizerDashboard.routes.drives import routes_drives
from OrganizerDashboard.routes.network import routes_network
from OrganizerDashboard.routes.tasks import routes_tasks
from OrganizerDashboard.routes.hardware import routes_hardware
from OrganizerDashboard.routes.api_recent_files import routes_api_recent_files
from OrganizerDashboard.routes.api_open_file import routes_api_open_file
from OrganizerDashboard.routes.auth_settings import routes_auth_settings
from OrganizerDashboard.routes.dashboard_config import routes_dashboard_config

app.register_blueprint(routes_dashboard)
app.register_blueprint(routes_update_config)
app.register_blueprint(routes_metrics)
app.register_blueprint(routes_service_name)
app.register_blueprint(routes_auth_check)
app.register_blueprint(routes_restart_service)
app.register_blueprint(routes_stop_service)
app.register_blueprint(routes_start_service)
app.register_blueprint(routes_tail)
app.register_blueprint(routes_stream)
app.register_blueprint(routes_clear_log)
app.register_blueprint(routes_change_password)
app.register_blueprint(routes_drives)
app.register_blueprint(routes_network)
app.register_blueprint(routes_tasks)
app.register_blueprint(routes_hardware)
app.register_blueprint(routes_api_recent_files)
app.register_blueprint(routes_api_open_file)
app.register_blueprint(routes_auth_settings)
app.register_blueprint(routes_dashboard_config)

# Initialize authentication manager after all globals are set
from OrganizerDashboard.auth.auth import initialize_auth_manager
initialize_auth_manager()

# --- Main Entry Point ---
if __name__ == "__main__":
    print("✅ Dashboard running at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)
