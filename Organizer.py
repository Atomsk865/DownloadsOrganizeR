"""
SortNStore Organizer - Advanced Multi-Folder File Organization Service

Watches multiple folders and intelligently routes files based on:
  - File extensions (primary routing)
  - Filename patterns and tags
  - File size and date ranges
  - File metadata (creation/modification dates)
  - Custom rules (user-defined patterns)
  - Duplicate detection and handling

Features:
  - Multiple watch folders support
  - Flexible routing rule system
  - Network path support with retry queue
  - Comprehensive logging and statistics
  - Configuration-driven behavior
  - Thread-safe operations
"""

from pathlib import Path
import os
import shutil
import json
import logging
import time
import hashlib
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading


# ============================================================================
# CONFIGURATION & INITIALIZATION
# ============================================================================

SCRIPT_DIR = Path(__file__).parent
CONFIG_PATHS = [
    SCRIPT_DIR / "organizer_config.json",
    Path("C:/Scripts/organizer_config.json"),
    Path("C:/ProgramData/SortNStore/organizer_config.json")
]

CONFIG = {}
for p in CONFIG_PATHS:
    if p.exists():
        try:
            with p.open("r", encoding="utf-8") as f:
                CONFIG = json.load(f)
            break
        except Exception:
            CONFIG = {}


def _build_extension_map(routes: dict) -> Dict[str, List[str]]:
    """Build normalized extension map from config."""
    if not routes:
        return _default_extension_map()
    
    ext_map = {}
    for category, extensions in routes.items():
        if isinstance(extensions, list):
            normalized = [("." + e.lower().lstrip('.')) for e in extensions]
            ext_map[category] = normalized
    return ext_map if ext_map else _default_extension_map()


def _default_extension_map() -> Dict[str, List[str]]:
    """Default extension categorization."""
    return {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp", ".heic", ".ico"],
        "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff", ".ape"],
        "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".ts"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".pages", ".numbers"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
        "Executables": [".exe", ".msi", ".bat", ".cmd", ".ps1", ".app", ".dmg"],
        "Shortcuts": [".lnk", ".url", ".webloc"],
        "Code": [".py", ".js", ".html", ".css", ".json", ".xml", ".sh", ".ts", ".php", ".java", ".cpp", ".c", ".h", ".cs", ".rb", ".go"],
        "Fonts": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
        "Data": [".sql", ".db", ".sqlite", ".xlsx", ".json", ".yaml", ".yml", ".xml"],
        "Logs": [".log"],
        "Other": []
    }


def _build_custom_routes(custom_routes: dict) -> Dict[str, str]:
    """Build extension -> custom destination mapping."""
    routes = {}
    for ext, target in (custom_routes or {}).items():
        if isinstance(ext, str) and isinstance(target, str):
            norm_ext = "." + ext.lower().lstrip('.')
            routes[norm_ext] = target.strip()
    return routes


def _build_tag_routes(tag_routes: dict) -> Dict[str, str]:
    """Build filename tag -> destination mapping."""
    routes = {}
    for tag, target in (tag_routes or {}).items():
        if isinstance(tag, str) and isinstance(target, str):
            routes[tag.lower()] = target.strip()
    return routes


def _build_pattern_routes(pattern_routes: dict) -> Dict[str, str]:
    """Build regex pattern -> destination mapping."""
    routes = {}
    for pattern, target in (pattern_routes or {}).items():
        if isinstance(pattern, str) and isinstance(target, str):
            try:
                re.compile(pattern)  # Validate regex
                routes[pattern] = target.strip()
            except re.error:
                pass
    return routes


# Get watch folders from config
WATCH_FOLDERS = []
wf = CONFIG.get("watch_folders")
if isinstance(wf, list) and wf:
    try:
        WATCH_FOLDERS = [Path(p) for p in wf if p]
    except Exception:
        WATCH_FOLDERS = []

if not WATCH_FOLDERS:
    wf_str = CONFIG.get("watch_folder")
    if wf_str:
        WATCH_FOLDERS = [Path(wf_str)]
    else:
        try:
            username = os.environ.get("USERNAME") or os.getlogin()
        except Exception:
            username = ""
        if username:
            downloads_path = Path(f"C:\\Users\\{username}\\Downloads")
        else:
            downloads_path = Path.home() / "Downloads"
        WATCH_FOLDERS = [downloads_path]

# Build routing configuration
EXTENSION_MAP = _build_extension_map(CONFIG.get("routes", {}))
CUSTOM_ROUTES = _build_custom_routes(CONFIG.get("custom_routes", {}))
TAG_ROUTES = _build_tag_routes(CONFIG.get("tag_routes", {}))
PATTERN_ROUTES = _build_pattern_routes(CONFIG.get("pattern_routes", {}))
SIZE_RULES = CONFIG.get("size_rules", [])
DATE_RULES = CONFIG.get("date_rules", [])

# Destination configuration (supports local, UNC, cloud paths)
DESTINATION_MODE = CONFIG.get("destination_mode", "subfolder")  # "subfolder" or "custom"
BASE_DESTINATION = CONFIG.get("base_destination", None)  # Override base path
CATEGORY_DESTINATIONS = CONFIG.get("category_destinations", {})  # Per-category overrides

# Logging configuration
LOGS_DIR = Path(CONFIG.get("logs_dir", SCRIPT_DIR / "logs"))
LOGS_DIR.mkdir(parents=True, exist_ok=True)
ORGANIZER_LOG = str(LOGS_DIR / "organizer.log")

# File tracking
FILE_MOVES_JSON = Path(CONFIG.get("file_moves_json", SCRIPT_DIR / "config" / "json" / "file_moves.json"))
FILE_HASHES_JSON = Path(CONFIG.get("file_hashes_json", SCRIPT_DIR / "config" / "json" / "file_hashes.json"))
NOTIFICATION_HISTORY_JSON = Path(CONFIG.get("notification_history_json", SCRIPT_DIR / "notification_history.json"))

# Ignore list
IGNORE_FILES = {
    "dashboard_config.json",
    "organizer_config.json",
    Path(ORGANIZER_LOG).name if ORGANIZER_LOG else ""
}
IGNORE_EXTENSIONS = {".crdownload", ".part", ".tmp", ".downloading", ".incomplete"}


# ============================================================================
# LOGGING SETUP
# ============================================================================

log_path = LOGS_DIR / "organizer.log"
log_path.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("SortNStore")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler(log_path, encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_unique_path(dest_dir: Path, filename: str) -> Path:
    """Return unique filepath by appending numbered suffix on collision."""
    base, ext = os.path.splitext(filename)
    candidate = dest_dir / filename
    counter = 1
    while candidate.exists():
        candidate = dest_dir / f"{base} ({counter}){ext}"
        counter += 1
    return candidate


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """Calculate hash of file for duplicate detection."""
    try:
        hasher = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.warning(f"Failed to hash {file_path}: {e}")
        return ""


def is_duplicate(file_path: Path) -> bool:
    """Check if file is a duplicate based on content hash."""
    try:
        file_hash = calculate_file_hash(file_path)
        if not file_hash:
            return False
        
        hashes = {}
        if FILE_HASHES_JSON.exists():
            with FILE_HASHES_JSON.open("r", encoding="utf-8") as f:
                hashes = json.load(f)
        
        if file_hash in hashes.values():
            logger.info(f"Duplicate detected: {file_path.name}")
            return True
        
        return False
    except Exception as e:
        logger.warning(f"Duplicate check failed: {e}")
        return False


def is_network_path(path: Path) -> bool:
    """Check if path is on network (UNC)."""
    p = str(path)
    return p.startswith('\\\\') or p.startswith('\\')


def is_cloud_path(path: Path) -> bool:
    """Check if path is on cloud storage (OneDrive, Google Drive, Dropbox, etc)."""
    p = str(path).lower()
    cloud_indicators = [
        'onedrive',
        'google drive',
        'googledrive',
        'dropbox',
        'icloud',
        'box.com',
        'mega',
        'pcloud',
        'sync.com'
    ]
    return any(indicator in p for indicator in cloud_indicators)


def resolve_destination_path(category: str, watch_folder: Path) -> Path:
    """Resolve destination path for a category based on configuration.
    
    Supports:
    - Subfolder mode (default): {watch_folder}/{category}
    - Custom mode with base_destination: {base_destination}/{category}
    - Per-category overrides: Absolute paths including UNC, cloud storage
    - Network paths (UNC): \\\\server\\share\\path
    - Cloud storage: C:\\Users\\You\\OneDrive\\Documents
    """
    # Check for per-category override first
    if category in CATEGORY_DESTINATIONS:
        dest = CATEGORY_DESTINATIONS[category]
        if isinstance(dest, str):
            return Path(dest)
    
    # Check if custom base destination is set
    if BASE_DESTINATION:
        base = Path(BASE_DESTINATION)
        return base / category
    
    # Default: subfolder mode
    if DESTINATION_MODE == "subfolder":
        return watch_folder / category
    
    # Fallback to watch folder subfolder
    return watch_folder / category


def is_file_accessible(file_path: Path, timeout: float = 2.0) -> bool:
    """Check if file is accessible and not locked."""
    try:
        with open(file_path, 'rb') as f:
            f.read(1)
        return True
    except (PermissionError, OSError):
        return False


# ============================================================================
# ADVANCED ROUTING ENGINE
# ============================================================================

class RoutingEngine:
    """Determines destination folder for a file using multiple criteria."""
    
    def __init__(self, config: dict):
        self.config = config
        self.duplicate_action = config.get("duplicate_action", "skip")
    
    def route_file(self, file_path: Path) -> Optional[Tuple[Path, str]]:
        """
        Route file and return (destination_path, routing_reason) or None.
        
        Routing priority:
          1. Check duplicates (if enabled)
          2. Custom per-extension routes
          3. Filename tag routes
          4. Regex pattern routes
          5. File size rules
          6. Date range rules
          7. Extension-based categorization
        """
        
        # Skip certain files
        if file_path.name in IGNORE_FILES or file_path.suffix in IGNORE_EXTENSIONS:
            return None
        
        # Check for duplicates
        if self.config.get("duplicate_detection", {}).get("enabled", False):
            if is_duplicate(file_path):
                if self.duplicate_action == "skip":
                    return None
        
        # 1. Custom per-extension routes (highest priority)
        result = self._check_custom_routes(file_path)
        if result:
            return result
        
        # 2. Filename tag routes
        result = self._check_tag_routes(file_path)
        if result:
            return result
        
        # 3. Regex pattern routes
        result = self._check_pattern_routes(file_path)
        if result:
            return result
        
        # 4. File size rules
        result = self._check_size_rules(file_path)
        if result:
            return result
        
        # 5. Date range rules
        result = self._check_date_rules(file_path)
        if result:
            return result
        
        # 6. Extension-based categorization (default)
        return self._check_extension_routes(file_path)
    
    def _check_custom_routes(self, file_path: Path) -> Optional[Tuple[Path, str]]:
        """Check custom per-extension routes."""
        ext = file_path.suffix.lower()
        if ext in CUSTOM_ROUTES:
            target = Path(CUSTOM_ROUTES[ext])
            return target, f"custom_route:{ext}"
        return None
    
    def _check_tag_routes(self, file_path: Path) -> Optional[Tuple[Path, str]]:
        """Check filename contains tag."""
        filename_lower = file_path.stem.lower()
        for tag, target in TAG_ROUTES.items():
            if tag in filename_lower:
                return Path(target), f"tag_route:{tag}"
        return None
    
    def _check_pattern_routes(self, file_path: Path) -> Optional[Tuple[Path, str]]:
        """Check regex patterns against filename."""
        filename = file_path.name
        for pattern, target in PATTERN_ROUTES.items():
            try:
                if re.search(pattern, filename, re.IGNORECASE):
                    return Path(target), f"pattern_route:{pattern}"
            except re.error:
                pass
        return None
    
    def _check_size_rules(self, file_path: Path) -> Optional[Tuple[Path, str]]:
        """Check file size rules."""
        try:
            file_size = file_path.stat().st_size / (1024 * 1024)
            for rule in SIZE_RULES:
                min_mb = rule.get("min_mb", 0)
                max_mb = rule.get("max_mb", float('inf'))
                if min_mb <= file_size <= max_mb:
                    target = rule.get("destination")
                    if target:
                        return Path(target), f"size_rule:{min_mb}-{max_mb}MB"
        except Exception as e:
            logger.warning(f"Size rule check failed for {file_path}: {e}")
        return None
    
    def _check_date_rules(self, file_path: Path) -> Optional[Tuple[Path, str]]:
        """Check file creation/modification date rules."""
        try:
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            for rule in DATE_RULES:
                days_old = rule.get("days_older_than")
                newer_than = rule.get("days_newer_than")
                
                age = (datetime.now() - mod_time).days
                
                if days_old and age >= days_old:
                    target = rule.get("destination")
                    if target:
                        return Path(target), f"date_rule:older_{days_old}d"
                
                if newer_than and age <= newer_than:
                    target = rule.get("destination")
                    if target:
                        return Path(target), f"date_rule:newer_{newer_than}d"
        except Exception as e:
            logger.warning(f"Date rule check failed for {file_path}: {e}")
        return None
    
    def _check_extension_routes(self, file_path: Path) -> Optional[Tuple[Path, str]]:
        """Default extension-based categorization."""
        ext = file_path.suffix.lower()
        
        # Determine watch folder context (for subfolder mode)
        watch_folder = file_path.parent
        
        for category, extensions in EXTENSION_MAP.items():
            if ext in extensions:
                target = resolve_destination_path(category, watch_folder)
                return target, f"extension:{category}"
        
        # Fallback to "Other" category
        target = resolve_destination_path("Other", watch_folder)
        return target, "extension:Other"


# ============================================================================
# RETRY QUEUE FOR NETWORK PATHS
# ============================================================================

class RetryQueue:
    """Retry queue for failed moves (especially network destinations)."""
    
    def __init__(self, config: dict):
        rq = config.get("retry_queue", {})
        self.enabled = bool(rq.get("enabled", True))
        self.interval = int(rq.get("interval_seconds", 600))
        self.max_retries = int(rq.get("max_retries", 10))
        self.queue = []
        self.lock = threading.Lock()
        self.thread = None
    
    def start(self):
        """Start retry worker thread."""
        if not self.enabled:
            return
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("RetryQueue started")
    
    def add(self, src: str, dest: str, reason: str = ""):
        """Add file move to retry queue."""
        with self.lock:
            logger.info(f"Queuing for retry: {src} -> {dest} ({reason})")
            self.queue.append({
                "src": src,
                "dest": dest,
                "reason": reason,
                "retries": 0,
                "added_at": datetime.now().isoformat()
            })
    
    def _run(self):
        """Worker thread main loop."""
        while True:
            time.sleep(self.interval)
            with self.lock:
                remaining = []
                for item in self.queue:
                    s, d, r = item["src"], item["dest"], item["retries"]
                    try:
                        Path(d).parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(s, d)
                        logger.info(f"Retry succeeded: {s} -> {d}")
                    except Exception as e:
                        r += 1
                        item["retries"] = r
                        if r < self.max_retries:
                            logger.warning(f"Retry {r}/{self.max_retries} failed: {e}")
                            remaining.append(item)
                        else:
                            logger.error(f"Max retries exhausted: {s} -> {d}")
                self.queue = remaining


# ============================================================================
# FILE MOVE LOGGING
# ============================================================================

def log_file_move(original_path: str, destination_path: str, category: str, reason: str = "") -> None:
    """Log file move to JSON for dashboard."""
    try:
        moves = []
        if FILE_MOVES_JSON.exists():
            try:
                with FILE_MOVES_JSON.open("r", encoding="utf-8") as f:
                    moves = json.load(f)
            except Exception:
                moves = []
        
        move_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_path": original_path,
            "destination_path": destination_path,
            "category": category,
            "reason": reason,
            "filename": Path(destination_path).name
        }
        moves.insert(0, move_entry)
        moves = moves[:1000]
        
        FILE_MOVES_JSON.parent.mkdir(parents=True, exist_ok=True)
        with FILE_MOVES_JSON.open("w", encoding="utf-8") as f:
            json.dump(moves, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to log file move: {e}")


def update_file_hash(file_path: Path, hash_value: str) -> None:
    """Update file hash for duplicate detection."""
    try:
        hashes = {}
        if FILE_HASHES_JSON.exists():
            with FILE_HASHES_JSON.open("r", encoding="utf-8") as f:
                hashes = json.load(f)
        
        hashes[hash_value] = str(file_path)
        
        FILE_HASHES_JSON.parent.mkdir(parents=True, exist_ok=True)
        with FILE_HASHES_JSON.open("w", encoding="utf-8") as f:
            json.dump(hashes, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to update file hash: {e}")


# ============================================================================
# FILE SYSTEM EVENT HANDLER
# ============================================================================

class SortNStoreHandler(FileSystemEventHandler):
    """Handles file system events (creation, modification)."""
    
    def __init__(self, watch_folder: Path, routing_engine: RoutingEngine, retry_queue: RetryQueue):
        super().__init__()
        self.watch_folder = watch_folder
        self.routing_engine = routing_engine
        self.retry_queue = retry_queue
        self.processing = set()
        self.lock = threading.Lock()
    
    def on_created(self, event):
        """Handle file creation."""
        if event.is_dir:
            return
        self._process_file(Path(event.src_path))
    
    def on_modified(self, event):
        """Handle file modification."""
        if event.is_dir:
            return
        self._process_file(Path(event.src_path))
    
    def on_moved(self, event):
        """Handle file moved into watch folder."""
        if event.is_dir:
            return
        self._process_file(Path(event.dest_path))
    
    def _process_file(self, file_path: Path):
        """Process a file for organization."""
        with self.lock:
            if file_path in self.processing:
                return
            self.processing.add(file_path)
        
        try:
            for attempt in range(10):
                if is_file_accessible(file_path):
                    break
                time.sleep(0.5)
            else:
                logger.warning(f"File not accessible after 5s: {file_path}")
                return
            
            result = self.routing_engine.route_file(file_path)
            if not result:
                logger.debug(f"File skipped (ignored): {file_path.name}")
                return
            
            dest_dir, reason = result
            
            try:
                dest_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create destination {dest_dir}: {e}")
                return
            
            unique_dest = get_unique_path(dest_dir, file_path.name)
            
            try:
                shutil.move(str(file_path), str(unique_dest))
                logger.info(f"Organized: {file_path.name} -> {unique_dest} ({reason})")
                log_file_move(str(file_path), str(unique_dest), reason.split(':')[0], reason)
                
                if CONFIG.get("duplicate_detection", {}).get("enabled"):
                    file_hash = calculate_file_hash(Path(unique_dest))
                    if file_hash:
                        update_file_hash(Path(unique_dest), file_hash)
            
            except Exception as e:
                logger.error(f"Failed to move {file_path}: {e}")
                # Queue for retry if network or cloud path
                if is_network_path(dest_dir) or is_cloud_path(dest_dir):
                    self.retry_queue.add(str(file_path), str(unique_dest), reason)
        
        finally:
            with self.lock:
                self.processing.discard(file_path)


# ============================================================================
# MAIN ORGANIZER
# ============================================================================

def main():
    """Main entry point for organizer service."""
    logger.info("=" * 70)
    logger.info("SortNStore File Organizer Starting")
    logger.info("=" * 70)
    logger.info(f"Watch folders: {[str(f) for f in WATCH_FOLDERS]}")
    
    routing_engine = RoutingEngine(CONFIG)
    retry_queue = RetryQueue(CONFIG)
    retry_queue.start()
    
    observer = Observer()
    
    for folder in WATCH_FOLDERS:
        if not folder.exists():
            logger.warning(f"Watch folder doesn't exist: {folder}")
            continue
        
        handler = SortNStoreHandler(folder, routing_engine, retry_queue)
        observer.schedule(handler, str(folder), recursive=False)
        logger.info(f"Watching: {folder}")
    
    observer.start()
    logger.info("Organizer started successfully. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping organizer...")
        observer.stop()
    
    observer.join()
    logger.info("Organizer stopped.")


if __name__ == "__main__":
    main()
