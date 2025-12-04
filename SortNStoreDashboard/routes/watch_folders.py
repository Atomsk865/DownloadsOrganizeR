"""
watch_folders.py - Expose watched folders configured for Organizer service

GET /api/watch_folders -> { folders: ["C:/Users/.../Downloads", ...] }
"""
from flask import Blueprint, jsonify, request
from pathlib import Path
import json
import os
import sys
from importlib import import_module
from datetime import datetime

routes_watch_folders = Blueprint('routes_watch_folders', __name__)

SCRIPT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATHS = [SCRIPT_DIR / "organizer_config.json", Path("C:/Scripts/organizer_config.json")]


def load_config():
    cfg = {}
    for p in CONFIG_PATHS:
        if p.exists():
            try:
                with p.open("r", encoding="utf-8") as f:
                    cfg = json.load(f)
                break
            except Exception:
                cfg = {}
    return cfg

AUDIT_PATH = SCRIPT_DIR / 'config_actions.json'

def append_audit(entry: dict):
    try:
        record = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            **entry
        }
        data = []
        if AUDIT_PATH.exists():
            with AUDIT_PATH.open('r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = []
                except Exception:
                    data = []
        data.append(record)
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_PATH.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        # best-effort; ignore audit failures
        pass

@routes_watch_folders.route('/api/config_actions', methods=['GET'])
def get_config_actions():
    """Return recent configuration action audit entries."""
    try:
        actions = []
        if AUDIT_PATH.exists():
            with AUDIT_PATH.open('r', encoding='utf-8') as f:
                actions = json.load(f)
                if not isinstance(actions, list):
                    actions = []
        # Return last 50 entries (most recent last)
        return jsonify(actions[-50:])
    except Exception as e:
        return jsonify({ 'error': str(e) }), 500


@routes_watch_folders.route('/api/watch_folders', methods=['GET'])
def get_watch_folders():
    cfg = load_config()
    folders = []
    wf = cfg.get('watch_folders')
    if isinstance(wf, list) and wf:
        folders = wf
    else:
        # fallback to single watch_folder or env DOWNLOADS_PATH
        single = cfg.get('watch_folder') or os.environ.get('DOWNLOADS_PATH')
        if single:
            folders = [single]
    return jsonify({ 'folders': folders })


@routes_watch_folders.route('/api/watch_folders', methods=['POST'])
def set_watch_folders():
    """Update watch_folders in organizer_config.json.
    Body: { "folders": ["path1", "path2", ...] }
    """
    try:
        data = request.get_json() or {}
        folders = data.get('folders')
        if not isinstance(folders, list):
            return jsonify({ 'error': 'folders must be a list' }), 400
        # Server-side validation: simple absolute/UNC checks with feedback
        valid = []
        invalid = []
        for f in folders:
            if not isinstance(f, str):
                invalid.append(str(f))
                continue
            s = f.strip()
            # allow placeholders
            s_check = s.replace('%USERNAME%', 'user').replace('%USER%', 'user')
            # UNC path like \\server\share\folder
            is_unc = s_check.startswith('\\\\') and len(s_check.split('\\')) >= 4
            # Windows absolute path like C:/ or C:\
            is_win_abs = (len(s_check) > 2 and s_check[1] == ':' and (s_check[2] == '/' or s_check[2] == '\\'))
            # Linux/Unix absolute
            is_linux_abs = s_check.startswith('/')
            if is_unc or is_win_abs or is_linux_abs:
                valid.append(s)
            else:
                invalid.append(s)
        if not valid:
            return jsonify({ 'error': 'No valid folder paths provided', 'invalid': invalid }), 400
        cfg = load_config()
        cfg['watch_folders'] = valid
        # Persist to the first writable config path
        for p in CONFIG_PATHS:
            try:
                # Only write to a real file path; skip non-existent parent
                p.parent.mkdir(parents=True, exist_ok=True)
                with p.open('w', encoding='utf-8') as f:
                    json.dump(cfg, f, indent=4)
                return jsonify({ 'success': True, 'folders': valid, 'invalid': invalid })
            except Exception:
                continue
        return jsonify({ 'error': 'Failed to persist configuration' }), 500
    except Exception as e:
        return jsonify({ 'error': str(e) }), 500


@routes_watch_folders.route('/api/watch_folders/scan', methods=['POST'])
def scan_watch_folder():
    """Trigger an initial scan for a specific folder using Organizer's logic.
    Body: { "folder": "C:/Users/.../Downloads" }
    """
    try:
        data = request.get_json() or {}
        folder = (data.get('folder') or '').strip()
        if not folder:
            return jsonify({ 'error': 'folder is required' }), 400
        # Validate folder path exists
        p = Path(folder)
        if not p.exists() or not p.is_dir():
            return jsonify({ 'error': 'Folder does not exist or is not a directory' }), 400

        # Import Organizer module dynamically
        try:
            root_dir = Path(__file__).resolve().parents[2]
            sys.path.insert(0, str(root_dir))
            Organizer = import_module('Organizer')
        except Exception as e:
            return jsonify({ 'error': f'Failed to import Organizer: {e}' }), 500

        # Run initial scan using Organizer.initial_scan
        try:
            Organizer.initial_scan(p)
            return jsonify({ 'success': True, 'folder': folder })
        except Exception as e:
            return jsonify({ 'error': f'Initial scan failed: {e}' }), 500
    except Exception as e:
        return jsonify({ 'error': str(e) }), 500

@routes_watch_folders.route('/api/watch_folders/test', methods=['POST'])
def test_watch_folder():
    """Preflight check: verify folder exists and is accessible (read/list). Optional create if missing.
    Body: { "folder": "path", "create": false }
    """
    try:
        data = request.get_json() or {}
        folder = (data.get('folder') or '').strip()
        create = bool(data.get('create', False))
        if not folder:
            return jsonify({ 'error': 'folder is required' }), 400
        p = Path(folder)
        if not p.exists():
            if create:
                try:
                    p.mkdir(parents=True, exist_ok=True)
                    append_audit({'action': 'create_folder', 'folder': folder, 'result': 'success'})
                except Exception as e:
                    append_audit({'action': 'create_folder', 'folder': folder, 'result': f'error: {e}'})
                    return jsonify({ 'error': f'Failed to create folder: {e}' }), 500
            else:
                return jsonify({ 'exists': False, 'readable': False, 'writable': False, 'message': 'Folder does not exist' }), 200
        # Check readability (list) and writability (create temp file)
        readable = False
        writable = False
        try:
            _ = list(p.iterdir())
            readable = True
        except Exception:
            readable = False
        try:
            tmp = p / '.dor_perm_test.tmp'
            with tmp.open('w', encoding='utf-8') as f:
                f.write('ok')
            if tmp.exists():
                writable = True
                tmp.unlink(missing_ok=True)
        except Exception:
            writable = False
        return jsonify({ 'exists': True, 'readable': readable, 'writable': writable }), 200
    except Exception as e:
        return jsonify({ 'error': str(e) }), 500
