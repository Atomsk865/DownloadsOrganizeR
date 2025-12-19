"""
Rate Limiting Configuration - Flask-Limiter with Redis Backend

@flask-limiter: Production-grade rate limiting
- Distributed rate limiting across multiple workers
- Redis-backed persistence
- Multiple rate limiting strategies (fixed-window, sliding-window, moving-window)
- Per-route and per-IP limiting
- Automatic 429 responses
- Exemption patterns
- Rate limit headers in responses

Strategies:
- "5 per hour" - Fixed window
- "5/hour" - Fixed window (alternative syntax)
- "100 per day, 50 per hour" - Multiple limits

Usage:
    from SortNStoreDashboard.rate_limiter_config import limiter
    
    @app.route('/api/expensive')
    @limiter.limit("5 per minute")
    def expensive_endpoint():
        return jsonify({'status': 'ok'})
    
    # Dynamic limits based on user
    @limiter.limit(lambda: '100/hour' if current_user.is_premium else '10/hour')
    def premium_endpoint():
        pass
    
    # Exempt specific routes
    limiter.exempt(cheap_endpoint)
"""

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    FLASK_LIMITER_AVAILABLE = True
except ImportError:
    FLASK_LIMITER_AVAILABLE = False
    Limiter = None
    get_remote_address = None


# @flask-limiter: Centralized limiter instance
limiter = None


def init_limiter(app, storage_uri=None, key_func=None):
    """
    Initialize Flask-Limiter with Redis backend.
    
    Args:
        app: Flask application instance
        storage_uri: Redis connection string (default: redis://localhost:6379)
        key_func: Function to extract rate limit key (default: get_remote_address)
    
    Returns:
        Limiter instance if successful, None otherwise
    """
    global limiter
    
    if not FLASK_LIMITER_AVAILABLE:
        try:
            from SortNStoreDashboard.structured_logging import get_logger
            log = get_logger(__name__)
            log.warning("flask_limiter_not_available",
                       message="Flask-Limiter not installed, rate limiting disabled")
        except:
            pass
        return None
    
    try:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        
        # Default storage URI - use existing Redis
        if storage_uri is None:
            storage_uri = "redis://localhost:6379"
        
        # Default key function - by IP address
        if key_func is None:
            key_func = get_remote_address
        
        # Try with Redis storage first, fallback to memory
        try:
            limiter = Limiter(
                app=app,
                key_func=key_func,
                storage_uri=storage_uri,
                storage_options={
                    "socket_connect_timeout": 5,
                    "socket_timeout": 5,
                    "retry_on_timeout": True,
                    "connection_pool_kwargs": {
                        "max_connections": 50,
                        "retry_on_timeout": True,
                    }
                },
                default_limits=["200 per day", "50 per hour"],
                in_memory_fallback_enabled=True,
                headers_enabled=True,
                swallow_errors=True,
            )
        except Exception as redis_error:
            # Fallback to in-memory storage
            log.warning("flask_limiter_redis_fallback", 
                       error=str(redis_error),
                       message="Falling back to in-memory rate limiting")
            limiter = Limiter(
                app=app,
                key_func=key_func,
                default_limits=["200 per day", "50 per hour"],
                headers_enabled=True,
                swallow_errors=True,
            )
        
        log.info("flask_limiter_initialized",
                storage_uri=storage_uri,
                key_func=key_func.__name__)
        
        return limiter
    
    except Exception as e:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        log.error("flask_limiter_initialization_failed", error=str(e))
        return None


def get_limiter():
    """Get the global limiter instance."""
    return limiter


def bypass_for_dev():
    """
    Check if rate limiting should be bypassed for development.
    
    Used to disable rate limiting in development environments.
    """
    import os
    return os.getenv('FLASK_ENV', 'production') == 'development'
