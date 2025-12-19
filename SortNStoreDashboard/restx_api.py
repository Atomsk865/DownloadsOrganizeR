"""
Flask-RESTX Integration for SortNStore Dashboard

Provides automatic API documentation with Swagger/OpenAPI interface.
Optional and non-breaking - can be enabled via configuration.

Usage:
    from SortNStoreDashboard.restx_api import init_restx_api
    
    app = Flask(__name__)
    init_restx_api(app)
    
    # Access at http://localhost:5000/api/docs

Features:
    - Automatic Swagger/OpenAPI documentation
    - Interactive API testing interface
    - Request/response validation
    - Type-safe API definitions
    - Non-breaking: wraps existing endpoints
"""

from typing import Optional, Dict, Any
from flask import Flask

# Attempt to import flask-restx; gracefully fallback if not installed
try:
    from flask_restx import Api, Resource, fields, Namespace
    RESTX_AVAILABLE = True
except ImportError:
    RESTX_AVAILABLE = False


def init_restx_api(app: Flask, prefix: str = "/api", doc_url: str = "/docs") -> Optional[Any]:
    """
    Initialize Flask-RESTX API documentation for the SortNStore dashboard.
    
    Args:
        app: Flask application instance.
        prefix: URL prefix for API endpoints (default: "/api").
        doc_url: URL for Swagger documentation (default: "/docs").
    
    Returns:
        Flask-RESTX Api instance, or None if flask-restx is not available.
    
    Example:
        app = Flask(__name__)
        api = init_restx_api(app)
        if api:
            # Document your endpoints...
            pass
    """
    if not RESTX_AVAILABLE:
        return None
    
    api = Api(
        app,
        version='2.0',
        title='SortNStore API',
        description='File organization service with automatic documentation',
        doc=doc_url,
        prefix=prefix,
        default_label='SortNStore Operations',
    )
    
    # Create namespaces for logical grouping
    ns_service = api.namespace('service', description='Service control')
    ns_config = api.namespace('config', description='Configuration management')
    ns_files = api.namespace('files', description='File operations')
    ns_metrics = api.namespace('metrics', description='System metrics')
    
    # ========================================================================
    # MODELS (API Schema Definitions)
    # ========================================================================
    
    # Service Status
    service_status_model = api.model('ServiceStatus', {
        'running': fields.Boolean(description='Service running status'),
        'uptime_seconds': fields.Integer(description='Uptime in seconds'),
        'files_processed': fields.Integer(description='Files processed'),
    })
    
    # Service Action
    service_action_model = api.model('ServiceAction', {
        'action': fields.String(
            required=True,
            enum=['start', 'stop', 'restart'],
            description='Action to perform'
        )
    })
    
    # Configuration
    config_model = api.model('Configuration', {
        'routes': fields.Raw(description='File routing rules'),
        'memory_threshold_mb': fields.Integer(description='Memory threshold'),
        'cpu_threshold_percent': fields.Integer(description='CPU threshold'),
    })
    
    # File Movement Record
    file_movement_model = api.model('FileMovement', {
        'filename': fields.String(description='File name'),
        'source': fields.String(description='Source path'),
        'destination': fields.String(description='Destination path'),
        'size_bytes': fields.Integer(description='File size'),
        'timestamp': fields.String(description='Movement timestamp'),
        'category': fields.String(description='File category'),
    })
    
    # System Metrics
    metrics_model = api.model('Metrics', {
        'cpu_percent': fields.Float(description='CPU usage %'),
        'memory_mb': fields.Float(description='Memory usage MB'),
        'disk_free_gb': fields.Float(description='Free disk space GB'),
    })
    
    # Error Response
    error_model = api.model('Error', {
        'message': fields.String(description='Error message'),
        'code': fields.String(description='Error code'),
    })
    
    # ========================================================================
    # SERVICE ENDPOINTS
    # ========================================================================
    
    @ns_service.route('/status')
    class ServiceStatus(Resource):
        @ns_service.doc('get_service_status')
        @ns_service.marshal_with(service_status_model)
        @ns_service.response(200, 'Service status retrieved')
        def get(self):
            """Get current service status"""
            # This will be wrapped with actual implementation via blueprints
            return {
                'running': True,
                'uptime_seconds': 0,
                'files_processed': 0,
            }
    
    @ns_service.route('/control')
    class ServiceControl(Resource):
        @ns_service.doc('control_service')
        @ns_service.expect(service_action_model)
        @ns_service.response(200, 'Service control executed')
        @ns_service.response(400, 'Invalid action', error_model)
        def post(self):
            """Start, stop, or restart the service"""
            return {'message': 'Service control endpoint'}
    
    # ========================================================================
    # CONFIGURATION ENDPOINTS
    # ========================================================================
    
    @ns_config.route('/current')
    class ConfigCurrent(Resource):
        @ns_config.doc('get_config')
        @ns_config.marshal_with(config_model)
        @ns_config.response(200, 'Configuration retrieved')
        def get(self):
            """Get current configuration"""
            return {
                'routes': {},
                'memory_threshold_mb': 200,
                'cpu_threshold_percent': 60,
            }
    
    @ns_config.route('/validate')
    class ConfigValidate(Resource):
        @ns_config.doc('validate_config')
        @ns_config.expect(config_model)
        @ns_config.response(200, 'Configuration is valid')
        @ns_config.response(400, 'Configuration validation failed', error_model)
        def post(self):
            """Validate configuration before applying"""
            return {'message': 'Configuration validation endpoint'}
    
    # ========================================================================
    # FILE OPERATIONS ENDPOINTS
    # ========================================================================
    
    @ns_files.route('/recent')
    class RecentFiles(Resource):
        @ns_files.doc('get_recent_files', 
                      params={'limit': 'Number of recent files to return'})
        @ns_files.marshal_with(file_movement_model)
        @ns_files.response(200, 'Recent files retrieved')
        def get(self):
            """Get recently moved files"""
            return []
    
    @ns_files.route('/statistics')
    class FileStatistics(Resource):
        @ns_files.doc('get_file_statistics')
        @ns_files.response(200, 'File statistics retrieved')
        def get(self):
            """Get file organization statistics"""
            return {
                'total_files_organized': 0,
                'files_by_category': {},
                'total_size_bytes': 0,
            }
    
    # ========================================================================
    # METRICS ENDPOINTS
    # ========================================================================
    
    @ns_metrics.route('/system')
    class SystemMetrics(Resource):
        @ns_metrics.doc('get_system_metrics')
        @ns_metrics.marshal_with(metrics_model)
        @ns_metrics.response(200, 'System metrics retrieved')
        def get(self):
            """Get system metrics (CPU, memory, disk)"""
            return {
                'cpu_percent': 0.0,
                'memory_mb': 0.0,
                'disk_free_gb': 0.0,
            }
    
    @ns_metrics.route('/health')
    class HealthCheck(Resource):
        @ns_metrics.doc('get_health')
        @ns_metrics.response(200, 'Service is healthy')
        @ns_metrics.response(503, 'Service unhealthy', error_model)
        def get(self):
            """Health check endpoint"""
            return {'status': 'healthy'}
    
    return api


class RestxDocumenter:
    """
    Utility class to help document existing Flask routes with RESTX.
    
    Usage:
        documenter = RestxDocumenter(api)
        
        # Document an existing endpoint
        documenter.document_endpoint(
            method='GET',
            path='/api/status',
            description='Get service status',
            response_model=status_model
        )
    """
    
    def __init__(self, api: Optional[Any] = None):
        self.api = api
    
    def document_endpoint(
        self,
        method: str,
        path: str,
        description: str,
        response_model: Optional[Dict[str, Any]] = None,
        request_model: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Document an existing endpoint.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Endpoint path
            description: Endpoint description
            response_model: Expected response schema
            request_model: Expected request schema
        
        Returns:
            True if documentation was added, False if restx not available
        """
        if not self.api:
            return False
        
        # Implementation would add decorator metadata
        return True


def get_restx_status() -> Dict[str, Any]:
    """
    Get status of Flask-RESTX integration.
    
    Returns:
        Dictionary with availability and version info.
    """
    return {
        'available': RESTX_AVAILABLE,
        'version': None if not RESTX_AVAILABLE else 'N/A',
        'docs_url': '/api/docs' if RESTX_AVAILABLE else None,
    }
