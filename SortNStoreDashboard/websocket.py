"""
Real-Time Task Dashboard - WebSocket Integration

Provides WebSocket-based real-time updates for:
- Live task status monitoring
- Worker health tracking
- Performance metrics
- Task history streaming
- System diagnostics

Features:
- @flask-socketio: WebSocket communication
- @socket_events: Task status broadcasts
- Non-blocking real-time updates
- Graceful fallback when SocketIO not available
- Structured logging for all events

Usage:
    from SortNStoreDashboard.websocket import init_socketio
    
    socketio = init_socketio(app)
    
    # Events emitted to connected clients:
    - task_started
    - task_progress
    - task_completed
    - task_failed
    - worker_status
    - system_metrics
"""

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    SocketIO = None


# @flask-socketio: Initialize SocketIO
def init_socketio(app):
    """
    Initialize Flask-SocketIO for real-time updates.
    
    Args:
        app: Flask application instance
    
    Returns:
        SocketIO instance if available, None otherwise
    """
    if not SOCKETIO_AVAILABLE:
        return None
    
    try:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        
        socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='threading',
            ping_timeout=60,
            ping_interval=25,
            logger=False,  # Use structured logging instead
            engineio_logger=False,
        )
        
        log.info("websocket_socketio_initialized", status="enabled")
        
        return socketio
    
    except Exception as e:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        log.error("websocket_socketio_initialization_failed", error=str(e))
        return None


# Global SocketIO instance
socketio_instance = None


def set_socketio(socketio):
    """Set global SocketIO instance."""
    global socketio_instance
    socketio_instance = socketio


def get_socketio():
    """Get global SocketIO instance."""
    return socketio_instance


# @flask-socketio: Real-time event handlers
def register_socketio_events(socketio):
    """
    Register WebSocket event handlers.
    
    Args:
        socketio: SocketIO instance
    """
    if not socketio or not SOCKETIO_AVAILABLE:
        return
    
    from SortNStoreDashboard.structured_logging import get_logger
    log = get_logger(__name__)
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        log.info("websocket_client_connected")
        emit('response', {'data': 'Connected to task monitoring'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnect."""
        log.info("websocket_client_disconnected")
    
    @socketio.on('subscribe_tasks')
    def handle_subscribe_tasks():
        """Subscribe to task updates."""
        join_room('tasks')
        log.info("websocket_subscribed_tasks")
        emit('subscribed', {'channel': 'tasks'})
    
    @socketio.on('unsubscribe_tasks')
    def handle_unsubscribe_tasks():
        """Unsubscribe from task updates."""
        leave_room('tasks')
        log.info("websocket_unsubscribed_tasks")
    
    @socketio.on('subscribe_workers')
    def handle_subscribe_workers():
        """Subscribe to worker updates."""
        join_room('workers')
        log.info("websocket_subscribed_workers")
        emit('subscribed', {'channel': 'workers'})
    
    @socketio.on('unsubscribe_workers')
    def handle_unsubscribe_workers():
        """Unsubscribe from worker updates."""
        leave_room('workers')
        log.info("websocket_unsubscribed_workers")
    
    @socketio.on('subscribe_metrics')
    def handle_subscribe_metrics():
        """Subscribe to system metrics."""
        join_room('metrics')
        log.info("websocket_subscribed_metrics")
        emit('subscribed', {'channel': 'metrics'})


# @flask-socketio: Broadcast functions
def broadcast_task_started(task_id, path=None):
    """
    Broadcast task started event.
    
    Args:
        task_id: Task ID
        path: File path being organized
    """
    if not socketio_instance or not SOCKETIO_AVAILABLE:
        return
    
    from SortNStoreDashboard.structured_logging import get_logger
    log = get_logger(__name__)
    
    try:
        socketio_instance.emit('task_started', {
            'task_id': task_id,
            'path': path,
            'status': 'started',
            'timestamp': None,  # Set by client
        }, room='tasks')
        
        log.info("websocket_broadcast_task_started", task_id=task_id)
    
    except Exception as e:
        log.error("websocket_broadcast_failed", error=str(e))


def broadcast_task_progress(task_id, current, total, status='processing'):
    """
    Broadcast task progress update.
    
    Args:
        task_id: Task ID
        current: Current progress count
        total: Total items
        status: Progress status message
    """
    if not socketio_instance or not SOCKETIO_AVAILABLE:
        return
    
    from SortNStoreDashboard.structured_logging import get_logger
    log = get_logger(__name__)
    
    try:
        socketio_instance.emit('task_progress', {
            'task_id': task_id,
            'current': current,
            'total': total,
            'percentage': (current / total * 100) if total > 0 else 0,
            'status': status,
            'timestamp': None,
        }, room='tasks')
        
        log.debug("websocket_broadcast_task_progress", task_id=task_id, current=current)
    
    except Exception as e:
        log.error("websocket_broadcast_failed", error=str(e))


def broadcast_task_completed(task_id, result):
    """
    Broadcast task completed event.
    
    Args:
        task_id: Task ID
        result: Task result/summary
    """
    if not socketio_instance or not SOCKETIO_AVAILABLE:
        return
    
    from SortNStoreDashboard.structured_logging import get_logger
    log = get_logger(__name__)
    
    try:
        socketio_instance.emit('task_completed', {
            'task_id': task_id,
            'status': 'completed',
            'result': result,
            'timestamp': None,
        }, room='tasks')
        
        log.info("websocket_broadcast_task_completed", task_id=task_id)
    
    except Exception as e:
        log.error("websocket_broadcast_failed", error=str(e))


def broadcast_task_failed(task_id, error):
    """
    Broadcast task failed event.
    
    Args:
        task_id: Task ID
        error: Error message
    """
    if not socketio_instance or not SOCKETIO_AVAILABLE:
        return
    
    from SortNStoreDashboard.structured_logging import get_logger
    log = get_logger(__name__)
    
    try:
        socketio_instance.emit('task_failed', {
            'task_id': task_id,
            'status': 'failed',
            'error': error,
            'timestamp': None,
        }, room='tasks')
        
        log.error("websocket_broadcast_task_failed", task_id=task_id, error=error)
    
    except Exception as e:
        log.error("websocket_broadcast_failed", error=str(e))


def broadcast_worker_status(workers_info):
    """
    Broadcast worker status update.
    
    Args:
        workers_info: List of worker status dicts
    """
    if not socketio_instance or not SOCKETIO_AVAILABLE:
        return
    
    from SortNStoreDashboard.structured_logging import get_logger
    log = get_logger(__name__)
    
    try:
        socketio_instance.emit('worker_status', {
            'workers': workers_info,
            'total': len(workers_info),
            'timestamp': None,
        }, room='workers')
        
        log.debug("websocket_broadcast_worker_status", count=len(workers_info))
    
    except Exception as e:
        log.error("websocket_broadcast_failed", error=str(e))


def broadcast_system_metrics(metrics):
    """
    Broadcast system metrics.
    
    Args:
        metrics: System metrics dict
    """
    if not socketio_instance or not SOCKETIO_AVAILABLE:
        return
    
    from SortNStoreDashboard.structured_logging import get_logger
    log = get_logger(__name__)
    
    try:
        socketio_instance.emit('system_metrics', {
            'metrics': metrics,
            'timestamp': None,
        }, room='metrics')
        
        log.debug("websocket_broadcast_system_metrics")
    
    except Exception as e:
        log.error("websocket_broadcast_failed", error=str(e))


def get_socketio_status():
    """
    Get WebSocket availability and status.
    
    Returns:
        dict with status information
    """
    return {
        'available': SOCKETIO_AVAILABLE,
        'enabled': socketio_instance is not None,
        'features': [
            'task_monitoring' if SOCKETIO_AVAILABLE else None,
            'worker_status' if SOCKETIO_AVAILABLE else None,
            'system_metrics' if SOCKETIO_AVAILABLE else None,
            'real_time_updates' if SOCKETIO_AVAILABLE else None,
        ] if SOCKETIO_AVAILABLE else [],
    }
