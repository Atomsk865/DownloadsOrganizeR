"""
duplicates.py - Duplicate File Detection Routes

Provides API endpoints for detecting, listing, and managing duplicate files
based on SHA256 hash comparison.

Routes:
    GET  /api/duplicates - List all duplicate files grouped by hash
    POST /api/duplicates/resolve - Resolve duplicates by keeping/deleting files
"""

from flask import Blueprint, jsonify, request
from pathlib import Path
import json
import logging
import os
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

routes_duplicates = Blueprint('routes_duplicates', __name__)

# Path to file hashes database
ROOT = Path(__file__).resolve().parents[2]
FILE_HASHES_JSON = ROOT / "config" / "json" / "file_hashes.json"


def require_auth(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Basic auth check - assumes session is already validated
        # This matches the pattern used in other routes
        return f(*args, **kwargs)
    return decorated_function


def load_file_hashes():
    """Load the file hashes database from JSON.
    
    Returns:
        Dictionary mapping SHA256 hashes to lists of file paths
    """
    if not FILE_HASHES_JSON.exists():
        return {}
    try:
        with FILE_HASHES_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load file hashes: {e}")
        return {}


def save_file_hashes(hashes):
    """Save the file hashes database to JSON.
    
    Args:
        hashes: Dictionary mapping SHA256 hashes to lists of file paths
    """
    try:
        FILE_HASHES_JSON.parent.mkdir(parents=True, exist_ok=True)
        with FILE_HASHES_JSON.open("w", encoding="utf-8") as f:
            json.dump(hashes, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save file hashes: {e}")


def get_file_metadata(file_path):
    """Get metadata for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file metadata or None if file doesn't exist
    """
    p = Path(file_path)
    if not p.exists():
        return None
    
    try:
        stat = p.stat()
        return {
            "path": str(p),
            "name": p.name,
            "size": stat.st_size,
            "size_human": format_file_size(stat.st_size),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "modified_human": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"Failed to get metadata for {file_path}: {e}")
        return None


def format_file_size(size_bytes):
    """Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


@routes_duplicates.route('/api/duplicates', methods=['GET'])
@require_auth
def get_duplicates():
    """Get all duplicate files grouped by hash.
    
    Returns:
        JSON response with duplicate groups:
        {
            "duplicates": [
                {
                    "hash": "abc123...",
                    "count": 3,
                    "total_size": 1048576,
                    "total_size_human": "1.0 MB",
                    "files": [
                        {
                            "path": "C:/Users/...",
                            "name": "file.jpg",
                            "size": 349525,
                            "size_human": "341.3 KB",
                            "modified": "2025-12-02T10:30:00",
                            "modified_human": "2025-12-02 10:30:00"
                        },
                        ...
                    ]
                },
                ...
            ],
            "total_duplicates": 5,
            "total_duplicate_files": 15,
            "wasted_space": 5242880,
            "wasted_space_human": "5.0 MB"
        }
    """
    try:
        # Feature gating via organizer_config.json
        cfg_path = ROOT / 'organizer_config.json'
        try:
            if cfg_path.exists():
                with cfg_path.open('r', encoding='utf-8') as f:
                    cfg = json.load(f)
                feats = cfg.get('features') or {}
                if feats.get('duplicates_enabled') is False:
                    return jsonify({"error": "Duplicate detection disabled"}), 400
        except Exception:
            pass
        hashes = load_file_hashes()
        
        # Find all hashes with multiple files (duplicates)
        duplicate_groups = []
        total_duplicate_files = 0
        wasted_space = 0
        
        for file_hash, file_paths in hashes.items():
            # Filter out non-existent files
            existing_files = [f for f in file_paths if Path(f).exists()]
            
            # Update hash database if files were removed
            if len(existing_files) != len(file_paths):
                hashes[file_hash] = existing_files
            
            # Only include groups with 2+ files (actual duplicates)
            if len(existing_files) >= 2:
                files_metadata = []
                group_size = 0
                
                for file_path in existing_files:
                    metadata = get_file_metadata(file_path)
                    if metadata:
                        files_metadata.append(metadata)
                        group_size += metadata["size"]
                
                if files_metadata:
                    # Sort files by modified time (newest first)
                    files_metadata.sort(key=lambda x: x["modified"], reverse=True)
                    
                    duplicate_groups.append({
                        "hash": file_hash,
                        "count": len(files_metadata),
                        "total_size": group_size,
                        "total_size_human": format_file_size(group_size),
                        "files": files_metadata
                    })
                    
                    total_duplicate_files += len(files_metadata)
                    # Wasted space = total size - size of one original
                    wasted_space += group_size - (group_size // len(files_metadata))
        
        # Save updated hashes (cleaned up non-existent files)
        save_file_hashes(hashes)
        
        # Sort duplicate groups by wasted space (highest first)
        duplicate_groups.sort(key=lambda x: x["total_size"], reverse=True)
        
        return jsonify({
            "duplicates": duplicate_groups,
            "total_duplicates": len(duplicate_groups),
            "total_duplicate_files": total_duplicate_files,
            "wasted_space": wasted_space,
            "wasted_space_human": format_file_size(wasted_space)
        })
        
    except Exception as e:
        logger.error(f"Error getting duplicates: {e}")
        return jsonify({"error": str(e)}), 500


@routes_duplicates.route('/api/duplicates/resolve', methods=['POST'])
@require_auth
def resolve_duplicates():
    """Resolve duplicates by deleting specified files.
    
    Request body:
        {
            "action": "delete",  // Currently only "delete" supported
            "files": ["C:/path/to/file1.jpg", "C:/path/to/file2.jpg"]
        }
    
    Returns:
        JSON response with results:
        {
            "success": true,
            "deleted": ["C:/path/to/file1.jpg"],
            "failed": [],
            "message": "Deleted 1 file(s)"
        }
    """
    try:
        # Feature gating via organizer_config.json
        cfg_path = ROOT / 'organizer_config.json'
        try:
            if cfg_path.exists():
                with cfg_path.open('r', encoding='utf-8') as f:
                    cfg = json.load(f)
                feats = cfg.get('features') or {}
                if feats.get('duplicates_enabled') is False:
                    return jsonify({"error": "Duplicate detection disabled"}), 400
        except Exception:
            pass
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        action = data.get("action")
        files_to_process = data.get("files", [])
        
        if not action or not files_to_process:
            return jsonify({"error": "Missing action or files"}), 400
        
        if action != "delete":
            return jsonify({"error": f"Unsupported action: {action}"}), 400
        
        deleted = []
        failed = []
        
        # Load hashes to update after deletion
        hashes = load_file_hashes()
        
        for file_path in files_to_process:
            try:
                p = Path(file_path)
                if p.exists():
                    p.unlink()
                    deleted.append(file_path)
                    logger.info(f"Deleted duplicate file: {file_path}")
                    
                    # Remove from hash database
                    for file_hash, paths in hashes.items():
                        if file_path in paths:
                            paths.remove(file_path)
                            # Remove hash entry if no files left
                            if not paths:
                                del hashes[file_hash]
                            break
                else:
                    failed.append({"file": file_path, "reason": "File not found"})
            except Exception as e:
                failed.append({"file": file_path, "reason": str(e)})
                logger.error(f"Failed to delete {file_path}: {e}")
        
        # Save updated hashes
        save_file_hashes(hashes)
        
        message = f"Deleted {len(deleted)} file(s)"
        if failed:
            message += f", {len(failed)} failed"
        
        return jsonify({
            "success": True,
            "deleted": deleted,
            "failed": failed,
            "message": message
        })
        
    except Exception as e:
        logger.error(f"Error resolving duplicates: {e}")
        return jsonify({"error": str(e)}), 500
