from flask import Blueprint, request, jsonify
import json
import os
from SortNStoreDashboard.auth.auth import requires_auth

routes_branding = Blueprint('routes_branding', __name__)

BRANDING_CONFIG_FILE = "dashboard_branding.json"

def load_branding():
    """Load branding configuration"""
    if os.path.exists(BRANDING_CONFIG_FILE):
        try:
            with open(BRANDING_CONFIG_FILE, 'r') as f:
                data = json.load(f)
                # Ensure timestamp exists for proper sync
                if 'timestamp' not in data:
                    data['timestamp'] = 0
                return data
        except Exception:
            pass
    return {
        "title": "DownloadsOrganizeR",
        "logo": "",
        "themeName": "Default",
        "colors": {
            "primary": "#0d6efd",
            "secondary": "#6c757d",
            "success": "#198754",
            "danger": "#dc3545",
            "warning": "#ffc107",
            "info": "#0dcaf0"
        },
        "borderRadius": "8px",
        "fontSize": "100%",
        "shadow": "normal",
        "css": "",
        "timestamp": 0
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
    import time
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Support both old and new branding format
    branding = {
        "title": data.get("title", "DownloadsOrganizeR"),
        "logo": data.get("logo", ""),
        "themeName": data.get("themeName", "Custom"),
        "colors": data.get("colors", {
            "primary": data.get("color", "#0d6efd"),  # Fallback for old format
            "secondary": "#6c757d",
            "success": "#198754",
            "danger": "#dc3545",
            "warning": "#ffc107",
            "info": "#0dcaf0"
        }),
        "borderRadius": data.get("borderRadius", "8px"),
        "fontSize": data.get("fontSize", "100%"),
        "shadow": data.get("shadow", "normal"),
        "css": data.get("css", ""),
        "timestamp": int(time.time() * 1000)  # Current timestamp in milliseconds
    }
    
    if save_branding(branding):
        return jsonify({"success": True, "branding": branding})
    else:
        return jsonify({"error": "Failed to save branding"}), 500
