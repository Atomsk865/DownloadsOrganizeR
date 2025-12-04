"""
Server-Sent Events (SSE) Streams
Real-time push updates for dashboard metrics
"""

from flask import Blueprint, Response, stream_with_context
import json
import time
import psutil

bp = Blueprint('sse_streams', __name__)

# Import require_auth from duplicates
def require_auth(f):
    """Decorator to require authentication for routes."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import session, redirect, url_for
        if 'user' not in session:
            return redirect(url_for('routes_login.login'))
        return f(*args, **kwargs)
    return decorated

def format_sse(data: dict, event: str = 'message') -> str:
    """Format data as SSE message"""
    msg = f"event: {event}\n"
    msg += f"data: {json.dumps(data)}\n\n"
    return msg

@bp.route('/stream/metrics')
@require_auth
def stream_metrics():
    """
    SSE stream for real-time system metrics
    Sends updates every 2 seconds
    """
    def generate():
        try:
            while True:
                try:
                    # Gather metrics
                    cpu = psutil.cpu_percent(interval=0.5)
                    mem = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    # Try to get GPU info if available
                    gpu_info = None
                    try:
                        import GPUtil
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            gpu = gpus[0]
                            gpu_info = {
                                'name': gpu.name,
                                'load': round(gpu.load * 100, 1),
                                'memory_used': round(gpu.memoryUsed, 1),
                                'memory_total': round(gpu.memoryTotal, 1),
                                'temperature': round(gpu.temperature, 1) if gpu.temperature else None
                            }
                    except (ImportError, Exception):
                        pass
                    
                    metrics = {
                        'timestamp': int(time.time() * 1000),
                        'cpu': round(cpu, 1),
                        'memory': {
                            'percent': round(mem.percent, 1),
                            'used_gb': round(mem.used / (1024**3), 2),
                            'total_gb': round(mem.total / (1024**3), 2)
                        },
                        'disk': {
                            'percent': round(disk.percent, 1),
                            'used_gb': round(disk.used / (1024**3), 2),
                            'free_gb': round(disk.free / (1024**3), 2),
                            'total_gb': round(disk.total / (1024**3), 2)
                        }
                    }
                    
                    if gpu_info:
                        metrics['gpu'] = gpu_info
                    
                    yield format_sse(metrics, 'metrics')
                    
                except Exception as e:
                    # Send error event but keep stream alive
                    yield format_sse({'error': str(e)}, 'error')
                
                time.sleep(2)  # Update every 2 seconds
                
        except GeneratorExit:
            # Client disconnected
            pass
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',  # Disable nginx buffering
            'Connection': 'keep-alive'
        }
    )

@bp.route('/stream/notifications')
@require_auth
def stream_notifications():
    """
    SSE stream for real-time notifications
    Checks for new notifications every 10 seconds
    """
    def generate():
        try:
            import os
            notification_file = 'notification_history.json'
            last_check = time.time()
            
            while True:
                try:
                    # Check if notification file was modified
                    if os.path.exists(notification_file):
                        mod_time = os.path.getmtime(notification_file)
                        if mod_time > last_check:
                            # File was updated, send notification
                            with open(notification_file, 'r') as f:
                                data = json.load(f)
                                yield format_sse({
                                    'notifications': data.get('notifications', []),
                                    'unread': data.get('unread', 0)
                                }, 'notifications')
                            last_check = time.time()
                    
                except Exception as e:
                    yield format_sse({'error': str(e)}, 'error')
                
                time.sleep(10)  # Check every 10 seconds
                
        except GeneratorExit:
            pass
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

@bp.route('/stream/file-activity')
@require_auth
def stream_file_activity():
    """
    SSE stream for real-time file organization activity
    Monitors file history for new entries
    """
    def generate():
        try:
            from OrganizerDashboard.routes.statistics import load_file_moves
            last_count = 0
            
            while True:
                try:
                    moves = load_file_moves()
                    current_count = len(moves)
                    
                    if current_count > last_count:
                        # New files organized
                        new_files = moves[:current_count - last_count]
                        yield format_sse({
                            'new_files': new_files,
                            'total_count': current_count
                        }, 'file-activity')
                        last_count = current_count
                    
                except Exception as e:
                    yield format_sse({'error': str(e)}, 'error')
                
                time.sleep(5)  # Check every 5 seconds
                
        except GeneratorExit:
            pass
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )
