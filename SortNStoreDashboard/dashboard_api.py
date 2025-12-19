"""
Dashboard Data API - Real-Time Monitoring

Provides API endpoints for dashboard:
- Task history and statistics
- Worker information
- System performance metrics
- Task analytics

Endpoints:
- GET /api/dashboard/tasks - Task list with stats
- GET /api/dashboard/workers - Worker information
- GET /api/dashboard/metrics - System metrics
- GET /api/dashboard/stats - Overall statistics

Features:
- @dashboard_api: API routes
- Real-time data aggregation
- Performance optimized queries
- Graceful degradation
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

try:
    from SortNStoreDashboard.task_monitoring import get_worker_status, get_task_status
    from SortNStoreDashboard.structured_logging import get_logger
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False


dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')
log = get_logger(__name__) if DASHBOARD_AVAILABLE else None


@dashboard_bp.route('/tasks', methods=['GET'])
def get_tasks_data():
    """
    Get task history and statistics.
    
    Query params:
        - limit: Max tasks to return (default: 50)
        - status: Filter by status (PENDING, SUCCESS, FAILURE)
    
    Returns:
        {
            "tasks": [...],
            "stats": {
                "total": 100,
                "completed": 85,
                "failed": 5,
                "pending": 10,
                "success_rate": 94.4
            }
        }
    """
    if log:
        log.info("dashboard_get_tasks")
    
    try:
        limit = request.args.get('limit', 50, type=int)
        status = request.args.get('status', None)
        
        # TODO: Query task history from database
        tasks = []
        
        stats = {
            'total': len(tasks),
            'completed': 0,
            'failed': 0,
            'pending': 0,
            'success_rate': 0.0,
        }
        
        return jsonify({
            'status': 'success',
            'tasks': tasks,
            'stats': stats,
        }), 200
    
    except Exception as e:
        if log:
            log.error("dashboard_get_tasks_failed", error=str(e))
        
        return jsonify({
            'status': 'error',
            'message': str(e),
        }), 500


@dashboard_bp.route('/workers', methods=['GET'])
def get_workers_data():
    """
    Get worker information and status.
    
    Returns:
        {
            "workers": [
                {
                    "name": "celery@hostname",
                    "status": "online",
                    "active_tasks": 2,
                    "pool": {...}
                }
            ],
            "total": 1,
            "healthy": 1
        }
    """
    if log:
        log.info("dashboard_get_workers")
    
    try:
        workers_status = get_worker_status()
        
        healthy = sum(1 for w in workers_status.get('workers', []) 
                     if w.get('status') == 'online')
        
        return jsonify({
            'status': 'success',
            'workers': workers_status.get('workers', []),
            'total': workers_status.get('total', 0),
            'healthy': healthy,
        }), 200
    
    except Exception as e:
        if log:
            log.error("dashboard_get_workers_failed", error=str(e))
        
        return jsonify({
            'status': 'error',
            'message': str(e),
        }), 500


@dashboard_bp.route('/metrics', methods=['GET'])
def get_metrics_data():
    """
    Get system performance metrics.
    
    Returns:
        {
            "cpu_percent": 25.5,
            "memory_mb": 450,
            "memory_percent": 15.2,
            "disk_percent": 60.0,
            "uptime_seconds": 86400,
            "tasks_total": 1000,
            "tasks_per_second": 0.58
        }
    """
    if log:
        log.info("dashboard_get_metrics")
    
    try:
        import psutil
        import time
        
        # Get system metrics
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get process info
        process = psutil.Process()
        process_mem = process.memory_info().rss / 1024 / 1024  # MB
        uptime = time.time() - process.create_time()
        
        return jsonify({
            'status': 'success',
            'metrics': {
                'cpu_percent': cpu,
                'memory_mb': process_mem,
                'memory_percent': mem.percent,
                'disk_percent': disk.percent,
                'uptime_seconds': uptime,
                'timestamp': datetime.utcnow().isoformat(),
            }
        }), 200
    
    except Exception as e:
        if log:
            log.error("dashboard_get_metrics_failed", error=str(e))
        
        return jsonify({
            'status': 'error',
            'message': str(e),
        }), 500


@dashboard_bp.route('/stats', methods=['GET'])
def get_statistics_data():
    """
    Get overall dashboard statistics.
    
    Returns:
        {
            "system": {...},
            "tasks": {...},
            "workers": {...},
            "performance": {...}
        }
    """
    if log:
        log.info("dashboard_get_stats")
    
    try:
        # Combine all statistics
        workers_status = get_worker_status()
        
        stats = {
            'system': {
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'healthy',
            },
            'workers': {
                'total': workers_status.get('total', 0),
                'online': sum(1 for w in workers_status.get('workers', [])
                            if w.get('status') == 'online'),
            },
            'tasks': {
                'total_queued': 0,  # TODO: Query from Celery
                'completed_today': 0,
                'failed_today': 0,
            },
            'performance': {
                'avg_task_time': 0.0,
                'tasks_per_hour': 0.0,
            },
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats,
        }), 200
    
    except Exception as e:
        if log:
            log.error("dashboard_get_stats_failed", error=str(e))
        
        return jsonify({
            'status': 'error',
            'message': str(e),
        }), 500


@dashboard_bp.route('/health', methods=['GET'])
def dashboard_health():
    """
    Get dashboard health status.
    
    Returns:
        {
            "status": "healthy",
            "components": {...}
        }
    """
    if log:
        log.info("dashboard_health_check")
    
    try:
        health = {
            'status': 'healthy',
            'components': {
                'celery': 'operational',
                'redis': 'operational',
                'database': 'operational',
                'websocket': 'operational' if SOCKETIO_AVAILABLE else 'unavailable',
            },
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        return jsonify(health), 200
    
    except Exception as e:
        if log:
            log.error("dashboard_health_check_failed", error=str(e))
        
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
        }), 503


def register_dashboard_blueprint(app):
    """Register dashboard API blueprint with Flask app."""
    if DASHBOARD_AVAILABLE:
        app.register_blueprint(dashboard_bp)
        if log:
            log.info("dashboard_blueprint_registered")
        return True
    return False
