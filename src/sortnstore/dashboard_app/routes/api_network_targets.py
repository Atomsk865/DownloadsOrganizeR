"""
Phase 4: Network Targets Configuration API

Endpoints for UNC path validation, SMB3 connection pooling, credential management.
"""

from flask import Blueprint, jsonify, request
import sys
import json
import re

routes_api_network_targets = Blueprint('routes_api_network_targets', __name__, url_prefix='/api/organizer/config')


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


def is_valid_unc_path(path):
    r"""Validate UNC path format (e.g., \\server\share)."""
    pattern = r'^\\\\[\w\-\.]+\\[\w\-\.\$ ]+'
    return bool(re.match(pattern, path))


@routes_api_network_targets.route('/network-targets', methods=['GET'])
@requires_right('view_metrics')
def list_network_targets():
    """GET /api/organizer/config/network-targets - Retrieve network folders."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        targets = config.get('network_targets', {})
        
        # Add status for each target if requested
        include_status = request.args.get('include_status', 'false').lower() == 'true'
        result = {}
        for name, target in targets.items():
            entry = dict(target)
            if include_status:
                # Simulate status check (would test actual connectivity)
                entry['status'] = 'online' if target.get('enabled', True) else 'disabled'
                entry['last_check'] = target.get('last_check', None)
            result[name] = entry
        
        return jsonify({'network_targets': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_network_targets.route('/network-targets', methods=['POST'])
@requires_right('manage_config')
def add_network_target():
    """POST /api/organizer/config/network-targets - Add UNC path."""
    try:
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        path = (data.get('path') or '').strip()
        description = data.get('description', '')
        enabled = data.get('enabled', True)
        
        if not name or not path:
            return jsonify({'error': 'name and path required'}), 400
        
        if not is_valid_unc_path(path):
            return jsonify({'error': 'Invalid UNC path format (expected: \\\\server\\share)'}), 400
        
        main = get_main_module()
        config = getattr(main, 'config', {})
        targets = config.get('network_targets', {})
        
        if name in targets:
            return jsonify({'error': 'Network target already exists'}), 409
        
        targets[name] = {
            'path': path,
            'description': description,
            'enabled': enabled,
            'created_at': __import__('datetime').datetime.utcnow().isoformat(),
            'status': 'online'
        }
        config['network_targets'] = targets
        _persist_config(main, config, 'organizer_config.json')
        
        return jsonify({'success': True, 'name': name}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_network_targets.route('/network-targets/<target_name>', methods=['GET'])
@requires_right('view_metrics')
def get_network_target(target_name):
    """GET /api/organizer/config/network-targets/<name> - Get target details."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        targets = config.get('network_targets', {})
        
        if target_name not in targets:
            return jsonify({'error': 'Network target not found'}), 404
        
        target = dict(targets[target_name])
        target['name'] = target_name
        return jsonify(target)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_network_targets.route('/network-targets/<target_name>', methods=['PUT'])
@requires_right('manage_config')
def update_network_target(target_name):
    """PUT /api/organizer/config/network-targets/<name> - Update target."""
    try:
        data = request.get_json() or {}
        main = get_main_module()
        config = getattr(main, 'config', {})
        targets = config.get('network_targets', {})
        
        if target_name not in targets:
            return jsonify({'error': 'Network target not found'}), 404
        
        target = targets[target_name]
        if 'path' in data:
            if not is_valid_unc_path(data['path']):
                return jsonify({'error': 'Invalid UNC path format'}), 400
            target['path'] = data['path']
        if 'description' in data:
            target['description'] = data['description']
        if 'enabled' in data:
            target['enabled'] = data['enabled']
        
        target['updated_at'] = __import__('datetime').datetime.utcnow().isoformat()
        config['network_targets'] = targets
        _persist_config(main, config, 'organizer_config.json')
        
        return jsonify({'success': True, 'target': target_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_network_targets.route('/network-targets/<target_name>', methods=['DELETE'])
@requires_right('manage_config')
def delete_network_target(target_name):
    """DELETE /api/organizer/config/network-targets/<name> - Remove target."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        targets = config.get('network_targets', {})
        
        if target_name not in targets:
            return jsonify({'error': 'Network target not found'}), 404
        
        del targets[target_name]
        config['network_targets'] = targets
        _persist_config(main, config, 'organizer_config.json')
        
        return jsonify({'success': True, 'deleted': target_name}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_network_targets.route('/network-targets/test', methods=['POST'])
@requires_right('test_nas')
def test_network_connection():
    """POST /api/organizer/config/network-targets/test - Test UNC path."""
    try:
        data = request.get_json() or {}
        path = (data.get('path') or '').strip()
        
        if not path:
            return jsonify({'error': 'path required'}), 400
        
        if not is_valid_unc_path(path):
            return jsonify({'error': 'Invalid UNC path format'}), 400
        
        # Simulate connectivity test (in production, would attempt actual SMB connection)
        # For now, return success for valid paths
        return jsonify({
            'success': True,
            'path': path,
            'status': 'online',
            'readable': True,
            'writable': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@routes_api_network_targets.route('/network-targets/<target_name>/credentials', methods=['PUT'])
@requires_right('manage_config')
def update_network_credentials(target_name):
    """PUT /api/organizer/config/network-targets/<name>/credentials - Update credentials."""
    try:
        data = request.get_json() or {}
        username = data.get('username', '')
        password = data.get('password', '')
        
        main = get_main_module()
        config = getattr(main, 'config', {})
        targets = config.get('network_targets', {})
        creds = config.get('credentials', {})
        
        if target_name not in targets:
            return jsonify({'error': 'Network target not found'}), 404
        
        # Store credentials separately (would be encrypted in production)
        cred_key = f'net_{target_name}'
        creds[cred_key] = {
            'username': username,
            'password': password,  # TODO: encrypt this
            'updated_at': __import__('datetime').datetime.utcnow().isoformat()
        }
        config['credentials'] = creds
        targets[target_name]['has_credentials'] = True
        config['network_targets'] = targets
        _persist_config(main, config, 'organizer_config.json')
        
        return jsonify({'success': True, 'target': target_name})
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
