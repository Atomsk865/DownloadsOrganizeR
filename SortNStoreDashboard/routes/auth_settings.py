"""Authentication settings route - view and update authentication configuration."""

from flask import Blueprint, jsonify, request
import json
import sys

routes_auth_settings = Blueprint('routes_auth_settings', __name__)


@routes_auth_settings.route("/api/auth/settings", methods=["GET"])
def get_auth_settings():
    """Get current authentication settings."""
    from SortNStoreDashboard.auth.auth import requires_auth
    
    @requires_auth
    def _get_auth_settings():
        main = sys.modules['__main__']
        config = main.config
        
        # Get available auth methods
        from SortNStoreDashboard.auth.auth import _auth_manager
        available_methods = _auth_manager.get_available_methods() if _auth_manager else ['basic']
        
        # Return sanitized config (don't expose passwords)
        ldap_config = config.get('ldap_config', {}).copy()
        if 'bind_password' in ldap_config:
            ldap_config['bind_password'] = '***' if ldap_config['bind_password'] else ''
        
        return jsonify({
            "auth_method": config.get('auth_method', 'basic'),
            "auth_fallback_enabled": config.get('auth_fallback_enabled', True),
            "available_methods": available_methods,
            "ldap_config": ldap_config,
            "windows_auth_config": config.get('windows_auth_config', {}),
            "dashboard_user": config.get('dashboard_user', 'admin')
        })
    
    return _get_auth_settings()


@routes_auth_settings.route("/api/auth/settings", methods=["POST"])
def update_auth_settings():
    """Update authentication settings."""
    from SortNStoreDashboard.auth.auth import requires_auth, initialize_auth_manager
    
    @requires_auth
    def _update_auth_settings():
        main = sys.modules['__main__']
        config = main.config
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update auth method
        if 'auth_method' in data:
            valid_methods = ['basic', 'ldap', 'windows']
            if data['auth_method'] not in valid_methods:
                return jsonify({"error": f"Invalid auth_method. Must be one of: {valid_methods}"}), 400
            config['auth_method'] = data['auth_method']
        
        # Update fallback setting
        if 'auth_fallback_enabled' in data:
            config['auth_fallback_enabled'] = bool(data['auth_fallback_enabled'])
        
        # Update LDAP config
        if 'ldap_config' in data:
            ldap_config = config.get('ldap_config', {})
            ldap_update = data['ldap_config']
            
            # Update only provided fields
            for field in ['server', 'base_dn', 'user_dn_template', 'use_ssl', 
                         'bind_dn', 'bind_password', 'search_filter', 'allowed_groups']:
                if field in ldap_update:
                    # Don't update password if it's masked
                    if field == 'bind_password' and ldap_update[field] == '***':
                        continue
                    ldap_config[field] = ldap_update[field]
            
            config['ldap_config'] = ldap_config
        
        # Update Windows auth config
        if 'windows_auth_config' in data:
            windows_config = config.get('windows_auth_config', {})
            windows_update = data['windows_auth_config']
            
            for field in ['domain', 'allowed_groups']:
                if field in windows_update:
                    windows_config[field] = windows_update[field]
            
            config['windows_auth_config'] = windows_config
        
        # Save config
        try:
            with open(main.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            return jsonify({"error": f"Failed to save config: {str(e)}"}), 500
        
        # Reinitialize auth manager with new config
        initialize_auth_manager()
        
        return jsonify({"success": True, "message": "Authentication settings updated successfully"})
    
    return _update_auth_settings()


@routes_auth_settings.route("/api/auth/test", methods=["POST"])
def test_auth():
    """Test authentication with provided credentials."""
    from SortNStoreDashboard.auth.auth import requires_auth, _auth_manager
    
    @requires_auth
    def _test_auth():
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"error": "Username and password required"}), 400
        
        username = data['username']
        password = data['password']
        method = data.get('method', 'basic')
        
        if not _auth_manager:
            return jsonify({"error": "Auth manager not initialized"}), 500
        
        # Test specific auth method
        provider = _auth_manager.providers.get(method)
        if not provider:
            return jsonify({"error": f"Auth method '{method}' not found"}), 400
        
        if not provider.is_available():
            return jsonify({
                "success": False, 
                "message": f"Auth method '{method}' is not available on this system"
            })
        
        try:
            result = provider.authenticate(username, password)
            return jsonify({
                "success": result,
                "message": "Authentication successful" if result else "Authentication failed"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Authentication error: {str(e)}"
            })
    
    return _test_auth()
