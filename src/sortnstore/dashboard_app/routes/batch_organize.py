"""
Batch organization and file history tracking

Provides endpoints for:
- Batch organize existing Downloads files
- Track file organization history
- Undo last organization (rollback file moves)
- Get organization statistics
"""

from flask import Blueprint, jsonify, request
from pathlib import Path
import json
import shutil
from datetime import datetime
import logging

batch_organize_bp = Blueprint('batch_organize', __name__)
logger = logging.getLogger(__name__)

# File history tracking
FILE_HISTORY_PATH = Path(__file__).parent.parent.parent / 'config' / 'json' / 'file_organization_history.json'
BATCH_HISTORY_PATH = Path(__file__).parent.parent.parent / 'config' / 'json' / 'batch_operations.json'


def ensure_history_file():
    """Ensure history JSON file exists"""
    FILE_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not FILE_HISTORY_PATH.exists():
        FILE_HISTORY_PATH.write_text(json.dumps({"operations": []}))


def load_history():
    """Load file operation history"""
    ensure_history_file()
    try:
        return json.loads(FILE_HISTORY_PATH.read_text())
    except:
        return {"operations": []}


def save_history(data):
    """Save file operation history"""
    ensure_history_file()
    FILE_HISTORY_PATH.write_text(json.dumps(data, indent=2))


def record_move(source, destination, category, batch_id=None):
    """Record a file move operation"""
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
    return operation


@batch_organize_bp.route('/api/batch-organize', methods=['POST'])
def batch_organize_downloads():
    """
    Batch organize all files in Downloads folder
    
    Request body:
    {
        "dry_run": false,  // Preview changes without moving
        "recursive": false // Include subdirectories
    }
    """
    try:
        from pathlib import Path
        import os
        
        data = request.get_json() or {}
        dry_run = data.get('dry_run', False)
        recursive = data.get('recursive', False)
        
        # Get downloads path the same way Organizer.py does
        try:
            username = os.environ.get("USERNAME") or os.getlogin()
        except Exception:
            username = ""
        
        if username:
            downloads_path = Path(f"C:\\Users\\{username}\\Downloads")
        else:
            downloads_path = Path.home() / "Downloads"
        
        if not downloads_path.exists():
            return jsonify({"success": False, "error": "Downloads folder not found"}), 400
        
        batch_id = datetime.now().isoformat()
        files_processed = []
        errors = []
        
        # Find all files
        if recursive:
            files = list(downloads_path.rglob('*'))
        else:
            files = list(downloads_path.glob('*'))
        
        # Filter to only files (not directories)
        files = [f for f in files if f.is_file()]
        
        logger.info(f"Batch organize: Found {len(files)} files, dry_run={dry_run}")
        
        for file_path in files:
            try:
                if dry_run:
                    # Just record what would happen
                    ext = file_path.suffix.lower()
                    category = "Other"  # Would need to check against EXTENSION_MAP
                    files_processed.append({
                        "file": str(file_path),
                        "status": "would_organize",
                        "category": category
                    })
                else:
                    # Actually organize the file
                    from Organizer import organize_file
                    destination, category = organize_file(str(file_path), downloads_path)
                    
                    if destination and category:
                        # Record the move in batch history
                        record_move(str(file_path), destination, category, batch_id)
                        files_processed.append({
                            "file": str(file_path),
                            "status": "organized",
                            "destination": destination,
                            "category": category
                        })
                    else:
                        # File was skipped (incomplete download, ignored file, etc.)
                        files_processed.append({
                            "file": str(file_path),
                            "status": "skipped"
                        })
            except Exception as e:
                logger.error(f"Error organizing {file_path}: {e}")
                errors.append({
                    "file": str(file_path),
                    "error": str(e)
                })
        
        return jsonify({
            "success": True,
            "batch_id": batch_id,
            "dry_run": dry_run,
            "files_processed": len(files_processed),
            "errors": len(errors),
            "operations": files_processed,
            "error_details": errors if errors else None
        }), 200
        
    except Exception as e:
        logger.error(f"Batch organize error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@batch_organize_bp.route('/api/file-history', methods=['GET'])
def get_file_history():
    """Get file organization history"""
    try:
        history = load_history()
        
        # Get query parameters for filtering
        limit = request.args.get('limit', 100, type=int)
        category = request.args.get('category')
        batch_id = request.args.get('batch_id')
        
        operations = history.get('operations', [])
        
        # Filter by category if specified
        if category:
            operations = [op for op in operations if op.get('category') == category]
        
        # Filter by batch_id if specified
        if batch_id:
            operations = [op for op in operations if op.get('batch_id') == batch_id]
        
        # Return most recent first, limited
        operations = sorted(operations, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
        return jsonify({
            "success": True,
            "total": len(history.get('operations', [])),
            "returned": len(operations),
            "operations": operations
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting file history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@batch_organize_bp.route('/api/file-history/undo/<operation_id>', methods=['POST'])
def undo_operation(operation_id):
    """
    Undo a file move operation (move file back to original location)
    """
    try:
        history = load_history()
        operations = history.get('operations', [])
        
        # Find the operation
        operation = None
        op_index = -1
        for i, op in enumerate(operations):
            if op.get('timestamp') == operation_id:
                operation = op
                op_index = i
                break
        
        if not operation or op_index < 0:
            return jsonify({"success": False, "error": "Operation not found"}), 404
        
        source = Path(operation['source'])
        destination = Path(operation['destination'])
        
        # Check if file exists at destination
        if not destination.exists():
            return jsonify({
                "success": False,
                "error": f"File not found at {destination}. Cannot undo operation."
            }), 400
        
        # Move file back to original location
        source.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(destination), str(source))
        
        # Update operation status
        operation['status'] = 'undone'
        operation['undo_timestamp'] = datetime.now().isoformat()
        if op_index >= 0:
            operations[op_index] = operation
        history['operations'] = operations
        save_history(history)
        
        logger.info(f"Undone operation: {destination} → {source}")
        
        return jsonify({
            "success": True,
            "message": f"Moved {destination.name} back to {source}",
            "operation": operation
        }), 200
        
    except Exception as e:
        logger.error(f"Error undoing operation: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@batch_organize_bp.route('/api/file-history/stats', methods=['GET'])
def get_organization_stats():
    """Get organization statistics"""
    try:
        history = load_history()
        operations = history.get('operations', [])
        
        # Calculate stats
        total_operations = len(operations)
        completed = len([op for op in operations if op.get('status') == 'completed'])
        undone = len([op for op in operations if op.get('status') == 'undone'])
        
        # Group by category
        categories = {}
        for op in operations:
            if op.get('status') == 'completed':
                cat = op.get('category', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1
        
        # Get today's operations
        today = datetime.now().date().isoformat()
        today_ops = len([
            op for op in operations 
            if op.get('timestamp', '').startswith(today) and op.get('status') == 'completed'
        ])
        
        return jsonify({
            "success": True,
            "total_operations": total_operations,
            "completed": completed,
            "undone": undone,
            "by_category": categories,
            "today": today_ops,
            "today_date": today
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# Watch Folder Management Endpoints
# ============================================================================

BATCH_CONFIG_PATH = Path(__file__).parent.parent.parent / 'batch_organizer_config.json'


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
    except:
        return {"watch_folders": [str(Path.home() / "Downloads")]}


def save_batch_config(config):
    """Save batch organizer configuration"""
    try:
        BATCH_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        BATCH_CONFIG_PATH.write_text(json.dumps(config, indent=2))
    except Exception as e:
        logger.error(f"Failed to save batch config: {e}")


@batch_organize_bp.route('/api/batch-config/watch-folders', methods=['GET'])
def get_watch_folders():
    """Get list of configured watch folders"""
    try:
        config = load_batch_config()
        folders = config.get("watch_folders", [])
        return jsonify({
            "success": True,
            "watch_folders": folders,
            "count": len(folders)
        }), 200
    except Exception as e:
        logger.error(f"Error getting watch folders: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@batch_organize_bp.route('/api/batch-config/watch-folders', methods=['POST'])
def add_watch_folder():
    """Add a folder to watch list"""
    try:
        data = request.get_json() or {}
        folder_path = data.get("path", "").strip()
        
        if not folder_path:
            return jsonify({"success": False, "error": "Folder path required"}), 400
        
        folder_path = str(Path(folder_path).absolute())
        
        if not Path(folder_path).exists():
            return jsonify({"success": False, "error": "Folder does not exist"}), 400
        
        config = load_batch_config()
        
        if folder_path in config.get("watch_folders", []):
            return jsonify({"success": False, "error": "Folder already in watch list"}), 400
        
        config["watch_folders"].append(folder_path)
        save_batch_config(config)
        
        logger.info(f"Added watch folder: {folder_path}")
        return jsonify({
            "success": True,
            "message": f"Added {folder_path}",
            "watch_folders": config["watch_folders"]
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding watch folder: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@batch_organize_bp.route('/api/batch-config/watch-folders/<path:folder_path>', methods=['DELETE'])
def remove_watch_folder(folder_path):
    """Remove a folder from watch list"""
    try:
        folder_path = str(Path(folder_path).absolute())
        
        config = load_batch_config()
        
        if folder_path not in config.get("watch_folders", []):
            return jsonify({"success": False, "error": "Folder not in watch list"}), 404
        
        config["watch_folders"].remove(folder_path)
        save_batch_config(config)
        
        logger.info(f"Removed watch folder: {folder_path}")
        return jsonify({
            "success": True,
            "message": f"Removed {folder_path}",
            "watch_folders": config["watch_folders"]
        }), 200
        
    except Exception as e:
        logger.error(f"Error removing watch folder: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@batch_organize_bp.route('/api/batch-config/watch-folders/organize', methods=['POST'])
def organize_all_watch_folders():
    """Organize all configured watch folders"""
    try:
        data = request.get_json() or {}
        dry_run = data.get("dry_run", False)
        
        config = load_batch_config()
        folders = config.get("watch_folders", [])
        
        if not folders:
            return jsonify({"success": False, "error": "No watch folders configured"}), 400
        
        batch_id = datetime.now().isoformat()
        total_results = {
            "success": True,
            "batch_id": batch_id,
            "dry_run": dry_run,
            "folders": [],
            "total_organized": 0,
            "total_skipped": 0,
            "total_errors": 0
        }
        
        # Organize each folder
        for folder in folders:
            folder_path = Path(folder)
            if not folder_path.exists():
                logger.warning(f"Watch folder does not exist: {folder}")
                continue
            
            try:
                # Use the same logic as batch_organize_downloads
                if folder_path.is_dir():
                    files = list(folder_path.glob('*'))
                    files = [f for f in files if f.is_file()]
                    
                    folder_result = {
                        "folder": str(folder),
                        "organized": 0,
                        "skipped": 0,
                        "operations": []
                    }
                    
                    for file_path in files:
                        try:
                            if not dry_run:
                                from Organizer import organize_file
                                destination, category = organize_file(str(file_path), folder_path)
                                
                                if destination and category:
                                    record_move(str(file_path), destination, category, batch_id)
                                    folder_result["organized"] += 1
                                    folder_result["operations"].append({
                                        "file": file_path.name,
                                        "destination": destination,
                                        "category": category
                                    })
                                else:
                                    folder_result["skipped"] += 1
                            else:
                                folder_result["organized"] += 1
                        except Exception as e:
                            logger.error(f"Error organizing {file_path}: {e}")
                            folder_result["skipped"] += 1
                    
                    total_results["folders"].append(folder_result)
                    total_results["total_organized"] += folder_result["organized"]
                    total_results["total_skipped"] += folder_result["skipped"]
                    
            except Exception as e:
                logger.error(f"Error processing folder {folder}: {e}")
                total_results["total_errors"] += 1
        
        return jsonify(total_results), 200
        
    except Exception as e:
        logger.error(f"Error organizing watch folders: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@batch_organize_bp.route('/api/batch-config/browse-folders', methods=['GET'])
def browse_folders():
    """List server-side subfolders for a given path (or default Downloads)."""
    try:
        requested_path = (request.args.get('path') or '').strip()

        # Default to Downloads if no path provided
        if not requested_path:
            base_path = Path.home() / "Downloads"
        else:
            # Allow UNC or absolute paths; Path will handle platform specifics
            base_path = Path(requested_path)

        if not base_path.exists() or not base_path.is_dir():
            return jsonify({"success": False, "error": "Folder not found"}), 400

        folders = []
        for child in base_path.iterdir():
            if child.is_dir():
                folders.append({"name": child.name, "path": str(child)})

        return jsonify({
            "success": True,
            "base": str(base_path),
            "count": len(folders),
            "folders": folders
        }), 200

    except Exception as e:
        logger.error(f"Error browsing folders: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
