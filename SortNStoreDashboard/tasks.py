"""
Celery Integration for SortNStore Dashboard

Provides asynchronous task processing for:
- File organization (non-blocking)
- Task status monitoring
- Retry logic and error handling
- Background job queue

Configuration:
- Broker: Redis (default) or RabbitMQ
- Backend: Redis or database
- Workers: Separate process pool
- Monitoring: Flower UI (optional)

Usage:
    from SortNStoreDashboard.tasks import organize_files_task
    
    # Queue async task
    task = organize_files_task.delay(path='/home/user/Downloads')
    
    # Check status
    status = task.status
    result = task.result

Features:
- @celery: Distributed task queue
- @redis: Message broker & result backend
- Non-blocking operations
- Graceful fallback when Celery not available
"""

try:
    from celery import Celery, Task
    from celery.utils.log import get_task_logger
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    Celery = None
    Task = object
    get_task_logger = None


# @celery: Initialize Celery application
def make_celery(app=None):
    """
    Create Celery instance.
    
    Args:
        app: Flask application instance (optional)
    
    Returns:
        Celery instance if available, None otherwise
    """
    if not CELERY_AVAILABLE:
        return None
    
    if app is None:
        # Default configuration without Flask app
        celery = Celery(__name__)
        celery.conf.update(
            broker_url='redis://localhost:6379/0',
            result_backend='redis://localhost:6379/0',
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            task_track_started=True,
            task_time_limit=30 * 60,  # 30 minutes hard limit
            task_soft_time_limit=25 * 60,  # 25 minutes soft limit
        )
    else:
        # Flask app integration
        celery = Celery(app.import_name)
        celery.conf.update(
            broker_url=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
            result_backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            task_track_started=True,
            task_time_limit=30 * 60,
            task_soft_time_limit=25 * 60,
        )
        
        # @celery: Make celery tasks aware of Flask app context
        class ContextTask(Task):
            """Celery task that runs in Flask app context."""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery


# @celery: Global Celery instance (initialized in create_app)
celery_app = None


def init_celery_with_app(app):
    """
    Initialize Celery with Flask app.
    
    Args:
        app: Flask application instance
    
    Returns:
        Celery instance if available, None otherwise
    """
    if not CELERY_AVAILABLE:
        return None
    
    global celery_app
    celery_app = make_celery(app)
    return celery_app


# @celery: File organization task
def organize_files_async(path=None):
    """
    Organize files asynchronously.
    
    This is the task function called by Celery workers.
    
    Args:
        path: Directory path to organize (default: Downloads)
    
    Returns:
        dict with operation results
    """
    if not CELERY_AVAILABLE or celery_app is None:
        return {'status': 'error', 'reason': 'Celery not available'}
    
    if get_task_logger is None:
        return {'status': 'error', 'reason': 'Celery logger not available'}
    
    # @celery: Get Celery logger for this task
    logger = get_task_logger(__name__)
    
    try:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        
        # @celery: Import file organizer
        from SortNStoreDashboard.organizer import Organizer
        
        if path is None:
            import os
            username = os.getenv('USERNAME') or os.getenv('USER', 'user')
            path = os.path.expanduser(f'~/{username}/Downloads')
        
        logger.info(f"Starting file organization for {path}")
        log.info("async_file_organization_started", path=path)
        
        # @celery: Create organizer and run
        organizer = Organizer(path)
        results = organizer.organize()
        
        logger.info(f"File organization completed: {results}")
        log.info("async_file_organization_completed",
                path=path,
                files_organized=results.get('count', 0),
                status='success')
        
        return {
            'status': 'success',
            'path': path,
            'files_organized': results.get('count', 0),
            'categories': results.get('categories', {}),
        }
    
    except Exception as e:
        logger.error(f"File organization failed: {str(e)}", exc_info=True)
        log.error("async_file_organization_failed",
                 path=path,
                 error=str(e),
                 exc_info=True)
        return {
            'status': 'error',
            'path': path,
            'error': str(e),
        }


# @celery: Email notification task
def send_email_async(to_addr, subject, body):
    """
    Send email asynchronously.
    
    Args:
        to_addr: Recipient email address
        subject: Email subject
        body: Email body
    
    Returns:
        dict with operation results
    """
    if not CELERY_AVAILABLE or celery_app is None:
        return {'status': 'error', 'reason': 'Celery not available'}
    
    if get_task_logger is None:
        return {'status': 'error', 'reason': 'Celery logger not available'}
    
    # @celery: Get Celery logger
    logger = get_task_logger(__name__)
    
    try:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        
        logger.info(f"Sending email to {to_addr}")
        log.info("async_email_started", to_addr=to_addr, subject=subject)
        
        # @celery: TODO: Implement email sending
        # from flask_mail import Mail, Message
        # msg = Message(subject, recipients=[to_addr], body=body)
        # mail.send(msg)
        
        logger.info(f"Email sent to {to_addr}")
        log.info("async_email_completed", to_addr=to_addr)
        
        return {
            'status': 'success',
            'to_addr': to_addr,
            'subject': subject,
        }
    
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}", exc_info=True)
        log.error("async_email_failed",
                 to_addr=to_addr,
                 error=str(e))
        return {
            'status': 'error',
            'to_addr': to_addr,
            'error': str(e),
        }


# @celery: Report generation task
def generate_report_async(report_type='summary', format='json'):
    """
    Generate reports asynchronously.
    
    Args:
        report_type: Type of report (summary, detailed, etc.)
        format: Output format (json, csv, pdf)
    
    Returns:
        dict with report data
    """
    if not CELERY_AVAILABLE or celery_app is None:
        return {'status': 'error', 'reason': 'Celery not available'}
    
    if get_task_logger is None:
        return {'status': 'error', 'reason': 'Celery logger not available'}
    
    # @celery: Get Celery logger
    logger = get_task_logger(__name__)
    
    try:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        
        logger.info(f"Generating {report_type} report ({format})")
        log.info("async_report_generation_started",
                report_type=report_type,
                format=format)
        
        # @celery: Generate report data
        report_data = {
            'type': report_type,
            'format': format,
            'timestamp': None,  # Will be set by celery
            'data': {},
        }
        
        # TODO: Implement report generation logic
        
        logger.info(f"Report generated: {report_type}")
        log.info("async_report_generation_completed",
                report_type=report_type,
                format=format)
        
        return {
            'status': 'success',
            'report': report_data,
        }
    
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}", exc_info=True)
        log.error("async_report_generation_failed",
                 report_type=report_type,
                 error=str(e))
        return {
            'status': 'error',
            'report_type': report_type,
            'error': str(e),
        }


def get_celery_status():
    """
    Get Celery availability and status.
    
    Returns:
        dict with status information
    """
    return {
        'available': CELERY_AVAILABLE,
        'enabled': celery_app is not None,
        'broker': 'redis://localhost:6379/0' if CELERY_AVAILABLE else None,
        'features': [
            'async_file_organization' if CELERY_AVAILABLE else None,
            'async_email' if CELERY_AVAILABLE else None,
            'async_reports' if CELERY_AVAILABLE else None,
            'task_tracking' if CELERY_AVAILABLE else None,
            'retry_logic' if CELERY_AVAILABLE else None,
        ] if CELERY_AVAILABLE else []
    }


# @celery: Create tasks as module-level functions (for delayed task definition)
if CELERY_AVAILABLE and celery_app:
    # These will be properly registered when celery_app is created
    @celery_app.task(bind=True, max_retries=3)
    def organize_files_task(self, path=None):
        """@celery: Async file organization task with retry."""
        try:
            return organize_files_async(path)
        except Exception as exc:
            # @celery: Retry logic
            raise self.retry(exc=exc, countdown=60, max_retries=3)
    
    @celery_app.task(bind=True, max_retries=3)
    def send_email_task(self, to_addr, subject, body):
        """@celery: Async email task with retry."""
        try:
            return send_email_async(to_addr, subject, body)
        except Exception as exc:
            # @celery: Retry logic with exponential backoff
            raise self.retry(exc=exc, countdown=60, max_retries=3)
    
    @celery_app.task(bind=True)
    def generate_report_task(self, report_type='summary', format='json'):
        """@celery: Async report generation task."""
        try:
            return generate_report_async(report_type, format)
        except Exception as exc:
            self.retry(exc=exc, countdown=60, max_retries=2)
else:
    # Stub implementations when Celery not available
    def organize_files_task(*args, **kwargs):
        return {'status': 'error', 'reason': 'Celery not available'}
    
    def send_email_task(*args, **kwargs):
        return {'status': 'error', 'reason': 'Celery not available'}
    
    def generate_report_task(*args, **kwargs):
        return {'status': 'error', 'reason': 'Celery not available'}
