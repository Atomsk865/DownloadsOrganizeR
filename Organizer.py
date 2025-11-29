
import os
import shutil
import json
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# ============================================================
# CONFIGURATION SECTION
# ============================================================

#Set Username Variable
uname = input("Please enter your PC username name: ")


DOWNLOADS_PATH = f"C:\\Users\\{uname}\\Downloads"
DOWNLOADS_JSON = "C:\\Scripts\\downloads_dashboard.json"
ORGANIZER_LOG = "organizer.log"  # exclusive log file to ignore

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
    "Logs": [".log"],  # dedicated folder for log files
    "Other": []  # catch-all
}
IGNORE_FILES = {"dashboard_config.json", ORGANIZER_LOG}
IGNORE_EXTENSIONS = {".crdownload", ".part", ".tmp"}

# ============================================================
# LOGGING SETUP
# ============================================================
log_path = os.path.join(DOWNLOADS_PATH, ORGANIZER_LOG)
logger = logging.getLogger("Organizer")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s\n %(levelname)s\n %(message)s", "%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler(log_path, encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ============================================================
# CORE LOGIC
# ============================================================
def get_unique_path(dest_dir, filename):
    """Generate a unique file path if duplicate exists."""
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(dest_dir, filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(dest_dir, f"{base} ({counter}){ext}")
        counter += 1
    return candidate

def organize_file(file_path):
    if not os.path.isfile(file_path):
        return
    filename = os.path.basename(file_path).lower()
    ext = os.path.splitext(file_path)[1].lower()
    # Only log actual changes, not searches or ignored files
    if filename in IGNORE_FILES or ext in IGNORE_EXTENSIONS:
        return
    target_dir = "Other"
    for category, extensions in EXTENSION_MAP.items():
        if ext in extensions:
            target_dir = category
            break
    dest_dir = os.path.join(DOWNLOADS_PATH, target_dir)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = get_unique_path(dest_dir, os.path.basename(file_path))
    try:
        shutil.move(file_path, dest_path)
        logger.info(f"Moved {file_path} → {dest_path}")
    except Exception as e:
        logger.error(f"Error moving {file_path}: {e}")

def update_dashboard_json(downloads_path):
    summary = {"last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    for entry in os.scandir(downloads_path):
        if entry.is_dir():
            summary[entry.name] = len([f for f in os.scandir(entry.path) if f.is_file()])
    with open(DOWNLOADS_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    logger.info("Dashboard JSON updated")

def initial_scan(downloads_path):
    for entry in os.scandir(downloads_path):
        if entry.is_file():
            organize_file(entry.path)
    update_dashboard_json(downloads_path)
    logger.info("Initial scan complete")

class DownloadsHandler(FileSystemEventHandler):
    def __init__(self, downloads_path):
        self.downloads_path = downloads_path
    def on_created(self, event):
        if not event.is_directory:
            organize_file(event.src_path)
            update_dashboard_json(self.downloads_path)
    def on_moved(self, event):
        if not event.is_directory:
            organize_file(event.dest_path)
            update_dashboard_json(self.downloads_path)
    def on_modified(self, event):
        if not event.is_directory:
            organize_file(event.src_path)
            update_dashboard_json(self.downloads_path)

# ============================================================
# MAIN ENTRY POINT
# ============================================================
if __name__ == "__main__":
    initial_scan(DOWNLOADS_PATH)
    event_handler = DownloadsHandler(DOWNLOADS_PATH)
    observer = Observer()
    observer.schedule(event_handler, DOWNLOADS_PATH, recursive=False)
    observer.start()
    logger.info(f"Monitoring {DOWNLOADS_PATH} started")
    print(f"Monitoring {DOWNLOADS_PATH}... Press Ctrl+C to stop.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logger.info("Monitoring stopped")
