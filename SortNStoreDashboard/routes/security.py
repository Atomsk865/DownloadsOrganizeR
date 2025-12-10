"""
Security admin endpoints - audit log viewing and lockout management.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required
from SortNStoreDashboard.auth.auth import requires_right
from SortNStoreDashboard.auth.security import (
    get_audit_log, get_lockout_status, reset_lockout
)

routes_security = Blueprint('routes_security', __name__)


@routes_security.route('/api/security/audit-log', methods=['GET'])
@login_required
@requires_right('admin')
def get_audit():
    """Retrieve authentication audit log."""
    try:
        limit = int(request.args.get('limit', 100))
        event_type = request.args.get('event_type')
        
        events = get_audit_log(limit=limit, event_type=event_type)
        return jsonify({
            "success": True,
            "events": events,
            "count": len(events)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@routes_security.route('/api/security/lockout-status', methods=['GET'])
@login_required
@requires_right('admin')
def lockout_status():
    """Get current lockout status."""
    try:
        status = get_lockout_status()
        return jsonify({
            "success": True,
            "status": status
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@routes_security.route('/api/security/unlock', methods=['POST'])
@login_required
@requires_right('admin')
def unlock():
    """Manually unlock a user or IP address."""
    try:
        data = request.get_json()
        identifier = data.get('identifier')
        identifier_type = data.get('type', 'username')  # 'username' or 'ip'
        
        if not identifier:
            return jsonify({"success": False, "error": "Identifier required"}), 400
        
        if identifier_type not in ['username', 'ip']:
            return jsonify({"success": False, "error": "Type must be 'username' or 'ip'"}), 400
        
        reset_lockout(identifier, identifier_type)
        
        return jsonify({
            "success": True,
            "message": f"{identifier_type.capitalize()} '{identifier}' unlocked"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@routes_security.route('/api/security/session-info', methods=['GET'])
@login_required
def session_info():
    """Get current session timing and timeout information."""
    try:
        from SortNStoreDashboard.auth.session_timeout import get_session_info
        info = get_session_info()
        return jsonify({
            "success": True,
            "session": info
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@routes_security.route('/api/security/refresh-session', methods=['POST'])
@login_required
def refresh_session():
    """Refresh session activity timestamp (keep-alive endpoint)."""
    try:
        from SortNStoreDashboard.auth.session_timeout import refresh_session_activity
        refresh_session_activity()
        return jsonify({
            "success": True,
            "message": "Session activity refreshed"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@routes_security.route('/api/security/ip-allowlist', methods=['GET'])
@login_required
@requires_right('admin')
def get_ip_allowlist():
    """Get current IP allowlist configuration."""
    try:
        from SortNStoreDashboard.config_runtime import get_dashboard_config
        from SortNStoreDashboard.auth.ip_allowlist import PRIVATE_NETWORKS
        
        config = get_dashboard_config()
        allowlist = config.get('ip_allowlist', [])
        
        return jsonify({
            "success": True,
            "allowlist": allowlist,
            "enabled": len(allowlist) > 0,
            "common_networks": PRIVATE_NETWORKS
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@routes_security.route('/api/security/ip-allowlist', methods=['POST'])
@login_required
@requires_right('admin')
def update_ip_allowlist():
    """Update IP allowlist configuration."""
    try:
        from SortNStoreDashboard.config_runtime import get_dashboard_config, save_dashboard_config
        from SortNStoreDashboard.auth.ip_allowlist import validate_cidr_list
        
        data = request.get_json()
        new_allowlist = data.get('allowlist', [])
        
        # Validate CIDR list
        valid, errors = validate_cidr_list(new_allowlist)
        if not valid:
            return jsonify({
                "success": False,
                "error": "Invalid CIDR notation",
                "details": errors
            }), 400
        
        # Update config
        config = get_dashboard_config()
        config['ip_allowlist'] = new_allowlist
        save_dashboard_config()
        
        # Warn if allowlist is empty (disables feature)
        if not new_allowlist:
            message = "IP allowlist disabled - all IPs allowed"
        else:
            message = f"IP allowlist updated with {len(new_allowlist)} ranges"
        
        return jsonify({
            "success": True,
            "message": message,
            "allowlist": new_allowlist
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@routes_security.route('/api/security/validate-cidr', methods=['POST'])
@login_required
@requires_right('admin')
def validate_cidr():
    """Validate CIDR notation without applying changes."""
    try:
        from SortNStoreDashboard.auth.ip_allowlist import validate_cidr_list
        
        data = request.get_json()
        cidrs = data.get('cidrs', [])
        
        valid, errors = validate_cidr_list(cidrs)
        
        return jsonify({
            "success": True,
            "valid": valid,
            "errors": errors
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@routes_security.route('/api/security/config', methods=['GET'])
@login_required
@requires_right('admin')
def get_security_config():
    """Retrieve all security configuration settings."""
    try:
        from SortNStoreDashboard.config_runtime import get_dashboard_config
        
        config = get_dashboard_config()
        security_config = config.get('security_config', {})
        
        return jsonify({
            'success': True,
            # Rate limiting & lockout
            'rate_limit': security_config.get('rate_limit', 10),
            'rate_window': security_config.get('rate_window', 60),
            'lockout_attempts': security_config.get('lockout_attempts', 5),
            'lockout_duration': security_config.get('lockout_duration', 5),
            # Session timeout
            'session_lifetime': security_config.get('session_lifetime', 60),
            'idle_timeout': security_config.get('idle_timeout', 30),
            'idle_warning': security_config.get('idle_warning', 25),
            # IP allowlist
            'ip_allowlist': config.get('ip_allowlist', []),
            # Audit settings
            'audit_retention_days': security_config.get('audit_retention_days', 90),
            'audit_max_entries': security_config.get('audit_max_entries', 10000)
        })
    except Exception as e:
        print(f"Error retrieving security config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@routes_security.route('/api/security/config', methods=['POST'])
@login_required
@requires_right('admin')
def update_security_config():
    """Update security configuration settings."""
    try:
        from SortNStoreDashboard.config_runtime import get_dashboard_config, save_dashboard_config
        from SortNStoreDashboard.auth.ip_allowlist import validate_cidr_list
        
        data = request.get_json() or {}
        config = get_dashboard_config()
        
        # Initialize security_config if it doesn't exist
        if 'security_config' not in config:
            config['security_config'] = {}
        
        security_config = config['security_config']
        
        # Update rate limiting & lockout settings
        if 'rate_limit' in data:
            security_config['rate_limit'] = max(1, min(100, int(data['rate_limit'])))
        if 'rate_window' in data:
            security_config['rate_window'] = max(10, min(300, int(data['rate_window'])))
        if 'lockout_attempts' in data:
            security_config['lockout_attempts'] = max(3, min(20, int(data['lockout_attempts'])))
        if 'lockout_duration' in data:
            security_config['lockout_duration'] = max(1, min(60, int(data['lockout_duration'])))
        
        # Update session timeout settings
        if 'session_lifetime' in data:
            security_config['session_lifetime'] = max(10, min(480, int(data['session_lifetime'])))
        if 'idle_timeout' in data:
            security_config['idle_timeout'] = max(5, min(120, int(data['idle_timeout'])))
        if 'idle_warning' in data:
            security_config['idle_warning'] = max(1, min(60, int(data['idle_warning'])))
        
        # Update IP allowlist
        if 'ip_allowlist' in data:
            allowlist = data['ip_allowlist']
            if not isinstance(allowlist, list):
                return jsonify({'success': False, 'error': 'ip_allowlist must be an array'}), 400
            
            # Validate CIDR list if not empty
            if allowlist:
                valid, errors = validate_cidr_list(allowlist)
                if not valid:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid CIDR notation',
                        'details': errors
                    }), 400
            
            config['ip_allowlist'] = allowlist
        
        # Update audit settings
        if 'audit_retention_days' in data:
            security_config['audit_retention_days'] = max(7, min(365, int(data['audit_retention_days'])))
        if 'audit_max_entries' in data:
            security_config['audit_max_entries'] = max(1000, min(100000, int(data['audit_max_entries'])))
        
        # Save configuration
        save_dashboard_config()
        
        return jsonify({
            'success': True,
            'message': 'Security configuration updated successfully'
        })
    except Exception as e:
        print(f"Error updating security config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
