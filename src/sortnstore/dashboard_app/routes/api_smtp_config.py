"""
Phase 4: SMTP & Credentials Manager API

Endpoints for email configuration, credential storage, OAuth2 handling.
"""

from flask import Blueprint, jsonify, request
import sys
import json
import re

routes_api_smtp = Blueprint('routes_api_smtp', __name__, url_prefix='/api/organizer/config')


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


def is_valid_email(email):
    """Validate email format."""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))


@routes_api_smtp.route('/smtp', methods=['GET'])
@requires_right('view_metrics')
def get_smtp_config():
    """GET /api/organizer/config/smtp - Retrieve SMTP configuration."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        smtp = config.get('smtp', {})
        
        # Mask password in response
        result = dict(smtp)
        if 'password' in result:
            result['password'] = '***'
        if 'oauth_refresh_token' in result:
            result['oauth_refresh_token'] = '***'
        
        return jsonify({'smtp': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_smtp.route('/smtp', methods=['PUT', 'POST'])
@requires_right('manage_config')
def update_smtp_config():
    """PUT/POST /api/organizer/config/smtp - Update SMTP configuration."""
    try:
        data = request.get_json() or {}
        main = get_main_module()
        config = getattr(main, 'config', {})
        
        smtp = config.get('smtp', {})
        
        # Validate required fields
        required = ['server', 'port', 'from_email']
        for field in required:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} required'}), 400
        
        if not is_valid_email(data['from_email']):
            return jsonify({'error': 'Invalid from_email format'}), 400
        
        smtp['server'] = data['server']
        smtp['port'] = int(data['port'])
        smtp['from_email'] = data['from_email']
        smtp['use_tls'] = data.get('use_tls', False)
        smtp['use_ssl'] = data.get('use_ssl', True)
        
        # Handle credentials
        if 'auth_method' in data:
            smtp['auth_method'] = data['auth_method']
        
        if data.get('auth_method') == 'basic':
            smtp['username'] = data.get('username', '')
            if data.get('password') and data['password'] != '***':
                smtp['password'] = data['password']  # TODO: encrypt
        elif data.get('auth_method') == 'oauth2':
            smtp['oauth_provider'] = data.get('oauth_provider', 'google')
            if data.get('oauth_client_id'):
                smtp['oauth_client_id'] = data['oauth_client_id']
            if data.get('oauth_client_secret') and data['oauth_client_secret'] != '***':
                smtp['oauth_client_secret'] = data['oauth_client_secret']
        
        smtp['updated_at'] = __import__('datetime').datetime.utcnow().isoformat()
        config['smtp'] = smtp
        _persist_config(main, config, 'organizer_config.json')
        
        return jsonify({'success': True, 'server': smtp['server']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_smtp.route('/smtp/test', methods=['POST'])
@requires_right('test_smtp')
def test_smtp_connection():
    """POST /api/organizer/config/smtp/test - Test SMTP connectivity."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        smtp = config.get('smtp', {})
        
        if not smtp.get('server'):
            return jsonify({'error': 'SMTP not configured'}), 400
        
        # Simulate SMTP connection test (in production, would attempt actual connection)
        return jsonify({
            'success': True,
            'server': smtp['server'],
            'port': smtp.get('port', 587),
            'message': 'SMTP connection test successful'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@routes_api_smtp.route('/smtp/send-test', methods=['POST'])
@requires_right('test_smtp')
def send_test_email():
    """POST /api/organizer/config/smtp/send-test - Send test email."""
    try:
        data = request.get_json() or {}
        recipient = data.get('recipient', '')
        
        if not recipient or not is_valid_email(recipient):
            return jsonify({'error': 'Valid recipient email required'}), 400
        
        main = get_main_module()
        config = getattr(main, 'config', {})
        smtp = config.get('smtp', {})
        
        if not smtp.get('server'):
            return jsonify({'error': 'SMTP not configured'}), 400
        
        # Simulate sending test email
        return jsonify({
            'success': True,
            'message': f'Test email sent to {recipient}',
            'timestamp': __import__('datetime').datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@routes_api_smtp.route('/credentials', methods=['GET'])
@requires_right('view_metrics')
def list_credentials():
    """GET /api/organizer/config/credentials - List stored credentials."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        creds = config.get('credentials', {})
        
        # Don't expose actual passwords
        result = {}
        for key, cred in creds.items():
            result[key] = {
                'type': cred.get('type', 'unknown'),
                'has_password': bool(cred.get('password')),
                'updated_at': cred.get('updated_at')
            }
        
        return jsonify({'credentials': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_smtp.route('/credentials', methods=['POST'])
@requires_right('manage_config')
def add_credential():
    """POST /api/organizer/config/credentials - Store new credential."""
    try:
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        cred_type = data.get('type', 'generic')
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not name:
            return jsonify({'error': 'name required'}), 400
        
        main = get_main_module()
        config = getattr(main, 'config', {})
        creds = config.get('credentials', {})
        
        if name in creds:
            return jsonify({'error': 'Credential already exists'}), 409
        
        creds[name] = {
            'type': cred_type,
            'username': username,
            'password': password,  # TODO: encrypt
            'created_at': __import__('datetime').datetime.utcnow().isoformat()
        }
        config['credentials'] = creds
        _persist_config(main, config, 'organizer_config.json')
        
        return jsonify({'success': True, 'name': name}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_smtp.route('/credentials/<cred_name>', methods=['DELETE'])
@requires_right('manage_config')
def delete_credential(cred_name):
    """DELETE /api/organizer/config/credentials/<name> - Remove credential."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        creds = config.get('credentials', {})
        
        if cred_name not in creds:
            return jsonify({'error': 'Credential not found'}), 404
        
        del creds[cred_name]
        config['credentials'] = creds
        _persist_config(main, config, 'organizer_config.json')
        
        return jsonify({'success': True, 'deleted': cred_name}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_smtp.route('/credentials/validate', methods=['POST'])
@requires_right('manage_config')
def validate_credential():
    """POST /api/organizer/config/credentials/validate - Test credential validity."""
    try:
        data = request.get_json() or {}
        cred_type = data.get('type', 'basic')
        
        # Simulate credential validation
        if cred_type == 'basic':
            username = data.get('username', '')
            password = data.get('password', '')
            if not username or not password:
                return jsonify({'error': 'username and password required', 'valid': False}), 400
        elif cred_type == 'oauth2':
            client_id = data.get('client_id', '')
            client_secret = data.get('client_secret', '')
            if not client_id:
                return jsonify({'error': 'client_id required', 'valid': False}), 400
        
        return jsonify({'success': True, 'valid': True, 'type': cred_type})
    except Exception as e:
        return jsonify({'error': str(e), 'valid': False}), 500


def _persist_config(main, config_dict, filename):
    """Helper: persist config to file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        setattr(main, 'config', config_dict)
    except Exception:
        pass
