# Makes OrganizerDashboard a package
# Export config and globals for use by routes and other modules

import os
import json

# --- Service and Config ---
SERVICE_NAME = "DownloadsOrganizer"
CONFIG_FILE = "organizer_config.json"

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
    "logs_dir": r"C:\Scripts\service-logs"
}

config = DEFAULT_CONFIG.copy()
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
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

LOGS_DIR = None
STDOUT_LOG = None
STDERR_LOG = None
update_log_paths()

__all__ = ['config', 'ADMIN_USER', 'ADMIN_PASS', 'ADMIN_PASS_HASH', 'SERVICE_NAME', 'LOGS_DIR', 'STDOUT_LOG', 'STDERR_LOG', 'update_log_paths', 'DEFAULT_CONFIG']

# --- App Factory Bridge ---
# Tests import OrganizerDashboard and expect a create_app() symbol.
# Provide a thin wrapper that delegates to the top-level OrganizerDashboard.py.
def create_app():
    import importlib.util
    import sys as _sys
    import os as _os
    root = _os.path.dirname(_os.path.dirname(__file__))
    entry = _os.path.join(root, 'OrganizerDashboard.py')
    spec = importlib.util.spec_from_file_location('OrganizerDashboard_entry', entry)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        # Register the dynamic module name so OrganizerDashboard.py can reference sys.modules[__name__]
        import sys as _sys
        _sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        if hasattr(mod, 'create_app'):
            return mod.create_app()
    raise AttributeError('OrganizerDashboard.create_app not available')

__all__.append('create_app')