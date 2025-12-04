
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
from flask_login import LoginManager, UserMixin
from flask_wtf.csrf import CSRFProtect
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
    },
    # Per-extension custom destinations (absolute folder paths)
    "custom_routes": {}
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
            "modify_layout": True,
            "test_smtp": True,
            "test_nas": True,
            "manage_network_targets": True,
            "manage_credentials": True,
            "send_reports": True
        },
        "operator": {
            "manage_service": True,
            "manage_config": False,
            "view_metrics": True,
            "view_recent_files": True,
            "modify_layout": False,
            "test_smtp": False,
            "test_nas": False,
            "manage_network_targets": False,
            "manage_credentials": False,
            "send_reports": False
        },
        "viewer": {
            "manage_service": False,
            "manage_config": False,
            "view_metrics": True,
            "view_recent_files": True,
            "modify_layout": False,
            "test_smtp": False,
            "test_nas": False,
            "manage_network_targets": False,
            "manage_credentials": False,
            "send_reports": False
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
    # Use setattr to avoid static analysis warnings on dynamic module attributes
    try:
        setattr(pkg_module, 'config', config)
        setattr(pkg_module, 'dashboard_config', dashboard_config)
        setattr(pkg_module, 'STDOUT_LOG', STDOUT_LOG)
        setattr(pkg_module, 'STDERR_LOG', STDERR_LOG)
        setattr(pkg_module, 'LOGS_DIR', LOGS_DIR)
    except Exception:
        pass

# --- Flask App and Blueprint Registration ---
def create_app():
    """Application factory to create and configure the Flask app.
    Ensures auth manager sees current config by setting __main__ to this module.
    """
    # Make this module the __main__ for auth manager expectations
    import sys as _sys
    # Safely set __main__ for auth manager expectations, even when dynamically imported
    try:
        _sys.modules['__main__'] = sys.modules[__name__]
    except KeyError:
        _sys.modules['__main__'] = _sys.modules.get('__main__', sys.modules[__name__])

    from flask_caching import Cache
    from flask_compress import Compress
    
    app = Flask(__name__, template_folder='dash')
    # Basic secret key for session cookies; can be overridden via env
    app.secret_key = os.environ.get('DASHBOARD_SECRET_KEY', 'downloads_organizer_secret')
    
    # Flask-Caching setup (simple in-memory cache)
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 5  # 5 seconds default
    cache = Cache(app)
    
    # Make cache available to blueprints
    from OrganizerDashboard.cache import init_cache
    init_cache(cache)
    
    # Flask-Compress setup (gzip/brotli compression for responses)
    app.config['COMPRESS_MIMETYPES'] = [
        'text/html', 'text/css', 'text/xml', 'text/plain',
        'application/json', 'application/javascript',
        'text/javascript', 'application/x-javascript',
        'image/svg+xml'
    ]
    app.config['COMPRESS_LEVEL'] = 6  # Compression level (1-9)
    app.config['COMPRESS_MIN_SIZE'] = 500  # Only compress > 500 bytes
    Compress(app)
    
    # CSRF Protection
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    # Secure session cookie settings
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    # Session persistence: allow long-lived sessions with remember cookies
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 14 * 24 * 60 * 60  # 14 days
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # No token expiry for long sessions

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    # Assign login_view via Any to avoid static analysis issues
    from typing import Any as _Any
    _lm_any: _Any = login_manager
    _lm_any.login_view = 'routes_login.login_page'

    class User(UserMixin):
        def __init__(self, username, role='viewer'):
            self.id = username
            self.role = role

    @login_manager.user_loader
    def load_user(user_id):
        try:
            from OrganizerDashboard.config_runtime import get_dashboard_config
            dash_cfg = get_dashboard_config()
            role = 'viewer'
            for u in dash_cfg.get('users', []):
                if u.get('username') == user_id:
                    role = u.get('role') or 'viewer'
                    break
            return User(user_id, role)
        except Exception:
            return User(user_id)

    # Asset versioning for cache busting
    @app.context_processor
    def inject_asset_version():
        """Inject asset version into all templates for cache busting"""
        import time
        # Use current timestamp for dev, use a fixed version in production
        version = os.environ.get('ASSET_VERSION', str(int(time.time())))
        return {'asset_version': version, 'cache': cache}

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
    try:
        from OrganizerDashboard.routes.api_recent_files import routes_api_recent_files
        print("✓ api_recent_files imported successfully")
    except Exception as e:
        print(f"✗ Failed to import api_recent_files: {e}")
        import traceback
        traceback.print_exc()
        routes_api_recent_files = None
    from OrganizerDashboard.routes.api_open_file import routes_api_open_file
    from OrganizerDashboard.routes.auth_settings import routes_auth_settings
    from OrganizerDashboard.routes.dashboard_config import routes_dashboard_config
    from OrganizerDashboard.routes.auth_session import routes_auth_session
    from OrganizerDashboard.routes.sse_streams import bp as sse_streams_bp
    from OrganizerDashboard.routes.service_install import routes_service_install
    from OrganizerDashboard.routes.factory_reset import routes_factory_reset
    from OrganizerDashboard.routes.setup import routes_setup
    from OrganizerDashboard.routes.admin_tools import routes_admin_tools
    from OrganizerDashboard.routes.login import routes_login
    from OrganizerDashboard.routes.csrf_token import routes_csrf
    from OrganizerDashboard.routes.user_links import routes_user_links
    from OrganizerDashboard.routes.reports import reports_bp
    from OrganizerDashboard.routes.branding import routes_branding
    from OrganizerDashboard.routes.statistics import routes_statistics
    from OrganizerDashboard.routes.notifications import routes_notifications
    from OrganizerDashboard.routes.changelog import routes_changelog
    from OrganizerDashboard.routes.config_backup import routes_config_backup
    from OrganizerDashboard.routes.watch_folders import routes_watch_folders
    from OrganizerDashboard.routes.duplicates import routes_duplicates
    from OrganizerDashboard.routes.docs import routes_docs
    from OrganizerDashboard.routes.dev_reset import routes_dev_reset
    from OrganizerDashboard.routes.env_test import routes_env
    from OrganizerDashboard.routes.unc_credentials import routes_unc_creds
    from OrganizerDashboard.routes.batch_organize import batch_organize_bp

    app.register_blueprint(routes_dashboard)
    app.register_blueprint(routes_update_config, url_prefix='/api')
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
    if routes_api_recent_files:
        print("Registering routes_api_recent_files blueprint...")
        app.register_blueprint(routes_api_recent_files)
        print("✓ routes_api_recent_files registered")
    else:
        print("⚠ Skipping routes_api_recent_files (import failed)")
    app.register_blueprint(routes_api_open_file)
    app.register_blueprint(routes_auth_settings)
    app.register_blueprint(routes_dashboard_config)
    app.register_blueprint(routes_auth_session)
    app.register_blueprint(routes_service_install)
    app.register_blueprint(routes_factory_reset)
    app.register_blueprint(routes_setup)
    app.register_blueprint(routes_login)
    app.register_blueprint(routes_admin_tools)
    app.register_blueprint(routes_csrf)
    app.register_blueprint(routes_branding)
    app.register_blueprint(routes_user_links)
    app.register_blueprint(reports_bp)
    app.register_blueprint(routes_statistics)
    app.register_blueprint(routes_notifications)
    app.register_blueprint(routes_changelog)
    app.register_blueprint(routes_config_backup)
    app.register_blueprint(routes_watch_folders)
    app.register_blueprint(routes_docs)
    app.register_blueprint(sse_streams_bp)
    app.register_blueprint(routes_duplicates)
    app.register_blueprint(routes_dev_reset)
    app.register_blueprint(routes_env)
    app.register_blueprint(routes_unc_creds)
    app.register_blueprint(batch_organize_bp)

    # Exempt setup and login blueprints from CSRF (run before session exists)
    csrf.exempt(routes_setup)
    csrf.exempt(routes_login)
    csrf.exempt(routes_dev_reset)  # Dev-only, no auth required
    # Exempt config update API from CSRF; relies on auth + basic rights
    csrf.exempt(routes_update_config)
    # Exempt service control endpoints; guarded by auth/rights server-side
    csrf.exempt(routes_start_service)
    csrf.exempt(routes_stop_service)
    csrf.exempt(routes_restart_service)
    # Exempt environment test utility endpoints (includes POST to run pytest)
    csrf.exempt(routes_env)
    # Exempt batch organize endpoints
    csrf.exempt(batch_organize_bp)

    # Initialize authentication manager after all globals are set
    from OrganizerDashboard.auth.auth import initialize_auth_manager
    initialize_auth_manager()

    # Debug: List all registered routes
    print("\n=== Registered Routes ===")
    for rule in app.url_map.iter_rules():
        if 'recent_files' in rule.rule:
            methods = ', '.join(rule.methods) if rule.methods else 'GET'
            print(f"  {rule.rule} -> {rule.endpoint} [{methods}]")
    print("========================\n")

    return app

# --- Main Entry Point ---
if __name__ == "__main__":
    print("✅ Dashboard running at http://localhost:5000")
    create_app().run(host="0.0.0.0", port=5000)
