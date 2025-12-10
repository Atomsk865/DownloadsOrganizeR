"""API endpoints for controlling organizer service enablement."""

from flask import Blueprint, jsonify, request
from SortNStoreDashboard.auth.auth import requires_right
from SortNStoreDashboard.config_runtime import get_config, save_config, get_dashboard_config, save_dashboard_config

routes_organizer_control = Blueprint('routes_organizer_control', __name__)

@routes_organizer_control.route('/api/organizer/status', methods=['GET'])
@requires_right('view_metrics')
def get_organizer_status():
    """Get current organizer enablement status."""
    try:
        config = get_config()
        dash_cfg = get_dashboard_config()
        
        organizer_enabled = config.get('organizer_enabled', False)
        destination_mode = config.get('destination_mode', 'subfolder')
        base_destination = config.get('base_destination', '')
        watch_folders = config.get('watch_folders', [])
        
        return jsonify({
            'success': True,
            'organizer_enabled': organizer_enabled,
            'destination_mode': destination_mode,
            'base_destination': base_destination,
            'watch_folders': watch_folders,
            'setup_completed': dash_cfg.get('setup_completed', False)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@routes_organizer_control.route('/api/organizer/enable', methods=['POST'])
@requires_right('manage_service')
def enable_organizer():
    """Enable the organizer service."""
    try:
        data = request.get_json() or {}
        enabled = data.get('enabled', True)
        
        config = get_config()
        dash_cfg = get_dashboard_config()
        
        # Validate that setup is complete
        if not dash_cfg.get('setup_completed', False):
            return jsonify({
                'success': False,
                'error': 'Setup must be completed before enabling the organizer'
            }), 400
        
        # Validate watch folders exist if enabling
        if enabled:
            watch_folders = config.get('watch_folders', [])
            if not watch_folders:
                return jsonify({
                    'success': False,
                    'error': 'At least one watch folder must be configured before enabling the organizer'
                }), 400
            
            # Validate custom destination if in custom mode
            destination_mode = config.get('destination_mode', 'subfolder')
            if destination_mode == 'custom':
                base_destination = config.get('base_destination', '').strip()
                if not base_destination:
                    return jsonify({
                        'success': False,
                        'error': 'Base destination path required when using custom destination mode'
                    }), 400
        
        # Update both configs
        config['organizer_enabled'] = enabled
        dash_cfg['organizer_enabled'] = enabled
        
        save_config()
        save_dashboard_config()
        
        status_msg = 'enabled' if enabled else 'disabled'
        restart_msg = ' Restart the service for changes to take effect.' if enabled else ''
        
        return jsonify({
            'success': True,
            'organizer_enabled': enabled,
            'message': f'Organizer service {status_msg} successfully.{restart_msg}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@routes_organizer_control.route('/api/organizer/config', methods=['POST'])
@requires_right('manage_config')
def update_organizer_config():
    """Update organizer configuration (destination mode, watch folders, etc.)."""
    try:
        data = request.get_json() or {}
        
        config = get_config()
        
        # Update destination settings if provided
        if 'destination_mode' in data:
            destination_mode = data['destination_mode']
            if destination_mode not in ['subfolder', 'custom']:
                return jsonify({'success': False, 'error': 'Invalid destination_mode'}), 400
            config['destination_mode'] = destination_mode
        
        if 'base_destination' in data:
            config['base_destination'] = data['base_destination'].strip()
        
        if 'watch_folders' in data:
            watch_folders = data['watch_folders']
            if not isinstance(watch_folders, list):
                return jsonify({'success': False, 'error': 'watch_folders must be a list'}), 400
            config['watch_folders'] = watch_folders
        
        save_config()
        
        return jsonify({
            'success': True,
            'message': 'Organizer configuration updated successfully. Restart the service for changes to take effect.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
