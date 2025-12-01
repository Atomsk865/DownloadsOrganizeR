from flask import Blueprint, jsonify
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
