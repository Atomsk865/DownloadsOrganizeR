"""
Celery Task API Blueprint

REST API endpoints for Celery task management:
- POST /api/organize - Queue file organization task
- GET /api/tasks/<id> - Get task status
- GET /api/tasks - List tasks
- DELETE /api/tasks/<id> - Cancel task
- GET /api/workers - Get worker status

Features:
- @celery: Async file organization endpoint
- @redis: Result backend queries
- Task status polling
- Worker health monitoring
"""

from flask import Blueprint, jsonify, request
from functools import wraps

# @celery: Import task functions
try:
    from SortNStoreDashboard.tasks import (
        organize_files_task,
        send_email_task,
        generate_report_task,
        CELERY_AVAILABLE,
    )
    from SortNStoreDashboard.task_monitoring import (
        get_task_status,
        cancel_task,
        get_worker_status,
        get_celery_monitoring_status,
    )
    from SortNStoreDashboard.structured_logging import get_logger
    CELERY_TASKS_AVAILABLE = True
except ImportError:
    CELERY_TASKS_AVAILABLE = False


# Create blueprint
tasks_bp = Blueprint('tasks', __name__, url_prefix='/api')
log = get_logger(__name__) if CELERY_TASKS_AVAILABLE else None


def require_celery(f):
    """Decorator to check if Celery is available."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not CELERY_AVAILABLE:
            return jsonify({
                'status': 'error',
                'message': 'Celery not available. Install via: pip install celery redis'
            }), 503
        return f(*args, **kwargs)
    return decorated_function


@tasks_bp.route('/organize', methods=['POST'])
@require_celery
def queue_organize_task():
    """
    Queue an async file organization task.
    
    POST body:
        {
            "path": "/home/user/Downloads"  (optional)
        }
    
    Returns:
        {
            "task_id": "abc123...",
            "status": "queued",
            "message": "File organization task queued"
        }
    """
    if log:
        log.info("organize_task_queued", endpoint="/api/organize")
    
    try:
        data = request.get_json() or {}
        path = data.get('path')
        
        # @celery: Queue async task
        task = organize_files_task.delay(path=path)
        
        if log:
            log.info("organize_task_submitted", task_id=task.id, path=path)
        
        return jsonify({
            'status': 'success',
            'message': 'File organization task queued',
            'task_id': task.id,
            'status_url': f'/api/tasks/{task.id}',
        }), 202
    
    except Exception as e:
        if log:
            log.error("organize_task_failed", error=str(e), exc_info=True)
        
        return jsonify({
            'status': 'error',
            'message': str(e),
        }), 500


@tasks_bp.route('/tasks/<task_id>', methods=['GET'])
@require_celery
def get_task_detail(task_id):
    """
    Get status and result of a task.
    
    Returns:
        {
            "task_id": "abc123...",
            "status": "SUCCESS|PENDING|FAILURE",
            "result": {...},
            "current": 50,
            "total": 100
        }
    """
    if log:
        log.info("get_task_status", task_id=task_id)
    
    try:
        status = get_task_status(task_id)
        return jsonify(status), 200
    
    except Exception as e:
        if log:
            log.error("get_task_failed", task_id=task_id, error=str(e))
        
        return jsonify({
            'status': 'error',
            'message': str(e),
        }), 500


@tasks_bp.route('/tasks/<task_id>', methods=['DELETE'])
@require_celery
def cancel_task_endpoint(task_id):
    """
    Cancel a pending task.
    
    Returns:
        {
            "status": "success",
            "message": "Task cancelled",
            "task_id": "abc123..."
        }
    """
    if log:
        log.info("cancel_task_requested", task_id=task_id)
    
    try:
        result = cancel_task(task_id)
        return jsonify(result), 200
    
    except Exception as e:
        if log:
            log.error("cancel_task_failed", task_id=task_id, error=str(e))
        
        return jsonify({
            'status': 'error',
            'message': str(e),
        }), 500


@tasks_bp.route('/tasks', methods=['GET'])
@require_celery
def list_tasks():
    """
    List recent tasks (placeholder).
    
    Query params:
        - limit: Max tasks to return (default: 50)
        - status: Filter by status (PENDING, SUCCESS, FAILURE)
    
    Returns:
        {
            "tasks": [...],
            "total": 5,
            "limit": 50
        }
    """
    if log:
        log.info("list_tasks_requested")
    
    try:
        limit = request.args.get('limit', 50, type=int)
        status = request.args.get('status', None)
        
        # @celery: Get task history
        # TODO: Implement task history query
        tasks = []
        
        return jsonify({
            'status': 'success',
            'tasks': tasks,
            'total': len(tasks),
            'limit': limit,
        }), 200
    
    except Exception as e:
        if log:
            log.error("list_tasks_failed", error=str(e))
        
        return jsonify({
            'status': 'error',
            'message': str(e),
        }), 500


@tasks_bp.route('/workers', methods=['GET'])
@require_celery
def get_workers_status():
    """
    Get status of all active Celery workers.
    
    Returns:
        {
            "status": "success",
            "workers": [
                {
                    "name": "celery@hostname",
                    "status": "online",
                    "active_tasks": 2,
                    "pool": {...}
                }
            ],
            "total": 1
        }
    """
    if log:
        log.info("get_workers_status")
    
    try:
        result = get_worker_status()
        return jsonify(result), 200
    
    except Exception as e:
        if log:
            log.error("get_workers_failed", error=str(e))
        
        return jsonify({
            'status': 'error',
            'message': str(e),
        }), 500


@tasks_bp.route('/celery/status', methods=['GET'])
def get_celery_status():
    """
    Get Celery system status.
    
    Returns:
        {
            "available": true,
            "enabled": true,
            "workers": 1,
            "broker": "redis://localhost:6379/0"
        }
    """
    if log:
        log.info("get_celery_status")
    
    try:
        status = get_celery_monitoring_status()
        return jsonify(status), 200
    
    except Exception as e:
        if log:
            log.error("celery_status_check_failed", error=str(e))
        
        return jsonify({
            'status': 'error',
            'message': str(e),
        }), 500


# @celery: Register blueprint
def register_tasks_blueprint(app):
    """Register tasks API blueprint with Flask app."""
    if CELERY_AVAILABLE:
        app.register_blueprint(tasks_bp)
        if log:
            log.info("tasks_blueprint_registered")
        return True
    return False
