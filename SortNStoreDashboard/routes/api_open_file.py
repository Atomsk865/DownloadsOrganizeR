from flask import Blueprint, jsonify, request
from SortNStoreDashboard.auth.auth import requires_auth
import os
import platform
import subprocess

routes_api_open_file = Blueprint('routes_api_open_file', __name__)

@routes_api_open_file.route("/api/open_file", methods=["POST"])
@requires_auth
def open_file():
    data = request.get_json()
    file_path = data.get("file_path")
    action = data.get("action", "open")
    if not file_path:
        return jsonify({"error": "No file path provided"}), 400
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    try:
        if platform.system() == "Windows":
            if action == "reveal":
                subprocess.run(["explorer", "/select,", file_path], check=False)
            else:
                subprocess.run(["cmd", "/c", "start", "", file_path], check=False, shell=True)
        elif platform.system() == "Darwin":
            if action == "reveal":
                subprocess.run(["open", "-R", file_path], check=False)
            else:
                subprocess.run(["open", file_path], check=False)
        else:
            if action == "reveal":
                parent_dir = os.path.dirname(file_path)
                subprocess.run(["xdg-open", parent_dir], check=False)
            else:
                subprocess.run(["xdg-open", file_path], check=False)
        return jsonify({"success": True, "message": f"File {'revealed' if action == 'reveal' else 'opened'}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
