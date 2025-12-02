from flask import Blueprint, jsonify, request, send_file
import json
import io
from datetime import datetime
from OrganizerDashboard.auth.auth import requires_right
from OrganizerDashboard.config_runtime import get_config, get_dashboard_config, save_config, save_dashboard_config

routes_config_backup = Blueprint('routes_config_backup', __name__)

@routes_config_backup.route('/api/config/export', methods=['GET'])
def export_config():
    """Export complete dashboard and organizer configuration as JSON."""
    @requires_right('manage_config')
    def _inner():
        try:
            # Gather all configs
            organizer_config = get_config()
            dashboard_config = get_dashboard_config()
            
            # Create export package with metadata
            export_data = {
                'export_version': '1.0',
                'export_timestamp': datetime.now().isoformat(),
                'application': 'DownloadsOrganizeR',
                'configs': {
                    'organizer': organizer_config,
                    'dashboard': dashboard_config
                }
            }
            
            # Create in-memory file
            json_str = json.dumps(export_data, indent=4)
            json_bytes = io.BytesIO(json_str.encode('utf-8'))
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'organizer_backup_{timestamp}.json'
            
            return send_file(
                json_bytes,
                mimetype='application/json',
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            return jsonify({'error': f'Export failed: {str(e)}'}), 500
    
    return _inner()


@routes_config_backup.route('/api/config/import', methods=['POST'])
def import_config():
    """Import and restore configuration from uploaded JSON file."""
    @requires_right('manage_config')
    def _inner():
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not file.filename.endswith('.json'):
                return jsonify({'error': 'File must be a JSON file'}), 400
            
            # Read and parse JSON
            try:
                content = file.read().decode('utf-8')
                import_data = json.loads(content)
            except json.JSONDecodeError as e:
                return jsonify({'error': f'Invalid JSON format: {str(e)}'}), 400
            
            # Validate structure
            if 'configs' not in import_data:
                return jsonify({'error': 'Invalid backup file: missing configs section'}), 400
            
            configs = import_data['configs']
            
            if 'organizer' not in configs or 'dashboard' not in configs:
                return jsonify({'error': 'Invalid backup file: missing organizer or dashboard config'}), 400
            
            # Validate essential fields
            organizer = configs['organizer']
            dashboard = configs['dashboard']
            
            if not isinstance(organizer, dict) or not isinstance(dashboard, dict):
                return jsonify({'error': 'Invalid config structure'}), 400
            
            # Check for critical fields
            if 'routes' not in organizer:
                return jsonify({'error': 'Invalid organizer config: missing routes'}), 400
            
            if 'roles' not in dashboard or 'users' not in dashboard:
                return jsonify({'error': 'Invalid dashboard config: missing roles or users'}), 400
            
            # Import options
            import_organizer = request.form.get('import_organizer', 'true').lower() == 'true'
            import_dashboard = request.form.get('import_dashboard', 'true').lower() == 'true'
            
            results = {
                'organizer_imported': False,
                'dashboard_imported': False,
                'warnings': []
            }
            
            # Import organizer config
            if import_organizer:
                current_organizer = get_config()
                current_organizer.update(organizer)
                save_config()
                results['organizer_imported'] = True
            
            # Import dashboard config
            if import_dashboard:
                current_dashboard = get_dashboard_config()
                
                # Preserve current authenticated user if not in import
                import sys
                main = sys.modules.get('__main__')
                if main:
                    admin_user = getattr(main, 'ADMIN_USER', 'admin')
                    # Ensure admin user exists in imported config
                    user_exists = any(u.get('username') == admin_user for u in dashboard.get('users', []))
                    if not user_exists:
                        results['warnings'].append(f'Admin user "{admin_user}" not found in import, preserving current admin')
                        # Add current admin to imported users
                        current_admin = next((u for u in current_dashboard.get('users', []) if u.get('username') == admin_user), None)
                        if current_admin:
                            dashboard.setdefault('users', []).insert(0, current_admin)
                
                current_dashboard.update(dashboard)
                save_dashboard_config()
                results['dashboard_imported'] = True
            
            return jsonify({
                'success': True,
                'message': 'Configuration imported successfully',
                'details': results,
                'export_timestamp': import_data.get('export_timestamp', 'unknown'),
                'export_version': import_data.get('export_version', 'unknown')
            })
            
        except Exception as e:
            return jsonify({'error': f'Import failed: {str(e)}'}), 500
    
    return _inner()


@routes_config_backup.route('/api/config/validate', methods=['POST'])
def validate_config_file():
    """Validate an uploaded config file without importing."""
    @requires_right('manage_config')
    def _inner():
        try:
            if 'file' not in request.files:
                return jsonify({'valid': False, 'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'valid': False, 'error': 'No file selected'}), 400
            
            if not file.filename.endswith('.json'):
                return jsonify({'valid': False, 'error': 'File must be a JSON file'}), 400
            
            # Parse JSON
            try:
                content = file.read().decode('utf-8')
                import_data = json.loads(content)
            except json.JSONDecodeError as e:
                return jsonify({'valid': False, 'error': f'Invalid JSON: {str(e)}'}), 200
            
            # Validate structure
            errors = []
            warnings = []
            
            if 'configs' not in import_data:
                errors.append('Missing "configs" section')
            else:
                configs = import_data['configs']
                
                if 'organizer' not in configs:
                    errors.append('Missing organizer configuration')
                elif not isinstance(configs['organizer'], dict):
                    errors.append('Organizer config must be an object')
                elif 'routes' not in configs['organizer']:
                    errors.append('Organizer config missing "routes"')
                
                if 'dashboard' not in configs:
                    errors.append('Missing dashboard configuration')
                elif not isinstance(configs['dashboard'], dict):
                    errors.append('Dashboard config must be an object')
                else:
                    dashboard = configs['dashboard']
                    if 'roles' not in dashboard:
                        warnings.append('Dashboard config missing "roles"')
                    if 'users' not in dashboard:
                        warnings.append('Dashboard config missing "users"')
                    elif not isinstance(dashboard['users'], list):
                        errors.append('Dashboard users must be an array')
            
            if errors:
                return jsonify({
                    'valid': False,
                    'errors': errors,
                    'warnings': warnings
                }), 200
            
            return jsonify({
                'valid': True,
                'message': 'Configuration file is valid',
                'warnings': warnings,
                'export_timestamp': import_data.get('export_timestamp', 'unknown'),
                'export_version': import_data.get('export_version', 'unknown')
            })
            
        except Exception as e:
            return jsonify({'valid': False, 'error': f'Validation failed: {str(e)}'}), 500
    
    return _inner()
