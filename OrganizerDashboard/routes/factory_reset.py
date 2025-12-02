"""Factory reset route - restore all configurations to defaults."""

from flask import Blueprint, jsonify
import json
import sys
import os

routes_factory_reset = Blueprint('routes_factory_reset', __name__)


@routes_factory_reset.route('/api/factory-reset', methods=['POST'])
def factory_reset():
    """Reset all configurations to default values."""
    from OrganizerDashboard.auth.auth import requires_right
    
    @requires_right('manage_config')
    def _reset():
        try:
            main = sys.modules['__main__']
            
            # Get default configs from main module
            default_config = main.DEFAULT_CONFIG.copy()
            default_dashboard_config = main.DASHBOARD_CONFIG_DEFAULT.copy()
            
            # Reset organizer_config.json
            with open(main.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
            
            # Reset dashboard_config.json (preserve admin user)
            admin_user = getattr(main, 'ADMIN_USER', 'admin')
            reset_dashboard_config = {
                "users": [
                    {"username": admin_user, "role": "admin"}
                ],
                "roles": default_dashboard_config['roles'].copy(),
                "layout": default_dashboard_config['layout'].copy()
            }
            
            with open(main.DASHBOARD_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(reset_dashboard_config, f, indent=4)
            
            # Update in-memory configs
            main.config = default_config.copy()
            main.dashboard_config = reset_dashboard_config.copy()
            
            # Update package module reference
            pkg_module = sys.modules.get('OrganizerDashboard')
            if pkg_module:
                pkg_module.config = main.config
                pkg_module.dashboard_config = main.dashboard_config
            
            # Reinitialize auth manager
            from OrganizerDashboard.auth.auth import initialize_auth_manager
            initialize_auth_manager()
            
            return jsonify({
                'success': True,
                'message': 'All configurations reset to factory defaults. Please log in again if needed.'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Factory reset failed: {str(e)}'
            }), 500
    
    return _reset()
