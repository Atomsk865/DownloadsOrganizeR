"""
Session management - timeout, idle detection, and activity tracking.
"""

from flask import session, request
from datetime import datetime, timedelta
from functools import wraps
import time

# Configuration
SESSION_LIFETIME_MINUTES = 60  # Total session lifetime
IDLE_TIMEOUT_MINUTES = 30      # Inactivity timeout
IDLE_WARNING_MINUTES = 25      # Show warning after 25min idle


def init_session_timeout(app):
    """
    Initialize session timeout middleware.
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def check_session_timeout():
        """Check and enforce session timeout before each request."""
        # Skip for login/logout/static routes
        if request.endpoint in ['routes_login.login_page', 'routes_login.login_post', 
                                 'routes_login.logout', 'static']:
            return
        
        # Skip if user not authenticated
        try:
            from flask_login import current_user
            if not current_user.is_authenticated:
                return
        except Exception:
            return
        
        now = time.time()
        
        # Initialize session timestamps on first request
        if 'session_start' not in session:
            session['session_start'] = now
            session['last_activity'] = now
            session.modified = True
            return
        
        # Check absolute session lifetime
        session_start = session.get('session_start', now)
        session_age_minutes = (now - session_start) / 60
        
        if session_age_minutes > SESSION_LIFETIME_MINUTES:
            # Session expired - force logout
            try:
                from flask_login import logout_user
                from flask import redirect, url_for, flash
                logout_user()
                flash('Your session has expired. Please log in again.', 'warning')
                return redirect(url_for('routes_login.login_page'))
            except Exception:
                pass
        
        # Check idle timeout
        last_activity = session.get('last_activity', now)
        idle_minutes = (now - last_activity) / 60
        
        if idle_minutes > IDLE_TIMEOUT_MINUTES:
            # Idle timeout - force logout
            try:
                from flask_login import logout_user
                from flask import redirect, url_for, flash
                logout_user()
                flash('Your session timed out due to inactivity. Please log in again.', 'warning')
                return redirect(url_for('routes_login.login_page'))
            except Exception:
                pass
        
        # Update last activity timestamp
        session['last_activity'] = now
        session.modified = True


def get_session_info():
    """
    Get current session timing information.
    
    Returns:
        Dictionary with session timestamps and remaining time
    """
    now = time.time()
    
    if 'session_start' not in session:
        return {
            "active": False,
            "session_age_seconds": 0,
            "idle_seconds": 0,
            "session_remaining_seconds": SESSION_LIFETIME_MINUTES * 60,
            "idle_remaining_seconds": IDLE_TIMEOUT_MINUTES * 60,
            "show_warning": False
        }
    
    session_start = session.get('session_start', now)
    last_activity = session.get('last_activity', now)
    
    session_age = now - session_start
    idle_time = now - last_activity
    
    session_remaining = max(0, (SESSION_LIFETIME_MINUTES * 60) - session_age)
    idle_remaining = max(0, (IDLE_TIMEOUT_MINUTES * 60) - idle_time)
    
    # Show warning if idle time approaching timeout
    show_warning = idle_time > (IDLE_WARNING_MINUTES * 60)
    
    return {
        "active": True,
        "session_age_seconds": int(session_age),
        "idle_seconds": int(idle_time),
        "session_remaining_seconds": int(session_remaining),
        "idle_remaining_seconds": int(idle_remaining),
        "show_warning": show_warning,
        "warning_threshold_seconds": IDLE_WARNING_MINUTES * 60
    }


def refresh_session_activity():
    """Manually refresh session activity timestamp (for AJAX calls)."""
    session['last_activity'] = time.time()
    session.modified = True
