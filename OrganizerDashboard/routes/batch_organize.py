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
        from OrganizerDashboard.routes.api_recent_files import get_downloads_path
        from Organizer import organize_file, logger as organizer_logger
        
        data = request.get_json() or {}
        dry_run = data.get('dry_run', False)
        recursive = data.get('recursive', False)
        
        downloads_path = Path(get_downloads_path())
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
                    organize_file(str(file_path), downloads_path)
                    files_processed.append({
                        "file": str(file_path),
                        "status": "organized"
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
        op_index = None
        for i, op in enumerate(operations):
            if op.get('timestamp') == operation_id:
                operation = op
                op_index = i
                break
        
        if not operation:
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
