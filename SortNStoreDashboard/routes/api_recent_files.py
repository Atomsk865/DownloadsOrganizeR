from flask import Blueprint, jsonify, request
from SortNStoreDashboard.auth.auth import requires_right
import os
import json
import hashlib
import requests
from pathlib import Path

routes_api_recent_files = Blueprint('routes_api_recent_files', __name__)

@routes_api_recent_files.route("/api/recent_files/test")
def test_route():
    """Simple test to verify blueprint is loaded"""
    return jsonify({"message": "Recent files blueprint is working"}), 200

@routes_api_recent_files.route("/api/recent_files")
@requires_right('view_recent_files')
def recent_files():
    import SortNStoreDashboard
    # Prefer organizer_config.json setting; default to repo-local config/json
    base = Path(__file__).resolve().parents[2]
    default_moves = base / 'config' / 'json' / 'file_moves.json'
    file_moves_path = OrganizerDashboard.config.get("file_moves_json", str(default_moves))
    try:
        if not os.path.exists(file_moves_path):
            return jsonify([])
        with open(file_moves_path, 'r', encoding='utf-8') as f:
            moves = json.load(f)
        return jsonify(moves[:20])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _load_organizer_config():
    try:
        base = Path(__file__).resolve().parents[2]
        cfg_path = base / 'organizer_config.json'
        if cfg_path.exists():
            with cfg_path.open('r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        return {}
    return {}

def _vt_cache_paths():
    base = Path(__file__).resolve().parents[2]
    cfg = _load_organizer_config()
    default_cache = base / 'config' / 'json' / 'vt_cache.json'
    path = cfg.get('vt_cache_json', str(default_cache))
    return Path(path)

def _vt_cache_get(sha256: str):
    try:
        cache_path = _vt_cache_paths()
        if cache_path.exists():
            with cache_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            entry = data.get(sha256)
            # TTL 24h
            if entry and (int(entry.get('timestamp', 0)) + 24*3600) > int(__import__('time').time()):
                return entry.get('response')
    except Exception:
        pass
    return None

def _vt_cache_set(sha256: str, response: dict):
    try:
        cache_path = _vt_cache_paths()
        cache = {}
        if cache_path.exists():
            with cache_path.open('r', encoding='utf-8') as f:
                cache = json.load(f)
        cache[sha256] = {
            'timestamp': int(__import__('time').time()),
            'response': response
        }
        with cache_path.open('w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
    except Exception:
        # Fail silently; caching is optional
        pass

def _sha256_file(path: str) -> str:
    try:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ''

@routes_api_recent_files.route("/api/recent_files/virustotal", methods=["POST"])
@requires_right('view_recent_files')
def virustotal_scan():
    """Query VirusTotal for a file by SHA256 hash or path.
    Body: { "path": "C:/.../file.ext" } or { "sha256": "..." }
    Requires organizer_config.json key: "virustotal_api_key"
    """
    data = request.get_json() or {}
    path = data.get('path')
    sha256 = data.get('sha256')
    cfg = _load_organizer_config()
    # Feature gating
    feats = cfg.get('features') or {}
    if feats.get('virustotal_enabled') is False:
        return jsonify({"error": "VirusTotal integration disabled"}), 400
    api_key = cfg.get('vt_api_key') or cfg.get('virustotal_api_key')
    if not api_key:
        return jsonify({"error": "VirusTotal API key not configured"}), 400
    if not sha256 and path:
        if not os.path.exists(path):
            return jsonify({"error": "File not found"}), 404
        sha256 = _sha256_file(path)
    if not sha256:
        return jsonify({"error": "No sha256 or valid path provided"}), 400
    # Use cache first
    cached = _vt_cache_get(sha256)
    if cached:
        return jsonify({"cached": True, **cached})
    try:
        # VT v3 API: get file report by hash
        url = f"https://www.virustotal.com/api/v3/files/{sha256}"
        headers = {"x-apikey": api_key}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            _vt_cache_set(sha256, result)
            return jsonify(result)
        else:
            # Pass through minimal error
            return jsonify({"status": resp.status_code, "error": resp.text[:500]}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_api_recent_files.route("/api/recent_files/<int:index>", methods=["DELETE"])
@requires_right('view_recent_files')
def remove_recent_file(index):
    import SortNStoreDashboard
    base = Path(__file__).resolve().parents[2]
    default_moves = base / 'config' / 'json' / 'file_moves.json'
    file_moves_path = OrganizerDashboard.config.get("file_moves_json", str(default_moves))
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
