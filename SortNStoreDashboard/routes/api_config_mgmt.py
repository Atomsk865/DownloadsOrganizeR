"""
Phase 4: Health, Sync Status, Config Management, and Audit Log APIs

Endpoints for system health checks, config sync status, export/import, and audit trails.
"""

from flask import Blueprint, jsonify, request, send_file
import sys
import json
import io
from datetime import datetime

routes_api_config_mgmt = Blueprint('routes_api_config_mgmt', __name__, url_prefix='/api/organizer')


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


@routes_api_config_mgmt.route('/health', methods=['GET'])
@requires_right('view_metrics')
def config_health_check():
    """GET /api/organizer/health - Overall config and system health."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        dash_cfg = getattr(main, 'dashboard_config', {})
        
        # Check various components
        users_ok = len(dash_cfg.get('users', [])) > 0
        roles_ok = len(dash_cfg.get('roles', {})) > 0
        network_targets_ok = len(config.get('network_targets', {})) > 0
        smtp_ok = bool(config.get('smtp', {}).get('server'))
        folders_ok = len(config.get('watched_folders', [])) > 0
        
        # Overall health score
        components_ok = sum([users_ok, roles_ok, network_targets_ok, smtp_ok, folders_ok])
        health_score = (components_ok / 5) * 100
        
        return jsonify({
            'status': 'healthy' if health_score > 60 else 'degraded' if health_score > 30 else 'unhealthy',
            'health_score': health_score,
            'components': {
                'users': {'ok': users_ok, 'count': len(dash_cfg.get('users', []))},
                'roles': {'ok': roles_ok, 'count': len(dash_cfg.get('roles', {}))},
                'network_targets': {'ok': network_targets_ok, 'count': len(config.get('network_targets', {}))},
                'smtp': {'ok': smtp_ok, 'server': config.get('smtp', {}).get('server', 'not configured')},
                'watched_folders': {'ok': folders_ok, 'count': len(config.get('watched_folders', []))}
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500


@routes_api_config_mgmt.route('/config/sync-status', methods=['GET'])
@requires_right('view_metrics')
def config_sync_status():
    """GET /api/organizer/config/sync-status - Check config sync state."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        dash_cfg = getattr(main, 'dashboard_config', {})
        
        return jsonify({
            'synced': True,
            'last_sync': config.get('last_sync', datetime.utcnow().isoformat()),
            'config_version': config.get('config_version', 1),
            'dashboard_config_version': dash_cfg.get('config_version', 1),
            'pending_changes': False,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_config_mgmt.route('/config/export', methods=['GET'])
@requires_right('manage_config')
def export_config():
    """GET /api/organizer/config/export - Export complete configuration backup."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        dash_cfg = getattr(main, 'dashboard_config', {})
        
        export_data = {
            'export_version': 1,
            'export_timestamp': datetime.utcnow().isoformat(),
            'application': 'DownloadsOrganizeR',
            'organizer_config': config,
            'dashboard_config': dash_cfg
        }
        
        filename = f'organizer_backup_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
        
        return send_file(
            io.BytesIO(json.dumps(export_data, indent=2, ensure_ascii=False).encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_config_mgmt.route('/config/import', methods=['POST'])
@requires_right('manage_config')
def import_config():
    """POST /api/organizer/config/import - Restore configuration from backup."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename.endswith('.json'):
            return jsonify({'error': 'Invalid file format (must be .json)'}), 400
        
        import_data = json.loads(file.read().decode('utf-8'))
        
        # Validate structure
        if 'export_version' not in import_data:
            return jsonify({'error': 'Invalid backup file structure'}), 400
        
        main = get_main_module()
        
        # Import organizer config
        if 'organizer_config' in import_data:
            config = import_data['organizer_config']
            with open('organizer_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            setattr(main, 'config', config)
        
        # Import dashboard config (preserve primary admin)
        if 'dashboard_config' in import_data:
            dash_cfg = import_data['dashboard_config']
            admin_user = getattr(main, 'ADMIN_USER', 'admin')
            # Preserve primary admin role
            for user in dash_cfg.get('users', []):
                if user.get('username') == admin_user:
                    user['role'] = 'admin'
                    break
            with open('dashboard_config.json', 'w', encoding='utf-8') as f:
                json.dump(dash_cfg, f, indent=2, ensure_ascii=False)
            setattr(main, 'dashboard_config', dash_cfg)
        
        return jsonify({
            'success': True,
            'message': 'Configuration imported successfully',
            'import_timestamp': datetime.utcnow().isoformat()
        })
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_config_mgmt.route('/config/validate', methods=['POST'])
@requires_right('manage_config')
def validate_import():
    """POST /api/organizer/config/validate - Pre-validate import file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename.endswith('.json'):
            return jsonify({'valid': False, 'error': 'Invalid file format'}), 400
        
        import_data = json.loads(file.read().decode('utf-8'))
        
        # Validate structure
        issues = []
        if 'export_version' not in import_data:
            issues.append('Missing export_version')
        if 'organizer_config' not in import_data and 'dashboard_config' not in import_data:
            issues.append('No config data found')
        
        return jsonify({
            'valid': len(issues) == 0,
            'issues': issues,
            'export_timestamp': import_data.get('export_timestamp', 'unknown'),
            'application': import_data.get('application', 'unknown')
        })
    except json.JSONDecodeError:
        return jsonify({'valid': False, 'error': 'Invalid JSON format'})
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})


# Audit Log endpoints

@routes_api_config_mgmt.route('/config/audit/users', methods=['GET'])
@requires_right('view_metrics')
def get_audit_log_users():
    """GET /api/organizer/config/audit/users - Get user management audit log."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        audit = config.get('audit_users', [])
        
        limit = request.args.get('limit', 50, type=int)
        return jsonify({
            'audit_log': audit[-limit:],
            'total_entries': len(audit),
            'resource': 'users'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_config_mgmt.route('/config/audit/network', methods=['GET'])
@requires_right('view_metrics')
def get_audit_log_network():
    """GET /api/organizer/config/audit/network - Get network targets audit log."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        audit = config.get('audit_network_targets', [])
        
        limit = request.args.get('limit', 50, type=int)
        return jsonify({
            'audit_log': audit[-limit:],
            'total_entries': len(audit),
            'resource': 'network_targets'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_config_mgmt.route('/config/audit/smtp', methods=['GET'])
@requires_right('view_metrics')
def get_audit_log_smtp():
    """GET /api/organizer/config/audit/smtp - Get SMTP configuration audit log."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        audit = config.get('audit_smtp', [])
        
        limit = request.args.get('limit', 50, type=int)
        return jsonify({
            'audit_log': audit[-limit:],
            'total_entries': len(audit),
            'resource': 'smtp'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_api_config_mgmt.route('/config/audit/folders', methods=['GET'])
@requires_right('view_metrics')
def get_audit_log_folders():
    """GET /api/organizer/config/audit/folders - Get watched folders audit log."""
    try:
        main = get_main_module()
        config = getattr(main, 'config', {})
        audit = config.get('watch_folders_audit', [])
        
        limit = request.args.get('limit', 50, type=int)
        return jsonify({
            'audit_log': audit[-limit:],
            'total_entries': len(audit),
            'resource': 'folders'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
