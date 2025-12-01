from flask import Blueprint, jsonify, request
from OrganizerDashboard.auth.auth import requires_right
import os
import json

routes_api_recent_files = Blueprint('routes_api_recent_files', __name__)

@routes_api_recent_files.route("/api/recent_files")
@requires_right('view_recent_files')
def recent_files():
    import OrganizerDashboard
    file_moves_path = OrganizerDashboard.config.get("file_moves_json", "C:/Scripts/file_moves.json")
    try:
        if not os.path.exists(file_moves_path):
            return jsonify([])
        with open(file_moves_path, 'r', encoding='utf-8') as f:
            moves = json.load(f)
        return jsonify(moves[:20])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_api_recent_files.route("/api/recent_files/<int:index>", methods=["DELETE"])
@requires_right('view_recent_files')
def remove_recent_file(index):
    import OrganizerDashboard
    file_moves_path = OrganizerDashboard.config.get("file_moves_json", "C:/Scripts/file_moves.json")
    try:
        if not os.path.exists(file_moves_path):
            return jsonify({"error": "File moves log not found"}), 404
        
        with open(file_moves_path, 'r', encoding='utf-8') as f:
            moves = json.load(f)
        
        if index < 0 or index >= len(moves):
            return jsonify({"error": "Invalid index"}), 400
        
        # Remove the entry at the specified index
        removed = moves.pop(index)
        
        # Write back to file
        with open(file_moves_path, 'w', encoding='utf-8') as f:
            json.dump(moves, f, indent=2)
        
        return jsonify({"success": True, "removed": removed}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
