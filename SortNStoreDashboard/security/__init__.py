"""
SortNStore Security Package

Enhanced authentication and authorization using Flask-Security-Too.

Modules:
- flask_security_integration.py: Core Flask-Security setup with User/Role models
- password_reset.py: Password reset and email verification flows

Usage:
    from SortNStoreDashboard.security.flask_security_integration import (
        init_flask_security,
        get_user_datastore,
        FLASK_SECURITY_AVAILABLE
    )
    
    if FLASK_SECURITY_AVAILABLE:
        init_flask_security(app, migrate=True)
        # Password reset endpoints automatically available
"""

# @flask-security-too: Export security components
from .flask_security_integration import (
    init_flask_security,
    get_user_datastore,
    User,
    Role,
    db,
    FLASK_SECURITY_AVAILABLE,
    migrate_users_from_config,
    export_users_to_config,
    FlaskSecurityStatus,
)

__all__ = [
    'init_flask_security',
    'get_user_datastore',
    'User',
    'Role',
    'db',
    'FLASK_SECURITY_AVAILABLE',
    'migrate_users_from_config',
    'export_users_to_config',
    'FlaskSecurityStatus',
]
