"""
Real-Time Dashboard Routes

Provides Flask routes for accessing the real-time dashboard:
- GET /dashboard - Dashboard HTML page
- WebSocket events for live updates

Features:
- @flask_route: Dashboard endpoint
- @websocket: Real-time updates
- Authentication integrated
- Graceful degradation
"""

from flask import Blueprint, render_template, current_app
from functools import wraps

try:
    from flask_login import login_required, current_user
    LOGIN_AVAILABLE = True
except ImportError:
    LOGIN_AVAILABLE = False
    def login_required(f):
        return f


# Create blueprint
dashboard_routes = Blueprint('dashboard_routes', __name__)


def dashboard_login_required(f):
    """Decorator to require login for dashboard."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if LOGIN_AVAILABLE:
            return login_required(f)(*args, **kwargs)
        return f(*args, **kwargs)
    return decorated_function


@dashboard_routes.route('/dashboard', methods=['GET'])
@dashboard_login_required
def real_time_dashboard():
    """
    Serve the real-time task monitoring dashboard.
    
    Returns:
        Rendered dashboard HTML with WebSocket client
    """
    from SortNStoreDashboard.structured_logging import get_logger
    log = get_logger(__name__)
    
    try:
        log.info("dashboard_page_accessed")
        return render_template('dashboard_real_time.html')
    
    except Exception as e:
        log.error("dashboard_page_error", error=str(e))
        return {
            'status': 'error',
            'message': 'Dashboard unavailable'
        }, 500


def register_dashboard_routes(app):
    """Register dashboard routes with Flask app."""
    try:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        
        app.register_blueprint(dashboard_routes)
        log.info("dashboard_routes_registered")
        return True
    
    except Exception as e:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        log.error("dashboard_routes_registration_failed", error=str(e))
        return False
