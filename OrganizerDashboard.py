
import os
import sys

# --- Package Name Collision Shim ---
# When running this script directly as OrganizerDashboard.py, Python will prefer the file
# over the package directory of the same name, breaking imports.
# This shim ensures the package directory is treated as a proper package.
_script_dir = os.path.dirname(os.path.abspath(__file__))
_pkg_name = 'OrganizerDashboard'
_pkg_dir = os.path.join(_script_dir, _pkg_name)

# Ensure script directory is in sys.path
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

# Force package resolution by setting up the package module
if os.path.isdir(_pkg_dir):
    if _pkg_name not in sys.modules:
        import types
        pkg = types.ModuleType(_pkg_name)
        pkg.__path__ = [_pkg_dir]
        pkg.__file__ = os.path.join(_pkg_dir, '__init__.py')
        sys.modules[_pkg_name] = pkg

from flask import Flask
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

from OrganizerDashboard.config_runtime import initialize as rt_init, get_config, get_dashboard_config
rt_init(CONFIG_FILE, DASHBOARD_CONFIG_FILE, DEFAULT_CONFIG, {})
config = get_config()

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
    "config_version": 1,
    "users": [
        {"username": ADMIN_USER, "role": "admin"}
    ],
    # Indicates whether the initial setup wizard has been completed.
    # When False, the dashboard will redirect all non-setup routes to /setup.
    "setup_completed": False,
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

from OrganizerDashboard.config_runtime import save_dashboard_config
dashboard_config = get_dashboard_config()
if not os.path.exists(DASHBOARD_CONFIG_FILE):
    try:
        save_dashboard_config()
    except Exception:
        pass

# --- Populate Package Namespace ---
# Routes import OrganizerDashboard and expect these attributes to be available
if _pkg_name in sys.modules:
    pkg_module = sys.modules[_pkg_name]
    pkg_module.config = config
    pkg_module.dashboard_config = dashboard_config
    pkg_module.STDOUT_LOG = STDOUT_LOG
    pkg_module.STDERR_LOG = STDERR_LOG
    pkg_module.LOGS_DIR = LOGS_DIR

# --- Flask App and Blueprint Registration ---
def create_app():
    """Application factory to create and configure the Flask app.
    Ensures auth manager sees current config by setting __main__ to this module.
    """
    # Make this module the __main__ for auth manager expectations
    import sys as _sys
    _sys.modules['__main__'] = sys.modules[__name__]

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
    from OrganizerDashboard.routes.auth_session import routes_auth_session
    from OrganizerDashboard.routes.service_install import routes_service_install
    from OrganizerDashboard.routes.factory_reset import routes_factory_reset
    from OrganizerDashboard.routes.setup import routes_setup

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
    app.register_blueprint(routes_auth_session)
    app.register_blueprint(routes_service_install)
    app.register_blueprint(routes_factory_reset)
    app.register_blueprint(routes_setup)

    # Initialize authentication manager after all globals are set
    from OrganizerDashboard.auth.auth import initialize_auth_manager
    initialize_auth_manager()

    return app

# --- Main Entry Point ---
if __name__ == "__main__":
    print("✅ Dashboard running at http://localhost:5000")
    create_app().run(host="0.0.0.0", port=5000)
