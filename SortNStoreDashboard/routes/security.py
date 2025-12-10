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
