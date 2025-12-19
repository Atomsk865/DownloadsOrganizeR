#!/usr/bin/env python3
"""
Flask-RESTX Integration Example for SortNStore

Purpose: Add automatic Swagger/OpenAPI documentation to API endpoints
Effort: Low (1-2 hours integration)
Benefits: 
  - Interactive API documentation
  - Automatic request/response validation
  - Better developer experience
  - Type-safe API definitions

Dependencies:
  pip install flask flask-restx

Usage:
  python flask_restx_example.py
  Open http://localhost:5001 to see Swagger UI

Integration Notes:
  - Non-breaking: Wraps existing endpoints
  - Opt-in: Can be enabled via config
  - Coexists with current dashboard
  - Easy to adopt incrementally
"""

from flask import Flask
from flask_restx import Api, Resource, fields, Namespace
from datetime import datetime

# ============================================================================
# SETUP
# ============================================================================

app = Flask(__name__)
app.config['RESTX_MASK_SWAGGER'] = False  # Show all fields in docs

# Create API with documentation
api = Api(
    app,
    version='2.0',
    title='SortNStore API',
    description='File organization service REST API with automatic documentation',
    doc='/api/docs',  # Swagger UI location
    prefix='/api'
)

# ============================================================================
# NAMESPACES (API Organization)
# ============================================================================

ns_service = api.namespace('service', description='Service control operations')
ns_config = api.namespace('config', description='Configuration management')
ns_files = api.namespace('files', description='File operations and history')
ns_metrics = api.namespace('metrics', description='System metrics and statistics')

# ============================================================================
# MODELS (API Schema Definitions)
# ============================================================================

# Service Status Model
service_status = api.model('ServiceStatus', {
    'running': fields.Boolean(description='Whether service is currently running'),
    'uptime_seconds': fields.Integer(description='Service uptime in seconds'),
    'files_organized': fields.Integer(description='Total files organized'),
    'last_activity': fields.String(description='ISO timestamp of last file movement'),
})

# Service Control Request
service_action = api.model('ServiceAction', {
    'action': fields.String(required=True, enum=['start', 'stop', 'restart'],
                           description='Action to perform on service')
})

# File Route Model
file_route = api.model('FileRoute', {
    'category': fields.String(required=True, description='File category name'),
    'extensions': fields.List(fields.String, description='List of file extensions'),
    'destination': fields.String(description='Destination folder path')
})

# Configuration Model
config_model = api.model('Configuration', {
    'routes': fields.List(fields.Nested(file_route), description='File routing rules'),
    'watch_folders': fields.List(fields.String, description='Folders to monitor'),
    'memory_threshold_mb': fields.Integer(description='Memory usage alert threshold'),
    'cpu_threshold_percent': fields.Integer(description='CPU usage alert threshold'),
})

# File Movement Record
file_movement = api.model('FileMovement', {
    'filename': fields.String(description='Name of the file'),
    'source': fields.String(description='Source folder path'),
    'destination': fields.String(description='Destination folder path'),
    'size_bytes': fields.Integer(description='File size in bytes'),
    'timestamp': fields.String(description='ISO timestamp of movement'),
    'category': fields.String(description='Detected file category')
})

# System Metrics Model
system_metrics = api.model('SystemMetrics', {
    'cpu_percent': fields.Float(description='Current CPU usage percentage'),
    'memory_mb': fields.Float(description='Current memory usage in MB'),
    'disk_free_gb': fields.Float(description='Available disk space in GB'),
    'uptime_seconds': fields.Integer(description='System uptime in seconds'),
})

# Error Model
error_model = api.model('Error', {
    'message': fields.String(description='Error message'),
    'code': fields.String(description='Error code'),
    'details': fields.Raw(description='Additional error details')
})

# ============================================================================
# SERVICE ENDPOINTS
# ============================================================================

@ns_service.route('/status')
class ServiceStatus(Resource):
    @ns_service.doc('get_service_status')
    @ns_service.marshal_with(service_status)
    @ns_service.response(200, 'Success')
    def get(self):
        """Get current service status"""
        # Mock data - replace with actual service check
        return {
            'running': True,
            'uptime_seconds': 86400,
            'files_organized': 1543,
            'last_activity': datetime.now().isoformat()
        }


@ns_service.route('/control')
class ServiceControl(Resource):
    @ns_service.doc('control_service')
    @ns_service.expect(service_action)
    @ns_service.marshal_with(service_status)
    @ns_service.response(200, 'Success')
    @ns_service.response(400, 'Invalid action', error_model)
    @ns_service.response(403, 'Insufficient permissions', error_model)
    def post(self):
        """Start, stop, or restart the service"""
        # Mock implementation - replace with actual service control
        action = api.payload.get('action')
        
        if action == 'start':
            # Start service logic
            pass
        elif action == 'stop':
            # Stop service logic
            pass
        elif action == 'restart':
            # Restart service logic
            pass
        else:
            api.abort(400, f"Invalid action: {action}")
        
        return {
            'running': action == 'start',
            'uptime_seconds': 0 if action == 'start' else 86400,
            'files_organized': 1543,
            'last_activity': datetime.now().isoformat()
        }


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@ns_config.route('/')
class Configuration(Resource):
    @ns_config.doc('get_configuration')
    @ns_config.marshal_with(config_model)
    @ns_config.response(200, 'Success')
    def get(self):
        """Get current configuration"""
        # Mock data - replace with actual config loading
        return {
            'routes': [
                {
                    'category': 'Images',
                    'extensions': ['jpg', 'png', 'gif', 'svg'],
                    'destination': 'C:\\Users\\Downloads\\Images'
                },
                {
                    'category': 'Documents',
                    'extensions': ['pdf', 'docx', 'txt'],
                    'destination': 'C:\\Users\\Downloads\\Documents'
                }
            ],
            'watch_folders': ['C:\\Users\\Downloads'],
            'memory_threshold_mb': 200,
            'cpu_threshold_percent': 60
        }
    
    @ns_config.doc('update_configuration')
    @ns_config.expect(config_model)
    @ns_config.marshal_with(config_model)
    @ns_config.response(200, 'Configuration updated')
    @ns_config.response(400, 'Invalid configuration', error_model)
    @ns_config.response(403, 'Insufficient permissions', error_model)
    def post(self):
        """Update configuration"""
        # Mock implementation - replace with actual config save
        config_data = api.payload
        
        # Validate configuration
        if not config_data.get('routes'):
            api.abort(400, "Routes are required")
        
        # Save configuration logic here
        
        return config_data


# ============================================================================
# FILE OPERATIONS ENDPOINTS
# ============================================================================

@ns_files.route('/recent')
class RecentFiles(Resource):
    @ns_files.doc('get_recent_files')
    @ns_files.marshal_list_with(file_movement)
    @ns_files.param('limit', 'Maximum number of records to return', type='integer', default=50)
    @ns_files.param('category', 'Filter by file category', type='string')
    @ns_files.response(200, 'Success')
    def get(self):
        """Get recently organized files"""
        # Mock data - replace with actual file history
        return [
            {
                'filename': 'document.pdf',
                'source': 'C:\\Users\\Downloads',
                'destination': 'C:\\Users\\Downloads\\Documents',
                'size_bytes': 1024000,
                'timestamp': datetime.now().isoformat(),
                'category': 'Documents'
            },
            {
                'filename': 'photo.jpg',
                'source': 'C:\\Users\\Downloads',
                'destination': 'C:\\Users\\Downloads\\Images',
                'size_bytes': 2048000,
                'timestamp': datetime.now().isoformat(),
                'category': 'Images'
            }
        ]


@ns_files.route('/stats')
class FileStats(Resource):
    @ns_files.doc('get_file_statistics')
    @ns_files.response(200, 'Success')
    def get(self):
        """Get file organization statistics"""
        # Mock data - replace with actual statistics
        return {
            'total_files_organized': 1543,
            'by_category': {
                'Images': 523,
                'Documents': 412,
                'Videos': 234,
                'Archives': 156,
                'Other': 218
            },
            'total_size_bytes': 15678234567,
            'average_file_size_bytes': 10156789
        }


# ============================================================================
# METRICS ENDPOINTS
# ============================================================================

@ns_metrics.route('/system')
class SystemMetrics(Resource):
    @ns_metrics.doc('get_system_metrics')
    @ns_metrics.marshal_with(system_metrics)
    @ns_metrics.response(200, 'Success')
    def get(self):
        """Get current system metrics"""
        # Mock data - replace with actual system metrics (psutil)
        return {
            'cpu_percent': 15.5,
            'memory_mb': 128.7,
            'disk_free_gb': 250.3,
            'uptime_seconds': 86400
        }


@ns_metrics.route('/health')
class HealthCheck(Resource):
    @ns_metrics.doc('health_check')
    @ns_metrics.response(200, 'Healthy')
    @ns_metrics.response(503, 'Unhealthy')
    def get(self):
        """Health check endpoint for monitoring"""
        # Simple health check - replace with actual checks
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        }


# ============================================================================
# INTEGRATION NOTES
# ============================================================================

"""
INTEGRATION INTO SORTNSTORE:

1. Install dependency:
   pip install flask-restx

2. Add to SortNStoreDashboard.py:
   
   from flask_restx import Api
   
   # After Flask app creation:
   api = Api(app, version='2.0', title='SortNStore API', 
             doc='/api/docs', prefix='/api')
   
3. Wrap existing endpoints:
   
   # Instead of:
   @app.route('/api/service/status')
   def service_status():
       return jsonify({'running': True})
   
   # Use:
   @ns_service.route('/status')
   class ServiceStatus(Resource):
       @ns_service.marshal_with(service_status_model)
       def get(self):
           return {'running': True}

4. Enable in config:
   
   {
     "enhanced_features": {
       "api_docs": true
     }
   }

5. Access Swagger UI:
   http://localhost:5000/api/docs

BENEFITS:
- Interactive API testing
- Automatic documentation
- Input validation
- Better error messages
- Type safety
- Developer-friendly

MIGRATION PATH:
- Add models for existing endpoints
- Wrap endpoints one at a time
- Keep old routes working
- Test thoroughly
- Update documentation
"""

# ============================================================================
# RUN EXAMPLE
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("Flask-RESTX Example Running")
    print("="*70)
    print("\n📚 Swagger UI: http://localhost:5001/api/docs")
    print("🔌 API Base: http://localhost:5001/api/")
    print("\nEndpoints:")
    print("  - GET  /api/service/status")
    print("  - POST /api/service/control")
    print("  - GET  /api/config/")
    print("  - POST /api/config/")
    print("  - GET  /api/files/recent")
    print("  - GET  /api/files/stats")
    print("  - GET  /api/metrics/system")
    print("  - GET  /api/metrics/health")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, port=5001)
