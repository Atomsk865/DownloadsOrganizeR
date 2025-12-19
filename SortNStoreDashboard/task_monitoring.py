"""
Celery Task Monitoring API

Provides REST endpoints for:
- Task status checking
- Task history
- Worker status
- Task result retrieval
- Task cancellation

Endpoints:
- GET /api/tasks/<task_id> - Get task status
- GET /api/tasks - List recent tasks
- DELETE /api/tasks/<task_id> - Cancel task
- GET /api/workers - Get worker status
- POST /api/organize - Queue file organization

Features:
- @celery: Task status tracking
- @redis: Result backend queries
- Real-time updates via status endpoint
- Task history logging
"""

try:
    from celery import Celery
    from celery.result import AsyncResult
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False


def get_task_status(task_id):
    """
    Get status of a Celery task.
    
    Args:
        task_id: Task ID to check
    
    Returns:
        dict with task status and result
    """
    if not CELERY_AVAILABLE:
        return {
            'status': 'unavailable',
            'message': 'Celery not available',
        }
    
    try:
        # @celery: Import celery app
        from SortNStoreDashboard.tasks import celery_app
        
        if celery_app is None:
            return {
                'status': 'unavailable',
                'message': 'Celery not initialized',
            }
        
        # @celery: Get AsyncResult for task
        result = AsyncResult(task_id, app=celery_app)
        
        response = {
            'task_id': task_id,
            'status': result.status,
            'current': result.info.get('current', 0) if isinstance(result.info, dict) else 0,
            'total': result.info.get('total', 100) if isinstance(result.info, dict) else 100,
        }
        
        if result.state == 'PENDING':
            response['result'] = 'Task pending...'
        elif result.state == 'PROGRESS':
            response['result'] = result.info.get('status', 'Processing...')
        elif result.state == 'SUCCESS':
            response['result'] = result.result
        elif result.state == 'FAILURE':
            response['result'] = str(result.info)
            response['error'] = str(result.info)
        
        return response
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
        }


def cancel_task(task_id):
    """
    Cancel a pending Celery task.
    
    Args:
        task_id: Task ID to cancel
    
    Returns:
        dict with cancellation status
    """
    if not CELERY_AVAILABLE:
        return {
            'status': 'error',
            'message': 'Celery not available',
        }
    
    try:
        # @celery: Import celery app
        from SortNStoreDashboard.tasks import celery_app
        
        if celery_app is None:
            return {
                'status': 'error',
                'message': 'Celery not initialized',
            }
        
        # @celery: Revoke task (cancel it)
        celery_app.control.revoke(task_id, terminate=True)
        
        return {
            'status': 'success',
            'message': f'Task {task_id} cancelled',
            'task_id': task_id,
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
        }


def get_worker_status():
    """
    Get status of all active Celery workers.
    
    Returns:
        dict with worker information
    """
    if not CELERY_AVAILABLE:
        return {
            'status': 'unavailable',
            'workers': [],
        }
    
    try:
        # @celery: Import celery app
        from SortNStoreDashboard.tasks import celery_app
        
        if celery_app is None:
            return {
                'status': 'unavailable',
                'workers': [],
            }
        
        # @celery: Query active workers
        inspect = celery_app.control.inspect()
        
        workers = {}
        
        # @celery: Get stats from all workers
        if inspect.stats():
            for worker_name, stats in inspect.stats().items():
                workers[worker_name] = {
                    'name': worker_name,
                    'status': 'online',
                    'pool': stats.get('pool', {}),
                    'total': stats.get('total', 0),
                }
        
        # @celery: Get active tasks
        if inspect.active():
            for worker_name, tasks in inspect.active().items():
                if worker_name in workers:
                    workers[worker_name]['active_tasks'] = len(tasks)
        
        return {
            'status': 'success',
            'workers': list(workers.values()),
            'total': len(workers),
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'workers': [],
        }


def get_task_history(limit=50):
    """
    Get history of recent tasks (from log).
    
    Args:
        limit: Maximum number of tasks to return
    
    Returns:
        list of task information
    """
    if not CELERY_AVAILABLE:
        return []
    
    try:
        # @celery: Get task history from structured logs
        from SortNStoreDashboard.structured_logging import get_logger
        
        log = get_logger('celery_tasks')
        
        # TODO: Query structured logs for task records
        # For now, return empty list
        return []
    
    except Exception:
        return []


def get_celery_monitoring_status():
    """
    Get overall Celery monitoring status.
    
    Returns:
        dict with monitoring information
    """
    if not CELERY_AVAILABLE:
        return {
            'available': False,
            'message': 'Celery not available',
        }
    
    try:
        # @celery: Check celery app
        from SortNStoreDashboard.tasks import celery_app
        
        return {
            'available': True,
            'enabled': celery_app is not None,
            'workers': get_worker_status()['total'],
            'broker': 'redis://localhost:6379/0' if celery_app else None,
        }
    
    except Exception as e:
        return {
            'available': False,
            'message': str(e),
        }
