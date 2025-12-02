
"""Organizer.py

Watches a user's Downloads folder and moves files into categorized
subfolders based on file extensions.

This module aims to be readable and easy-to-run for development. It will
attempt to load `organizer_config.json` from the current working directory
and use the `routes` mapping there if present. Otherwise it falls back to a
bundled `EXTENSION_MAP`.
"""

from pathlib import Path
import os
import shutil
import json
import logging
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from base64 import b64decode
from datetime import datetime


# -----------------------------
# Configuration and paths
# -----------------------------
SCRIPT_DIR = Path(__file__).parent
CONFIG_PATHS = [SCRIPT_DIR / "organizer_config.json", Path("C:/Scripts/organizer_config.json")]
CONFIG = {}
for p in CONFIG_PATHS:
    if p.exists():
        try:
            with p.open("r", encoding="utf-8") as f:
                CONFIG = json.load(f)
            break
        except Exception:
            CONFIG = {}

# Allow overriding the watch folder path via config, env var, or fallback to Downloads
downloads_path_str = CONFIG.get("watch_folder") or os.environ.get("DOWNLOADS_PATH")
if not downloads_path_str:
    # Try common Windows environment variables, otherwise fallback to user's Downloads
    try:
        username = os.environ.get("USERNAME") or os.getlogin()
    except Exception:
        username = ""
    if username:
        downloads_path_str = f"C:\\Users\\{username}\\Downloads"
    else:
        downloads_path_str = str(Path.home() / "Downloads")

DOWNLOADS_PATH = Path(downloads_path_str)
DOWNLOADS_JSON = Path(CONFIG.get("downloads_json", "C:/Scripts/downloads_dashboard.json"))
ORGANIZER_LOG = CONFIG.get("organizer_log", "organizer.log")
FILE_MOVES_JSON = Path(CONFIG.get("file_moves_json", "C:/Scripts/file_moves.json"))

# Load extension map from config if available and normalize to dot-prefixed lower-case
if CONFIG.get("routes"):
    EXTENSION_MAP = {}
    for cat, exts in CONFIG["routes"].items():
        normalized = [("." + e.lower().lstrip('.')) for e in exts]
        EXTENSION_MAP[cat] = normalized
else:
    EXTENSION_MAP = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp", ".heic"],
        "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
        "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
        "Executables": [".exe", ".msi", ".bat", ".cmd", ".ps1"],
        "Shortcuts": [".lnk", ".url"],
        "Scripts": [".py", ".js", ".html", ".css", ".json", ".xml", ".sh", ".ts", ".php"],
        "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
        "Logs": [".log"],
        "Other": []
    }

# Optional per-extension custom destination mapping: {"ext": "C:/Target/Folder"}
CUSTOM_ROUTES = {}
try:
    for ext, target in (CONFIG.get("custom_routes") or {}).items():
        if isinstance(ext, str) and isinstance(target, str) and target.strip():
            CUSTOM_ROUTES["." + ext.lower().lstrip('.')] = target.strip()
except Exception:
    CUSTOM_ROUTES = {}

IGNORE_FILES = {"dashboard_config.json", ORGANIZER_LOG}
IGNORE_EXTENSIONS = {".crdownload", ".part", ".tmp"}


# -----------------------------
# Logging
# -----------------------------
log_path = DOWNLOADS_PATH / ORGANIZER_LOG
log_path.parent.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger("Organizer")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler(log_path, encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# -----------------------------
# Core functions
# -----------------------------
def get_unique_path(dest_dir: Path, filename: str) -> str:
    """Return a unique filepath in ``dest_dir`` for ``filename`` by appending
    a numbered suffix when collisions occur.
    """
    base, ext = os.path.splitext(filename)
    candidate = dest_dir / filename
    counter = 1
    while candidate.exists():
        candidate = dest_dir / f"{base} ({counter}){ext}"
        counter += 1
    return str(candidate)


class RetryQueue:
    """Simple in-memory retry queue for failed moves to inaccessible destinations.

    Periodically attempts to move queued files. Intended primarily for network
    destinations (e.g., NAS/SMB paths) that may be temporarily unavailable.
    """
    def __init__(self, cfg: dict):
        rq = cfg.get("retry_queue", {})
        self.enabled = bool(rq.get("enabled", True))
        self.interval = int(rq.get("interval_seconds", 600))
        self.max_retries = int(rq.get("max_retries", 10))
        self.queue = []
        self.lock = threading.Lock()
        self.thread = None

    def start(self):
        if not self.enabled:
            return
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def add(self, src: str, dest: str):
        with self.lock:
            logger.info(f"Queuing move for retry: {src} -> {dest}")
            self.queue.append({"src": src, "dest": dest, "retries": 0})

    def _run(self):
        while True:
            time.sleep(self.interval)
            with self.lock:
                remaining = []
                for item in self.queue:
                    s, d, r = item["src"], item["dest"], item["retries"]
                    try:
                        Path(d).parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(s, d)
                        logger.info(f"Retry successful: {s} -> {d}")
                    except Exception as e:
                        r += 1
                        item["retries"] = r
                        if r < self.max_retries:
                            logger.warning(f"Retry {r} failed for {s} -> {d}: {e}")
                            remaining.append(item)
                        else:
                            logger.error(f"Max retries reached for {s} -> {d}: {e}")
                self.queue = remaining


def log_file_move(original_path: str, destination_path: str, category: str) -> None:
    """Log a file move to the file moves JSON for dashboard reference.
    
    Maintains a list of recent file moves with metadata including timestamp,
    original path, destination path, category, and filename. Limits to most
    recent 100 entries to prevent unbounded growth.
    """
    try:
        # Load existing moves
        moves = []
        if FILE_MOVES_JSON.exists():
            try:
                with FILE_MOVES_JSON.open("r", encoding="utf-8") as f:
                    moves = json.load(f)
            except Exception:
                moves = []
        
        # Add new move entry
        move_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_path": original_path,
            "destination_path": destination_path,
            "category": category,
            "filename": Path(destination_path).name
        }
        moves.insert(0, move_entry)  # Add to beginning (most recent first)
        
        # Keep only the 100 most recent moves
        moves = moves[:100]
        
        # Save back to file
        FILE_MOVES_JSON.parent.mkdir(parents=True, exist_ok=True)
        with FILE_MOVES_JSON.open("w", encoding="utf-8") as f:
            json.dump(moves, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to log file move: {e}")


def is_network_path(path: Path) -> bool:
    p = str(path)
    return p.startswith('\\\\') or p.startswith('\\')


def organize_file(file_path: str) -> None:
    """Move a single file into the matching category folder under Downloads.

    The function is careful to skip incomplete downloads and explicitly
    ignored files.
    """
    p = Path(file_path)
    if not p.is_file():
        return
    filename = p.name
    ext = p.suffix.lower()

    if filename in IGNORE_FILES or ext in IGNORE_EXTENSIONS:
        return

    # First, check for a custom route for this extension
    custom_target_path = CUSTOM_ROUTES.get(ext)
    if custom_target_path:
        dest_dir = Path(custom_target_path)
        category_label = "Custom"
    else:
        # Fallback to category-based routing inside Downloads
        target_dir = "Other"
        for category, extensions in EXTENSION_MAP.items():
            if ext in extensions:
                target_dir = category
                break
        dest_dir = DOWNLOADS_PATH / target_dir
        category_label = target_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = get_unique_path(dest_dir, filename)
    try:
        shutil.move(str(p), dest_path)
        logger.info(f"Moved {file_path} → {dest_path}")
        log_file_move(file_path, dest_path, category_label)
    except Exception as e:
        logger.warning(f"Move failed: {file_path} -> {dest_path}: {e}")
        # If destination is network or currently inaccessible, queue for retry
        if RETRY_QUEUE and (is_network_path(dest_dir)):
            RETRY_QUEUE.add(str(p), dest_path)
        else:
            logger.error(f"Error moving {file_path}: {e}")


def update_dashboard_json(downloads_path: Path) -> None:
    """Write a small summary JSON used by the dashboard (if configured)."""
    summary = {"last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    for entry in downloads_path.iterdir():
        if entry.is_dir():
            summary[entry.name] = str(len([f for f in entry.iterdir() if f.is_file()]))
    try:
        DOWNLOADS_JSON.parent.mkdir(parents=True, exist_ok=True)
        with DOWNLOADS_JSON.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to update dashboard JSON: {e}")


def initial_scan(downloads_path: Path) -> None:
    """Process existing files in Downloads once at startup."""
    for entry in downloads_path.iterdir():
        if entry.is_file():
            organize_file(str(entry))
    update_dashboard_json(downloads_path)
    logger.info("Initial scan complete")


class DownloadsHandler(FileSystemEventHandler):
    """Watchdog event handler for the Downloads folder."""

    def __init__(self, downloads_path: Path):
        self.downloads_path = downloads_path

    def on_created(self, event):
        if not event.is_directory:
            organize_file(str(event.src_path))
            update_dashboard_json(self.downloads_path)
    def on_moved(self, event):
        if not event.is_directory:
            organize_file(str(event.dest_path))
            update_dashboard_json(self.downloads_path)
    def on_modified(self, event):
        if not event.is_directory:
            organize_file(str(event.src_path))
            update_dashboard_json(self.downloads_path)


# -----------------------------
# Main entrypoint
# -----------------------------
if __name__ == "__main__":
    DOWNLOADS_PATH.mkdir(parents=True, exist_ok=True)
    # Initialize retry queue
    RETRY_QUEUE = RetryQueue(CONFIG)
    RETRY_QUEUE.start()
    initial_scan(DOWNLOADS_PATH)
    event_handler = DownloadsHandler(DOWNLOADS_PATH)
    observer = Observer()
    observer.schedule(event_handler, str(DOWNLOADS_PATH), recursive=False)
    observer.start()
    logger.info(f"Monitoring {DOWNLOADS_PATH} started")
    print(f"Monitoring {DOWNLOADS_PATH}... Press Ctrl+C to stop.")
    try:
        # Sleep in the loop to avoid a busy-wait and reduce CPU usage
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logger.info("Monitoring stopped")
