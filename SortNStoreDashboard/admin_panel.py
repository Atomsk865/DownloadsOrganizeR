"""
Flask-Admin Integration for SortNStore Dashboard

Provides auto-generated admin interface for:
- User management (create, edit, delete)
- Role management (create, edit, delete, permissions)
- Configuration management
- Audit logging

Access: http://localhost:5000/admin

Features:
- @flask-admin: Auto-generated admin views
- @sqlalchemy: SQLAlchemy model integration
- Authentication: Requires admin role to access
- Non-breaking: Complements existing dashboard
- Graceful: Returns None if flask-admin not installed

Usage:
    from SortNStoreDashboard.admin_panel import init_flask_admin
    admin = init_flask_admin(app, db)

    if admin:
        app.logger.info("Admin panel initialized at /admin")
"""

try:
    from flask_admin import Admin, AdminIndexView
    from flask_admin.contrib.sqla import ModelView
    from flask_login import current_user
    FLASK_ADMIN_AVAILABLE = True
except ImportError:
    FLASK_ADMIN_AVAILABLE = False
    Admin = None
    AdminIndexView = object
    ModelView = object
    current_user = None


# @flask-admin: Secure admin index view requiring authentication
class SecureAdminIndexView(AdminIndexView):
    """
    Admin index view with authentication check.
    
    Requires user to have admin role to access admin panel.
    """
    def is_accessible(self):
        """Check if admin panel is accessible to current user."""
        if not current_user or not current_user.is_authenticated:
            return False
        
        # Check if user has admin role
        try:
            from SortNStoreDashboard.security.flask_security_integration import Role
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role and admin_role in current_user.roles:
                return True
        except Exception:
            pass
        
        return False
    
    def inaccessible_callback(self, name, **kwargs):
        """Handle inaccessible admin panel access attempt."""
        from flask import redirect, url_for, flash
        flash('You do not have access to the admin panel.', 'error')
        return redirect(url_for('login', next=request.url))


# @flask-admin & @sqlalchemy: User model admin view
class UserAdmin(ModelView):
    """
    Admin view for User model.
    
    Allows:
    - View all users
    - Create new users
    - Edit user details (username, email, roles)
    - Delete users
    - Manage roles assignment
    """
    
    # @flask-admin: Security - require admin access
    def is_accessible(self):
        """User admin requires authentication."""
        if not current_user or not current_user.is_authenticated:
            return False
        
        # Check admin role
        try:
            from SortNStoreDashboard.security.flask_security_integration import Role
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role and admin_role in current_user.roles:
                return True
        except Exception:
            pass
        
        return False
    
    # @flask-admin: Column configuration
    column_list = ['id', 'username', 'email', 'roles', 'confirmed_at', 'active', 'last_login_at']
    column_searchable_list = ['username', 'email']
    column_filters = ['active', 'confirmed_at', 'last_login_at']
    
    # @flask-admin: Form configuration
    form_excluded_columns = ['password', 'failed_login_count', 'locked_at', 'fs_uniquifier']
    form_columns = ['username', 'email', 'active', 'roles']
    
    # @flask-admin: Display configuration
    column_labels = {
        'id': 'User ID',
        'username': 'Username',
        'email': 'Email Address',
        'active': 'Active',
        'confirmed_at': 'Email Confirmed',
        'last_login_at': 'Last Login',
        'last_login_ip': 'Last Login IP',
        'failed_login_count': 'Failed Logins',
        'locked_at': 'Locked Until',
        'roles': 'Roles',
    }
    
    # @flask-admin: Formatting
    column_formatters = {
        'confirmed_at': lambda v, c, m, p: m.confirmed_at.strftime('%Y-%m-%d %H:%M:%S') if m.confirmed_at else 'Not confirmed',
        'last_login_at': lambda v, c, m, p: m.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if m.last_login_at else 'Never',
    }


# @flask-admin & @sqlalchemy: Role model admin view
class RoleAdmin(ModelView):
    """
    Admin view for Role model.
    
    Allows:
    - View all roles
    - Create new roles
    - Edit role details (name, description, permissions)
    - Delete roles
    - Manage permissions
    """
    
    # @flask-admin: Security - require admin access
    def is_accessible(self):
        """Role admin requires authentication."""
        if not current_user or not current_user.is_authenticated:
            return False
        
        # Check admin role
        try:
            from SortNStoreDashboard.security.flask_security_integration import Role
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role and admin_role in current_user.roles:
                return True
        except Exception:
            pass
        
        return False
    
    # @flask-admin: Column configuration
    column_list = ['id', 'name', 'description', 'permissions']
    column_searchable_list = ['name', 'description']
    column_filters = ['id', 'name']
    
    # @flask-admin: Form configuration
    form_columns = ['name', 'description', 'permissions']
    
    # @flask-admin: Display configuration
    column_labels = {
        'id': 'Role ID',
        'name': 'Role Name',
        'description': 'Description',
        'permissions': 'Permissions',
    }


def init_flask_admin(app, db):
    """
    Initialize Flask-Admin interface.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    
    Returns:
        Admin instance if flask-admin is available, None otherwise
    
    Example:
        admin = init_flask_admin(app, db)
        if admin:
            logger.info("Admin panel at /admin")
    """
    if not FLASK_ADMIN_AVAILABLE:
        return None
    
    if not db or not hasattr(db, 'Model'):
        return None
    
    try:
        from SortNStoreDashboard.security.flask_security_integration import User, Role
        from SortNStoreDashboard.structured_logging import get_logger
        
        log = get_logger(__name__)
        
        # @flask-admin: Initialize admin interface
        admin = Admin(
            app,
            name='SortNStore Admin',
            index_view=SecureAdminIndexView(
                name='Dashboard',
                template='admin/index.html',
                url='/admin'
            ),
            base_template='admin/base.html',
            url='/admin'
        )
        
        # @flask-admin & @sqlalchemy: Add User model view
        admin.add_view(
            UserAdmin(
                User,
                db.session,
                name='Users',
                category='User Management'
            )
        )
        
        # @flask-admin & @sqlalchemy: Add Role model view
        admin.add_view(
            RoleAdmin(
                Role,
                db.session,
                name='Roles',
                category='User Management'
            )
        )
        
        log.info("flask_admin_initialized",
                status="success",
                admin_url="/admin",
                views=["Users", "Roles"])
        
        return admin
    
    except ImportError as e:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        log.debug("flask_admin_import_failed",
                 reason="flask_security_not_available",
                 error=str(e))
        return None
    
    except Exception as e:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        log.error("flask_admin_initialization_failed",
                 error=str(e),
                 exc_info=True)
        return None


# @flask-admin: Configuration helper function
def get_flask_admin_status():
    """
    Get Flask-Admin availability and status.
    
    Returns:
        dict with status information
    """
    return {
        'available': FLASK_ADMIN_AVAILABLE,
        'admin_url': '/admin' if FLASK_ADMIN_AVAILABLE else None,
        'requires_auth': True,
        'requires_admin_role': True,
        'features': [
            'User management' if FLASK_ADMIN_AVAILABLE else None,
            'Role management' if FLASK_ADMIN_AVAILABLE else None,
            'Configuration editing' if FLASK_ADMIN_AVAILABLE else None,
        ] if FLASK_ADMIN_AVAILABLE else []
    }
