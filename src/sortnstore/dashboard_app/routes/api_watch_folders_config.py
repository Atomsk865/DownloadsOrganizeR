"""
Phase 4: Watched Folders Configuration API

Endpoints for multi-path monitoring, placeholder resolution, batch folder tests.
"""

from flask import Blueprint, jsonify, request
import sys
import json
import re
import os

routes_api_watch_folders = Blueprint('routes_api_watch_folders', __name__, url_prefix='/api/organizer/config')


def get_main_module():
    """Get the main dashboard module."""
    return sys.modules.get('__main__') or sys.modules.get('SortNStoreDashboard')


def requires_right(right_name):
    """Decorator: check user has required right."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            from flask_login import current_user
            from SortNStoreDashboard.auth.auth import check_auth
            
            auth = request.authorization
            is_authenticated = getattr(current_user, 'is_authenticated', False)
            is_admin = getattr(current_user, 'role', None) == 'admin'
            
            if not is_authenticated:
                if auth:
                    if check_auth(str(auth.username), str(auth.password)):
                        is_authenticated = True
                        main = get_main_module()
                        dash_cfg = getattr(main, 'dashboard_config', {})
                        for u in dash_cfg.get('users', []):
                            if u.get('username') == auth.username:
                                is_admin = u.get('role') == 'admin'
                                break
                else:
                    return jsonify({'error': 'Unauthorized'}), 401
            
            if not is_authenticated:
                return jsonify({'error': 'Unauthorized'}), 401
            
            if right_name != 'view_metrics' and not is_admin:
                return jsonify({'error': 'Forbidden'}), 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


def resolve_placeholders(path):
    """Resolve placeholders like %USERNAME%, %USER% in paths."""
    path = str(path)
    # Replace common placeholders
    path = path.replace('%USERNAME%', os.environ.get('USERNAME', os.environ.get('USER', 'user')))
    path = path.replace('%USER%', os.environ.get('USER', os.environ.get('USERNAME', 'user')))
    path = path.replace('%USERPROFILE%', os.environ.get('USERPROFILE', os.path.expanduser('~')))
    path = path.replace('%HOME%', os.path.expanduser('~'))
    return path


def test_folder_access(path):
    """Test if folder is readable and writable."""
    try:
        resolved = resolve_placeholders(path)
        # Normalize path
        resolved = os.path.abspath(resolved)
        
        readable = os.path.isdir(resolved) and os.access(resolved, os.R_OK)
        writable = os.path.isdir(resolved) and os.access(resolved, os.W_OK)
        
        return {
            'readable': readable,
            'writable': writable,
            'exists': os.path.isdir(resolved),
            'resolved_path': resolved
        }
    except Exception as e:
        return {
            'readable': False,
            'writable': False,
            'exists': False,
            'error': str(e)
        }


@routes_api_watch_folders.route('/folders', methods=['GET'])
@requires_right('view_metrics')
def list_watch_folders():
    """GET /api/organizer/config/folders - Retrieve monitored folders."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        folders = config.get('watched_folders', [])
        
        result = []
        for folder in folders:
            entry = dict(folder)
            # Test access
            access = test_folder_access(folder.get('path', ''))
            entry['access_test'] = access
            result.append(entry)
        
        return jsonify({'watched_folders': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_watch_folders.route('/folders', methods=['POST'])
@requires_right('manage_config')
def add_watch_folder():
    """POST /api/organizer/config/folders - Add monitored folder."""
    try:
        data = request.get_json() or {}
        path = (data.get('path') or '').strip()
        name = data.get('name', '')
        enabled = data.get('enabled', True)
        recursive = data.get('recursive', True)
        
        if not path:
            return jsonify({'error': 'path required'}), 400
        
        main = get_main_module()
        config = getattr(main, 'config', {})
        folders = config.get('watched_folders', [])
        
        # Check for duplicates
        for f in folders:
            if f.get('path') == path:
                return jsonify({'error': 'Folder already being monitored'}), 409
        
        # Test access
        access = test_folder_access(path)
        
        if not name:
            name = os.path.basename(resolve_placeholders(path)) or 'Folder'
        
        new_folder = {
            'path': path,
            'name': name,
            'enabled': enabled,
            'recursive': recursive,
            'created_at': __import__('datetime').datetime.utcnow().isoformat(),
            'last_check': __import__('datetime').datetime.utcnow().isoformat(),
            'access_test': access
        }
        
        folders.append(new_folder)
        config['watched_folders'] = folders
        _persist_config(main, config, 'organizer_config.json')
        
        return jsonify({'success': True, 'folder': name, 'access': access}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_watch_folders.route('/folders/<int:folder_id>', methods=['GET'])
@requires_right('view_metrics')
def get_watch_folder(folder_id):
    """GET /api/organizer/config/folders/<id> - Get folder details."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        folders = config.get('watched_folders', [])
        
        if folder_id < 0 or folder_id >= len(folders):
            return jsonify({'error': 'Folder not found'}), 404
        
        folder = dict(folders[folder_id])
        access = test_folder_access(folder.get('path', ''))
        folder['access_test'] = access
        folder['id'] = folder_id
        
        return jsonify(folder)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_watch_folders.route('/folders/<int:folder_id>', methods=['PUT'])
@requires_right('manage_config')
def update_watch_folder(folder_id):
    """PUT /api/organizer/config/folders/<id> - Update folder settings."""
    try:
        data = request.get_json() or {}
        main = get_main_module()
        config = getattr(main, 'config', {})
        folders = config.get('watched_folders', [])
        
        if folder_id < 0 or folder_id >= len(folders):
            return jsonify({'error': 'Folder not found'}), 404
        
        folder = folders[folder_id]
        
        if 'path' in data:
            folder['path'] = data['path']
        if 'name' in data:
            folder['name'] = data['name']
        if 'enabled' in data:
            folder['enabled'] = data['enabled']
        if 'recursive' in data:
            folder['recursive'] = data['recursive']
        
        folder['updated_at'] = __import__('datetime').datetime.utcnow().isoformat()
        config['watched_folders'] = folders
        _persist_config(main, config, 'organizer_config.json')
        
        return jsonify({'success': True, 'folder_id': folder_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_watch_folders.route('/folders/<int:folder_id>', methods=['DELETE'])
@requires_right('manage_config')
def delete_watch_folder(folder_id):
    """DELETE /api/organizer/config/folders/<id> - Remove folder from monitoring."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        folders = config.get('watched_folders', [])
        
        if folder_id < 0 or folder_id >= len(folders):
            return jsonify({'error': 'Folder not found'}), 404
        
        removed = folders.pop(folder_id)
        config['watched_folders'] = folders
        _persist_config(main, config, 'organizer_config.json')
        
        return jsonify({'success': True, 'deleted': removed.get('name')}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_watch_folders.route('/folders/test', methods=['POST'])
@requires_right('test_nas')
def test_watch_folders():
    """POST /api/organizer/config/folders/test - Test folder access."""
    try:
        data = request.get_json() or {}
        path = (data.get('path') or '').strip()
        
        if not path:
            return jsonify({'error': 'path required'}), 400
        
        access = test_folder_access(path)
        
        return jsonify({
            'success': access['exists'],
            'path': path,
            'access': access
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@routes_api_watch_folders.route('/folders/test-all', methods=['POST'])
@requires_right('test_nas')
def batch_test_watch_folders():
    """POST /api/organizer/config/folders/test-all - Test all folders."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        folders = config.get('watched_folders', [])
        
        results = []
        for idx, folder in enumerate(folders):
            path = folder.get('path', '')
            access = test_folder_access(path)
            results.append({
                'id': idx,
                'name': folder.get('name', path),
                'path': path,
                'access': access
            })
        
        # Update last_check timestamps
        for folder in folders:
            folder['last_check'] = __import__('datetime').datetime.utcnow().isoformat()
        config['watched_folders'] = folders
        _persist_config(main, config, 'organizer_config.json')
        
        return jsonify({
            'success': True,
            'tested': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@routes_api_watch_folders.route('/folders/audit-log', methods=['GET'])
@requires_right('view_metrics')
def get_watch_folders_audit():
    """GET /api/organizer/config/watch-folders/audit-log - Get audit trail."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        audit = config.get('watch_folders_audit', [])
        
        # Return latest 50 audit entries
        return jsonify({
            'audit_log': audit[-50:],
            'total_entries': len(audit)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _persist_config(main, config_dict, filename):
    """Helper: persist config to file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        setattr(main, 'config', config_dict)
    except Exception:
        pass
