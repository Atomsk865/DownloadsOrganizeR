"""
Flask-Security-Too Integration for SortNStore Dashboard

Provides enhanced authentication with:
- Password reset via email
- Email verification
- User/role management
- Account lockout protection
- 2FA support (future)

Non-breaking integration that coexists with existing auth system.

Usage:
    from SortNStoreDashboard.security.flask_security_integration import (
        init_flask_security, 
        get_user_datastore,
        FLASK_SECURITY_AVAILABLE
    )
    
    if FLASK_SECURITY_AVAILABLE:
        init_flask_security(app, db)

Documentation:
    https://flask-security-too.readthedocs.io/
"""

from typing import Optional, Dict, Any
import sys

# @flask-security-too: Check availability
try:
    from flask_security import Security, SQLAlchemyUserDatastore, hash_password
    from flask_sqlalchemy import SQLAlchemy
    FLASK_SECURITY_AVAILABLE = True
except ImportError:
    FLASK_SECURITY_AVAILABLE = False
    # Provide stub for development when not installed
    SQLAlchemy = None


# @flask-security-too: SQLAlchemy database instance (shared with app)
if FLASK_SECURITY_AVAILABLE:
    db = SQLAlchemy()
else:
    # Provide stub class when Flask-Security not available
    class _StubDB:
        def init_app(self, app): pass
        def Model(self): pass
        class Column: pass
        class Integer: pass
        class String: pass
        class Text: pass
        class Boolean: pass
        class DateTime: pass
        class Table: pass
        def relationship(self, *args, **kwargs): return None
        def ForeignKey(self, *args): return None
        class session:
            @staticmethod
            def commit(): pass
            @staticmethod
            def rollback(): pass
        func = None
    db = _StubDB()
    db.func = type('Func', (), {'now': lambda: None})()


# @flask-security-too: Define User and Role models
if FLASK_SECURITY_AVAILABLE:
    
    class Role(db.Model):
        """User role for RBAC (Role-Based Access Control)."""
        
        __tablename__ = 'role'
        
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(80), unique=True, nullable=False)
        description = db.Column(db.String(255))
        
        # Permissions: JSON-encoded list of permission names
        permissions = db.Column(db.Text, default='[]')
        
        def __repr__(self):
            return f'<Role {self.name}>'


    class User(db.Model):
        """User account with security features."""
        
        __tablename__ = 'user'
        
        id = db.Column(db.Integer(), primary_key=True)
        username = db.Column(db.String(255), unique=True, nullable=False, index=True)
        email = db.Column(db.String(255), unique=True, nullable=True)
        
        # @flask-security-too: Password security
        password = db.Column(db.String(255), nullable=False)
        
        # Account status
        active = db.Column(db.Boolean(), default=True, nullable=False)
        
        # @flask-security-too: Email verification
        confirmed_at = db.Column(db.DateTime())
        
        # @flask-security-too: Account lockout
        failed_login_count = db.Column(db.Integer(), default=0)
        locked_at = db.Column(db.DateTime())
        
        # Last login tracking
        last_login_at = db.Column(db.DateTime())
        last_login_ip = db.Column(db.String(45))  # IPv6-compatible
        
        # Metadata
        created_at = db.Column(db.DateTime(), default=db.func.now())
        updated_at = db.Column(db.DateTime(), default=db.func.now(), onupdate=db.func.now())
        
        # Relationships
        roles = db.relationship('Role', secondary='user_roles',
                               backref=db.backref('users', lazy='dynamic'))
        
        def __repr__(self):
            return f'<User {self.username}>'
        
        def has_role(self, role_name: str) -> bool:
            """Check if user has a specific role."""
            return any(role.name == role_name for role in self.roles)
        
        def set_password(self, password: str) -> None:
            """Hash and set password using Flask-Security."""
            if FLASK_SECURITY_AVAILABLE:
                self.password = hash_password(password)
            else:
                # Fallback for when Flask-Security not available
                import bcrypt
                self.password = bcrypt.hashpw(
                    password.encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')


    # @flask-security-too: Many-to-many relationship table
    user_roles = db.Table(
        'user_roles',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
    )

else:
    # Stub classes when Flask-Security not available
    class Role:
        pass
    
    class User:
        pass
    
    user_roles = None


def init_flask_security(app, migrate=False) -> Optional[Any]:
    """
    Initialize Flask-Security-Too with SortNStore.
    
    Args:
        app: Flask application instance
        migrate: If True, create database tables (for development)
    
    Returns:
        Security instance or None if Flask-Security not available
    """
    if not FLASK_SECURITY_AVAILABLE:
        return None
    
    # @flask-security-too: Initialize SQLAlchemy
    db.init_app(app)
    
    # @flask-security-too: Configure Flask-Security
    app.config['SECURITY_PASSWORD_SALT'] = app.config.get(
        'SECURITY_PASSWORD_SALT',
        'sortnstore-security-salt'
    )
    
    # @flask-security-too: Email configuration (requires SMTP setup)
    app.config.setdefault('SECURITY_EMAIL_SENDER', 'noreply@sortnstore.local')
    app.config.setdefault('SECURITY_PASSWORD_RESET_EMAIL', True)
    app.config.setdefault('SECURITY_CONFIRMABLE', False)  # Email verification (optional)
    app.config.setdefault('SECURITY_REGISTERABLE', False)  # User self-registration (disabled)
    
    # @flask-security-too: Security headers
    app.config.setdefault('SECURITY_REMEMBER_COOKIE_SAMESITE', 'Lax')
    app.config.setdefault('SECURITY_REMEMBER_COOKIE_SECURE', False)  # Enable in production with HTTPS
    
    # @flask-security-too: User datastore
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    
    # @flask-security-too: Initialize Security
    security = Security(app, user_datastore)
    
    # @flask-security-too: Create database tables
    with app.app_context():
        if migrate:
            db.create_all()
            
            # Create default roles if missing
            if not user_datastore.find_role("admin"):
                user_datastore.create_role(name="admin", description="Administrator")
            if not user_datastore.find_role("operator"):
                user_datastore.create_role(name="operator", description="Operator")
            if not user_datastore.find_role("viewer"):
                user_datastore.create_role(name="viewer", description="Viewer")
            
            db.session.commit()
    
    return security, user_datastore


def get_user_datastore() -> Optional[Any]:
    """
    Get the user datastore instance for managing users/roles.
    
    Usage:
        datastore = get_user_datastore()
        if datastore:
            user = datastore.create_user(username="admin", email="admin@local")
            datastore.add_role_to_user(user, "admin")
    
    Returns:
        SQLAlchemyUserDatastore instance or None if Flask-Security not available
    """
    if not FLASK_SECURITY_AVAILABLE:
        return None
    
    # Try to get from app context
    try:
        from flask import current_app
        if hasattr(current_app, 'security'):
            return current_app.security.datastore
    except Exception:
        pass
    
    return None


def migrate_users_from_config(config: Dict[str, Any]) -> int:
    """
    Migrate users from config JSON to Flask-Security database.
    
    This enables gradual migration from file-based config to database-backed users.
    
    Args:
        config: Configuration dict with 'users' list
    
    Returns:
        Number of users migrated
    
    Example config format:
        {
            "users": [
                {"username": "admin", "role": "admin", "password_hash": "..."},
                {"username": "operator", "role": "operator", "password_hash": "..."}
            ]
        }
    """
    if not FLASK_SECURITY_AVAILABLE:
        return 0
    
    from flask import current_app
    
    migrated = 0
    datastore = get_user_datastore()
    if not datastore:
        return 0
    
    users_config = config.get('users', [])
    
    with current_app.app_context():
        for user_conf in users_config:
            username = user_conf.get('username')
            if not username:
                continue
            
            # Skip if user already exists
            if datastore.find_user(username=username):
                continue
            
            # Create user with password from config
            password_hash = user_conf.get('password_hash', '')
            email = user_conf.get('email', f'{username}@sortnstore.local')
            
            user = datastore.create_user(
                username=username,
                email=email,
                password=password_hash if password_hash else 'changeme',
                active=True
            )
            
            # Assign roles
            role_name = user_conf.get('role', 'viewer')
            role = datastore.find_role(role_name)
            if role:
                datastore.add_role_to_user(user, role)
            
            db.session.commit()
            migrated += 1
    
    return migrated


def export_users_to_config() -> Dict[str, Any]:
    """
    Export Flask-Security users to config JSON format.
    
    Returns:
        Dict with 'users' list in config format
    """
    if not FLASK_SECURITY_AVAILABLE:
        return {"users": []}
    
    from flask import current_app
    
    with current_app.app_context():
        users = User.query.all()
        users_list = []
        
        for user in users:
            role_names = [role.name for role in user.roles]
            users_list.append({
                'username': user.username,
                'email': user.email,
                'role': role_names[0] if role_names else 'viewer',
                'active': user.active,
                'confirmed': user.confirmed_at is not None
            })
        
        return {"users": users_list}


class FlaskSecurityStatus:
    """Status and diagnostic information for Flask-Security integration."""
    
    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Get current Flask-Security status."""
        return {
            'available': FLASK_SECURITY_AVAILABLE,
            'enabled': False,  # Set to True when initialized
            'version': None if not FLASK_SECURITY_AVAILABLE else 'N/A',
            'features': {
                'password_reset': FLASK_SECURITY_AVAILABLE,
                'email_verification': False,  # Requires SMTP
                'two_factor': False,  # Future
                'user_registration': False,  # Disabled by default
                'account_lockout': FLASK_SECURITY_AVAILABLE,
            },
            'user_count': User.query.count() if FLASK_SECURITY_AVAILABLE else 0,
        }
