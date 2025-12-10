#!/usr/bin/env python3
"""
BatchSortNStore.py - One-time file organization service

Unlike the continuous SortNStoreService (formerly Organizer.py),
BatchSortNStore is designed to be run once (manually or via scheduler)
to organize files in specified watch folders.

Usage:
    python BatchSortNStore.py                    # Organize all configured watch folders
    python BatchSortNStore.py --folder "C:/path" # Organize specific folder
    python BatchSortNStore.py --dry-run          # Preview without moving files
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get script directory
SCRIPT_DIR = Path(__file__).parent.absolute()
CONFIG_DIR = SCRIPT_DIR / "config" / "json"
BATCH_CONFIG_PATH = SCRIPT_DIR / "batch_organizer_config.json"
HISTORY_PATH = CONFIG_DIR / "file_organization_history.json"

# Ensure config directory exists
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_batch_config():
    """Load batch organizer configuration"""
    if not BATCH_CONFIG_PATH.exists():
        default_config = {
            "watch_folders": [
                str(Path.home() / "Downloads")
            ],
            "dry_run": False,
            "recursive": True,
            "exclude_extensions": [".crdownload", ".part", ".tmp"],
            "exclude_files": ["desktop.ini", "thumbs.db"]
        }
        save_batch_config(default_config)
        return default_config
    
    try:
        return json.loads(BATCH_CONFIG_PATH.read_text())
    except Exception as e:
        logger.error(f"Failed to load batch config: {e}")
        return {"watch_folders": [str(Path.home() / "Downloads")]}


def save_batch_config(config):
    """Save batch organizer configuration"""
    try:
        BATCH_CONFIG_PATH.write_text(json.dumps(config, indent=2))
        logger.info(f"Saved batch config to {BATCH_CONFIG_PATH}")
    except Exception as e:
        logger.error(f"Failed to save batch config: {e}")


def load_history():
    """Load file organization history"""
    if not HISTORY_PATH.exists():
        return {"operations": []}
    try:
        return json.loads(HISTORY_PATH.read_text())
    except Exception:
        return {"operations": []}


def save_history(history):
    """Save file organization history"""
    try:
        HISTORY_PATH.write_text(json.dumps(history, indent=2))
    except Exception as e:
        logger.error(f"Failed to save history: {e}")


def record_move(source, destination, category, batch_id=None):
    """Record a file move in history"""
    history = load_history()
    operation = {
        "timestamp": datetime.now().isoformat(),
        "source": str(source),
        "destination": str(destination),
        "category": category,
        "batch_id": batch_id,
        "status": "completed"
    }
    history["operations"].append(operation)
    save_history(history)
    logger.info(f"Recorded: {Path(source).name} → {category}")
    return operation


def get_unique_path(dest_dir, filename):
    """Get unique path by appending counter if file exists"""
    dest_path = Path(dest_dir) / filename
    if not dest_path.exists():
        return dest_path
    
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    
    while True:
        new_filename = f"{stem} ({counter}){suffix}"
        dest_path = Path(dest_dir) / new_filename
        if not dest_path.exists():
            return dest_path
        counter += 1


def get_category_for_file(file_path, extension_map):
    """Determine category for a file based on extension"""
    ext = Path(file_path).suffix.lower()
    for category, extensions in extension_map.items():
        if ext in extensions:
            return category
    return "Other"


def organize_files_in_folder(folder_path, dry_run=False, batch_id=None):
    """
    Organize all files in a folder
    
    Args:
        folder_path: Path to folder to organize
        dry_run: If True, preview without moving
        batch_id: Unique identifier for batch operation
        
    Returns:
        Dictionary with operation results
    """
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        logger.warning(f"Folder does not exist: {folder_path}")
        return {
            "folder": str(folder_path),
            "success": False,
            "error": "Folder not found",
            "files_organized": 0,
            "files_skipped": 0,
            "errors": []
        }
    
    # Load extension map from sortnstore_config.json or organizer_config.json
    extension_map = load_extension_map()
    batch_config = load_batch_config()
    
    exclude_extensions = set(batch_config.get("exclude_extensions", []))
    exclude_files = set(batch_config.get("exclude_files", []))
    
    files_organized = 0
    files_skipped = 0
    errors = []
    operations = []
    
    logger.info(f"Scanning folder: {folder_path}")
    
    # Get all files
    files = [f for f in folder_path.glob("*") if f.is_file()]
    if batch_config.get("recursive", False):
        files.extend([f for f in folder_path.rglob("*") if f.is_file()])
    
    logger.info(f"Found {len(files)} files in {folder_path}")
    
    for file_path in files:
        try:
            filename = file_path.name
            
            # Skip ignored files
            if filename in exclude_files:
                files_skipped += 1
                continue
            
            # Skip ignored extensions
            if file_path.suffix.lower() in exclude_extensions:
                files_skipped += 1
                continue
            
            # Skip if file is in a subdirectory that's not a category folder
            if file_path.parent != folder_path and not file_path.parent.name in extension_map:
                files_skipped += 1
                continue
            
            category = get_category_for_file(file_path, extension_map)
            dest_dir = folder_path / category
            
            if dry_run:
                operations.append({
                    "file": filename,
                    "source": str(file_path),
                    "destination": str(dest_dir / filename),
                    "category": category,
                    "status": "would_organize"
                })
                files_organized += 1
            else:
                # Create category directory
                dest_dir.mkdir(exist_ok=True)
                dest_path = get_unique_path(dest_dir, filename)
                
                # Move file
                shutil.move(str(file_path), str(dest_path))
                record_move(str(file_path), str(dest_path), category, batch_id)
                
                operations.append({
                    "file": filename,
                    "source": str(file_path),
                    "destination": str(dest_path),
                    "category": category,
                    "status": "organized"
                })
                files_organized += 1
                logger.info(f"Organized: {filename} → {category}")
        
        except Exception as e:
            files_skipped += 1
            error_msg = f"Error organizing {file_path.name}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
    
    return {
        "folder": str(folder_path),
        "success": True,
        "batch_id": batch_id,
        "files_organized": files_organized,
        "files_skipped": files_skipped,
        "errors": errors,
        "operations": operations
    }


def load_extension_map():
    """Load file extension mapping from config"""
    config_files = [
        SCRIPT_DIR / "sortnstore_config.json",
        SCRIPT_DIR / "config.json",
        SCRIPT_DIR / "organizer_config.json"
    ]
    
    for config_file in config_files:
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text())
                if "routes" in config:
                    # Convert to {ext: category} format
                    ext_map = {}
                    for category, exts in config["routes"].items():
                        for ext in exts:
                            if not ext.startswith("."):
                                ext = "." + ext
                            ext_map[ext.lower()] = category
                    return ext_map
            except Exception as e:
                logger.warning(f"Failed to load config from {config_file}: {e}")
    
    # Default extension map
    return {
        ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images",
        ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos",
        ".mp3": "Music", ".wav": "Music", ".flac": "Music",
        ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents", ".txt": "Documents",
        ".zip": "Archives", ".rar": "Archives", ".7z": "Archives"
    }


def add_watch_folder(folder_path):
    """Add a folder to watch list"""
    config = load_batch_config()
    folder_path = str(Path(folder_path).absolute())
    
    if folder_path not in config["watch_folders"]:
        config["watch_folders"].append(folder_path)
        save_batch_config(config)
        logger.info(f"Added watch folder: {folder_path}")
        return True
    return False


def remove_watch_folder(folder_path):
    """Remove a folder from watch list"""
    config = load_batch_config()
    folder_path = str(Path(folder_path).absolute())
    
    if folder_path in config["watch_folders"]:
        config["watch_folders"].remove(folder_path)
        save_batch_config(config)
        logger.info(f"Removed watch folder: {folder_path}")
        return True
    return False


def get_watch_folders():
    """Get list of configured watch folders"""
    config = load_batch_config()
    return config.get("watch_folders", [])


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Batch organize files in configured watch folders"
    )
    parser.add_argument("--folder", help="Organize specific folder instead of configured watches")
    parser.add_argument("--dry-run", action="store_true", help="Preview without moving files")
    parser.add_argument("--add-folder", help="Add folder to watch list")
    parser.add_argument("--remove-folder", help="Remove folder from watch list")
    parser.add_argument("--list-folders", action="store_true", help="List configured watch folders")
    
    args = parser.parse_args()
    
    # Handle configuration commands
    if args.add_folder:
        add_watch_folder(args.add_folder)
        return
    
    if args.remove_folder:
        remove_watch_folder(args.remove_folder)
        return
    
    if args.list_folders:
        folders = get_watch_folders()
        print(json.dumps(folders, indent=2))
        return
    
    # Organize files
    batch_id = datetime.now().isoformat()
    folders_to_organize = []
    
    if args.folder:
        folders_to_organize = [args.folder]
    else:
        folders_to_organize = get_watch_folders()
    
    if not folders_to_organize:
        logger.warning("No folders to organize")
        return
    
    logger.info(f"Starting batch organization (dry_run={args.dry_run})")
    
    total_organized = 0
    total_skipped = 0
    all_errors = []
    
    for folder in folders_to_organize:
        result = organize_files_in_folder(folder, dry_run=args.dry_run, batch_id=batch_id)
        total_organized += result["files_organized"]
        total_skipped += result["files_skipped"]
        all_errors.extend(result["errors"])
        
        logger.info(f"Folder: {folder} - Organized: {result['files_organized']}, Skipped: {result['files_skipped']}")
    
    logger.info(f"Batch complete - Organized: {total_organized}, Skipped: {total_skipped}")
    if all_errors:
        logger.warning(f"Errors: {len(all_errors)}")


if __name__ == "__main__":
    main()
