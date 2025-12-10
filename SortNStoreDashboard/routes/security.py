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
