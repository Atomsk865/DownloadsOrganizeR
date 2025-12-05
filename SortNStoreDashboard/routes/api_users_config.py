"""
Phase 4: Users & Roles Configuration API

Endpoints for user lifecycle management, role-based rights, LDAP/AD hooks.
"""

from flask import Blueprint, jsonify, request
import sys
import bcrypt
import json

routes_api_users = Blueprint('routes_api_users', __name__, url_prefix='/api/organizer/config')


def get_main_module():
    """Get the main dashboard module."""
    return sys.modules.get('__main__') or sys.modules.get('SortNStoreDashboard')


def requires_right(right_name):
    """Decorator: check user has required right."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            from flask_login import current_user
            from SortNStoreDashboard.auth.auth import check_auth
            
            # Check Flask-Login or Basic Auth
            auth = request.authorization
            is_authenticated = getattr(current_user, 'is_authenticated', False)
            is_admin = getattr(current_user, 'role', None) == 'admin'
            
            if not is_authenticated:
                if auth:
                    if check_auth(str(auth.username), str(auth.password)):
                        is_authenticated = True
                        # Try to load user role from dashboard config
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
            
            # For now, only admins can modify config
            if right_name != 'view_metrics' and not is_admin:
                return jsonify({'error': 'Forbidden'}), 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


@routes_api_users.route('/users', methods=['GET'])
@requires_right('view_metrics')
def list_users():
    """GET /api/organizer/config/users - Retrieve all users."""
    try:
        main = get_main_module()
        dash_cfg = getattr(main, 'dashboard_config', {})
        users = []
        for u in dash_cfg.get('users', []):
            sanitized = {k: v for k, v in u.items() if k != 'password_hash'}
            sanitized['has_password'] = 'password_hash' in u and bool(u['password_hash'])
            users.append(sanitized)
        return jsonify({'users': users, 'count': len(users)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_users.route('/users', methods=['POST'])
@requires_right('manage_config')
def create_user():
    """POST /api/organizer/config/users - Add a new user."""
    try:
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip()
        roles = data.get('roles', ['viewer'])
        source = data.get('source', 'local')
        password = data.get('password')
        
        if not username:
            return jsonify({'error': 'username required'}), 400
        
        main = get_main_module()
        dash_cfg = getattr(main, 'dashboard_config', {})
        users = dash_cfg.get('users', [])
        
        # Check for duplicates
        for u in users:
            if u.get('username') == username:
                return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        new_user = {
            'username': username,
            'email': email,
            'roles': roles if isinstance(roles, list) else [roles],
            'source': source,
            'created_at': __import__('datetime').datetime.utcnow().isoformat()
        }
        if password:
            pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_user['password_hash'] = pw_hash
        
        users.append(new_user)
        dash_cfg['users'] = users
        _persist_config(main, dash_cfg, 'dashboard_config.json')
        
        return jsonify({'success': True, 'user': username}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_users.route('/users/<username>', methods=['GET'])
@requires_right('view_metrics')
def get_user(username):
    """GET /api/organizer/config/users/<username> - Get user details."""
    try:
        main = get_main_module()
        dash_cfg = getattr(main, 'dashboard_config', {})
        for u in dash_cfg.get('users', []):
            if u.get('username') == username:
                sanitized = {k: v for k, v in u.items() if k != 'password_hash'}
                sanitized['has_password'] = 'password_hash' in u and bool(u['password_hash'])
                return jsonify(sanitized)
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_users.route('/users/<username>', methods=['PUT'])
@requires_right('manage_config')
def update_user(username):
    """PUT /api/organizer/config/users/<username> - Update user."""
    try:
        data = request.get_json() or {}
        main = get_main_module()
        dash_cfg = getattr(main, 'dashboard_config', {})
        users = dash_cfg.get('users', [])
        
        user = None
        for u in users:
            if u.get('username') == username:
                user = u
                break
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent changing primary admin role
        if username == getattr(main, 'ADMIN_USER', 'admin'):
            if 'roles' in data and 'admin' not in data.get('roles', []):
                return jsonify({'error': 'Cannot remove admin role from primary admin'}), 400
        
        if 'email' in data:
            user['email'] = data['email']
        if 'roles' in data:
            user['roles'] = data['roles']
        if 'password' in data and data['password']:
            pw_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user['password_hash'] = pw_hash
        
        user['updated_at'] = __import__('datetime').datetime.utcnow().isoformat()
        dash_cfg['users'] = users
        _persist_config(main, dash_cfg, 'dashboard_config.json')
        
        return jsonify({'success': True, 'user': username})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_users.route('/users/<username>', methods=['DELETE'])
@requires_right('manage_config')
def delete_user(username):
    """DELETE /api/organizer/config/users/<username> - Remove user."""
    try:
        main = get_main_module()
        dash_cfg = getattr(main, 'dashboard_config', {})
        users = dash_cfg.get('users', [])
        
        # Prevent deleting primary admin
        if username == getattr(main, 'ADMIN_USER', 'admin'):
            return jsonify({'error': 'Cannot delete primary admin user'}), 400
        
        original_len = len(users)
        users = [u for u in users if u.get('username') != username]
        
        if len(users) == original_len:
            return jsonify({'error': 'User not found'}), 404
        
        dash_cfg['users'] = users
        _persist_config(main, dash_cfg, 'dashboard_config.json')
        
        return jsonify({'success': True, 'deleted': username}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_users.route('/roles', methods=['GET'])
@requires_right('view_metrics')
def list_roles():
    """GET /api/organizer/config/roles - List all available roles."""
    try:
        main = get_main_module()
        dash_cfg = getattr(main, 'dashboard_config', {})
        roles = dash_cfg.get('roles', {})
        return jsonify({'roles': roles, 'count': len(roles)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_users.route('/roles/<role>', methods=['GET'])
@requires_right('view_metrics')
def get_role(role):
    """GET /api/organizer/config/roles/<role> - Get role details."""
    try:
        main = get_main_module()
        dash_cfg = getattr(main, 'dashboard_config', {})
        roles = dash_cfg.get('roles', {})
        
        if role not in roles:
            return jsonify({'error': 'Role not found'}), 404
        
        return jsonify({'name': role, 'permissions': roles[role]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_users.route('/roles/<role>', methods=['PUT'])
@requires_right('manage_config')
def update_role(role):
    """PUT /api/organizer/config/roles/<role> - Update role permissions."""
    try:
        data = request.get_json() or {}
        main = get_main_module()
        dash_cfg = getattr(main, 'dashboard_config', {})
        roles = dash_cfg.get('roles', {})
        
        if role not in roles:
            return jsonify({'error': 'Role not found'}), 404
        
        # Prevent removing all rights from admin role
        if role == 'admin' and not any(data.get(k, False) for k in data.keys()):
            return jsonify({'error': 'Admin role must have at least one right'}), 400
        
        for perm in data:
            if perm in roles[role]:
                roles[role][perm] = data[perm]
        
        dash_cfg['roles'] = roles
        _persist_config(main, dash_cfg, 'dashboard_config.json')
        
        return jsonify({'success': True, 'role': role, 'permissions': roles[role]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _persist_config(main, config_dict, filename):
    """Helper: persist config to file."""
    try:
        import os
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        # Update module attribute
        setattr(main, 'dashboard_config', config_dict)
    except Exception:
        pass
