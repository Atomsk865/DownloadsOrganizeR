import bcrypt
import json
import sys
import platform
from flask import Response, request, g
try:
    from flask_login import current_user
except Exception:
    current_user = None
from functools import wraps
from typing import Optional, Dict, Any

# Optional imports with graceful fallbacks
try:
    from ldap3 import Server, Connection, ALL, NTLM
    from ldap3.core.exceptions import LDAPException
    LDAP_AVAILABLE = True
except ImportError:
    LDAP_AVAILABLE = False

try:
    if platform.system() == 'Windows':
        import win32security
        import win32api
        import win32con
        WINDOWS_AUTH_AVAILABLE = True
    else:
        WINDOWS_AUTH_AVAILABLE = False
except ImportError:
    WINDOWS_AUTH_AVAILABLE = False


class AuthProvider:
    """Base authentication provider interface."""
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user with given credentials. Returns True if valid."""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if this auth provider is available on this system."""
        return True


class BasicAuthProvider(AuthProvider):
    """Basic authentication using bcrypt hashed passwords."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.admin_user = config.get('dashboard_user', 'admin')
        self.admin_pass_hash = None
        self._initialize_password_hash()
    
    def _initialize_password_hash(self):
        """Initialize the password hash from config or environment using runtime config."""
        from OrganizerDashboard.config_runtime import get_config, save_config
        # Also ensure dashboard_config mirrors the admin password hash for consistent auth lookups
        try:
            from OrganizerDashboard.config_runtime import get_dashboard_config, save_dashboard_config
        except Exception:
            get_dashboard_config = None
            save_dashboard_config = None
        main = sys.modules.get('__main__')
        
        if main is not None and hasattr(main, 'ADMIN_PASS_HASH') and main.ADMIN_PASS_HASH is not None:
            self.admin_pass_hash = main.ADMIN_PASS_HASH
            return
        
        stored_hash = get_config().get("dashboard_pass_hash")
        if stored_hash:
            self.admin_pass_hash = stored_hash.encode('utf-8')
            if main is not None and hasattr(main, 'ADMIN_PASS_HASH'):
                main.ADMIN_PASS_HASH = self.admin_pass_hash
            # Mirror into dashboard_config users if missing
            if get_dashboard_config and save_dashboard_config:
                try:
                    dash = get_dashboard_config()
                    updated = False
                    for u in dash.get('users', []):
                        if u.get('username') == self.admin_user:
                            if not u.get('password_hash'):
                                u['password_hash'] = stored_hash
                                updated = True
                            break
                    if not any(u.get('username') == self.admin_user for u in dash.get('users', [])):
                        dash.setdefault('users', []).append({'username': self.admin_user, 'role': 'admin', 'password_hash': stored_hash})
                        updated = True
                    if updated:
                        save_dashboard_config()
                except Exception:
                    pass
            return
        
        plain = get_config().get("dashboard_pass")
        if plain:
            self.admin_pass_hash = bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt())
            try:
                cfg = get_config()
                cfg['dashboard_pass_hash'] = self.admin_pass_hash.decode('utf-8')
                if 'dashboard_pass' in cfg:
                    del cfg['dashboard_pass']
                save_config()
                if get_dashboard_config and save_dashboard_config:
                    dash = get_dashboard_config()
                    # Update or insert user entry
                    found = False
                    for u in dash.get('users', []):
                        if u.get('username') == self.admin_user:
                            u['password_hash'] = cfg['dashboard_pass_hash']
                            found = True
                            break
                    if not found:
                        dash.setdefault('users', []).append({'username': self.admin_user, 'role': 'admin', 'password_hash': cfg['dashboard_pass_hash']})
                    save_dashboard_config()
            except Exception:
                pass
            return
        
        # Use default password from environment
        default_pass = getattr(main, 'ADMIN_PASS', 'change_this_password') if main is not None else 'change_this_password'
        self.admin_pass_hash = bcrypt.hashpw(default_pass.encode('utf-8'), bcrypt.gensalt())
        try:
            cfg = get_config()
            cfg['dashboard_user'] = self.admin_user
            cfg['dashboard_pass_hash'] = self.admin_pass_hash.decode('utf-8')
            save_config()
            if get_dashboard_config and save_dashboard_config:
                dash = get_dashboard_config()
                found = False
                for u in dash.get('users', []):
                    if u.get('username') == self.admin_user:
                        u['password_hash'] = cfg['dashboard_pass_hash']
                        found = True
                        break
                if not found:
                    dash.setdefault('users', []).append({'username': self.admin_user, 'role': 'admin', 'password_hash': cfg['dashboard_pass_hash']})
                save_dashboard_config()
        except Exception:
            pass
    
    def authenticate(self, username: str, password: str) -> bool:
        """Verify username/password against stored bcrypt hash or dashboard_config users."""
        # Primary admin user
        if username == self.admin_user and self.admin_pass_hash is not None:
            try:
                return bcrypt.checkpw(password.encode('utf-8'), self.admin_pass_hash)
            except Exception:
                return False

        # Support additional users loaded from dashboard_config
        try:
            from OrganizerDashboard.config_runtime import get_dashboard_config
            dashboard_config = get_dashboard_config()
            users = dashboard_config.get('users', [])
            for u in users:
                if u.get('username') == username:
                    pwd_hash = u.get('password_hash')
                    if pwd_hash:
                        try:
                            return bcrypt.checkpw(password.encode('utf-8'), pwd_hash.encode('utf-8'))
                        except Exception:
                            return False
                    # Fallback: if this is the admin user and we have admin_pass_hash
                    if username == self.admin_user and self.admin_pass_hash is not None:
                        try:
                            return bcrypt.checkpw(password.encode('utf-8'), self.admin_pass_hash)
                        except Exception:
                            return False
                    return False
        except Exception:
            return False
        return False


class LDAPAuthProvider(AuthProvider):
    """LDAP/Active Directory authentication."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ldap_config = config.get('ldap_config', {})
        self.server_uri = self.ldap_config.get('server')
        self.base_dn = self.ldap_config.get('base_dn')
        self.user_dn_template = self.ldap_config.get('user_dn_template', 'uid={username},{base_dn}')
        self.use_ssl = self.ldap_config.get('use_ssl', True)
        self.bind_dn = self.ldap_config.get('bind_dn')  # Optional service account
        self.bind_password = self.ldap_config.get('bind_password')
        self.search_filter = self.ldap_config.get('search_filter', '(uid={username})')
        self.allowed_groups = self.ldap_config.get('allowed_groups', [])
    
    def is_available(self) -> bool:
        """Check if LDAP is configured and library is available."""
        return LDAP_AVAILABLE and bool(self.server_uri and self.base_dn)
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate against LDAP server."""
        if not self.is_available():
            return False
        
        try:
            # Create server connection
            server = Server(self.server_uri, use_ssl=self.use_ssl, get_info=ALL)
            
            # Format user DN
            user_dn = self.user_dn_template.format(
                username=username,
                base_dn=self.base_dn
            )
            
            # Try direct bind
            conn = Connection(server, user=user_dn, password=password, auto_bind=True)
            
            # Check group membership if required
            if self.allowed_groups:
                search_filter = self.search_filter.format(username=username)
                conn.search(
                    search_base=self.base_dn,
                    search_filter=search_filter,
                    attributes=['memberOf']
                )
                
                if not conn.entries:
                    return False
                
                user_groups = conn.entries[0].memberOf.values if hasattr(conn.entries[0], 'memberOf') else []
                if not any(group in user_groups for group in self.allowed_groups):
                    return False
            
            conn.unbind()
            return True
            
        except LDAPException:
            return False
        except Exception:
            return False


class WindowsAuthProvider(AuthProvider):
    """Windows local/domain authentication using win32security."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.windows_config = config.get('windows_auth_config', {})
        self.domain = self.windows_config.get('domain', '')
        self.allowed_groups = self.windows_config.get('allowed_groups', [])
    
    def is_available(self) -> bool:
        """Check if Windows auth is available."""
        return WINDOWS_AUTH_AVAILABLE
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate using Windows local or domain credentials."""
        if not self.is_available():
            return False
        
        try:
            # Format username with domain if configured
            if self.domain and '\\' not in username and '@' not in username:
                full_username = f"{self.domain}\\{username}"
            else:
                full_username = username
            
            # Attempt to logon user
            handle = win32security.LogonUser(
                full_username,
                None,  # Domain is in username
                password,
                win32con.LOGON32_LOGON_NETWORK,
                win32con.LOGON32_PROVIDER_DEFAULT
            )
            
            # Check group membership if required
            if self.allowed_groups:
                # Get user's groups
                user_sid = win32security.GetTokenInformation(
                    handle, win32security.TokenUser
                )[0]
                
                groups = win32security.GetTokenInformation(
                    handle, win32security.TokenGroups
                )
                
                user_groups = []
                for group_sid, _ in groups:
                    try:
                        name, domain, _ = win32security.LookupAccountSid(None, group_sid)
                        user_groups.append(f"{domain}\\{name}" if domain else name)
                    except Exception:
                        pass
                
                if not any(group in user_groups for group in self.allowed_groups):
                    win32api.CloseHandle(handle)
                    return False
            
            win32api.CloseHandle(handle)
            return True
            
        except Exception:
            return False


class AuthManager:
    """Manages multiple authentication providers with fallback chain."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.auth_method = config.get('auth_method', 'basic')
        self.enable_fallback = config.get('auth_fallback_enabled', True)
        
        # Initialize all providers
        self.providers = {
            'basic': BasicAuthProvider(config),
            'ldap': LDAPAuthProvider(config),
            'windows': WindowsAuthProvider(config)
        }
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user using configured method with optional fallback."""
        # Try primary auth method
        primary_provider = self.providers.get(self.auth_method)
        if primary_provider and primary_provider.is_available():
            if primary_provider.authenticate(username, password):
                return True
        
        # Try fallback to basic auth if enabled and primary failed
        if self.enable_fallback and self.auth_method != 'basic':
            basic_provider = self.providers['basic']
            if basic_provider.authenticate(username, password):
                return True
        
        return False
    
    def get_available_methods(self) -> list:
        """Get list of available authentication methods."""
        available = []
        for name, provider in self.providers.items():
            if provider.is_available():
                available.append(name)
        return available


# Global auth manager instance
_auth_manager: Optional[AuthManager] = None


def initialize_auth_manager():
    """Initialize the global auth manager with config from main module."""
    global _auth_manager
    try:
        from OrganizerDashboard.config_runtime import get_config
        cfg = get_config()
        _auth_manager = AuthManager(cfg)
    except Exception:
        # Fallback to legacy behavior using __main__ if available
        try:
            main = sys.modules['__main__']
            _auth_manager = AuthManager(getattr(main, 'config', {}))
        except Exception:
            _auth_manager = AuthManager({})


def initialize_password_hash():
    """Legacy function for backwards compatibility. Now handled by AuthManager."""
    initialize_auth_manager()


def check_auth(username: str, password: str) -> bool:
    """Verify username/password using configured auth manager."""
    global _auth_manager
    if _auth_manager is None:
        initialize_auth_manager()
    return _auth_manager.authenticate(username, password) if _auth_manager else False


def authenticate():
    """Return 401 authentication required response."""
    return Response(
        'Authentication required', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    """Decorator to require authentication for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        # First, accept Basic auth if provided
        if auth and check_auth(auth.username or '', auth.password or ''):
            g.current_user = auth.username
            return f(*args, **kwargs)
        # Fallback to session-based authentication
        if current_user is not None:
            try:
                if current_user.is_authenticated:
                    g.current_user = current_user.get_id()
                    return f(*args, **kwargs)
            except Exception:
                pass
        return authenticate()
    return decorated

def requires_right(right_name: str):
    """Decorator enforcing that authenticated user possesses a specific right via role mapping."""
    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            auth = request.authorization
            username = None
            # Try Basic auth first
            if auth and check_auth(auth.username or '', auth.password or ''):
                username = auth.username
            elif current_user is not None:
                try:
                    if current_user.is_authenticated:
                        username = current_user.get_id()
                except Exception:
                    username = None
            if not username:
                return authenticate()
            g.current_user = username
            # Resolve role & rights
            try:
                from OrganizerDashboard.config_runtime import get_dashboard_config, get_config
                dashboard_config = get_dashboard_config()
                roles = dashboard_config.get('roles', {})
                # Determine role
                admin_user = get_config().get('dashboard_user', 'admin')
                role_name = 'admin' if username == admin_user else None
                if role_name is None:
                    for u in dashboard_config.get('users', []):
                        if u.get('username') == username:
                            role_name = u.get('role') or 'viewer'
                            break
                rights = roles.get(role_name or 'viewer', {})
                allowed = rights.get(right_name, False)
                if not allowed:
                    return Response('Forbidden: missing right', 403)
            except Exception:
                return Response('Forbidden: role resolution error', 403)
            return f(*args, **kwargs)
        return inner
    return wrapper
