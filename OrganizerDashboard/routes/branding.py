from flask import Blueprint, request, jsonify
import json
import os
from OrganizerDashboard.auth.auth import requires_auth

routes_branding = Blueprint('routes_branding', __name__)

BRANDING_CONFIG_FILE = "dashboard_branding.json"

def load_branding():
    """Load branding configuration"""
    if os.path.exists(BRANDING_CONFIG_FILE):
        try:
            with open(BRANDING_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "title": "DownloadsOrganizeR",
        "logo": "",
        "color": "#0d6efd",
        "css": ""
    }

def save_branding(branding):
    """Save branding configuration"""
    try:
        with open(BRANDING_CONFIG_FILE, 'w') as f:
            json.dump(branding, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving branding: {e}")
        return False

@routes_branding.route("/api/dashboard/branding", methods=["GET"])
@requires_auth
def get_branding():
    """Get current branding configuration"""
    branding = load_branding()
    return jsonify(branding)

@routes_branding.route("/api/dashboard/branding", methods=["POST"])
@requires_auth
def update_branding():
    """Update branding configuration"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    branding = {
        "title": data.get("title", "DownloadsOrganizeR"),
        "logo": data.get("logo", ""),
        "color": data.get("color", "#0d6efd"),
        "css": data.get("css", "")
    }
    
    if save_branding(branding):
        return jsonify({"success": True, "branding": branding})
    else:
        return jsonify({"error": "Failed to save branding"}), 500
