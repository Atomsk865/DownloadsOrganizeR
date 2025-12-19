"""
Centralized Caching Configuration - Flask-Caching with Redis Backend

@flask-caching: Production-grade caching with Redis
- Distributed caching across multiple workers
- Automatic TTL management
- Memoization for expensive function calls
- Type-safe decorators
- Built-in cache invalidation

Features:
- @cache.cached(): Cache function results by key prefix
- @cache.memoize(): Cache by function arguments
- @cache.delete_memoized(): Invalidate specific cached result
- @cache.clear(): Clear entire cache
- Per-function and global timeout configuration
- Thread-safe operations
- Redis connection pooling

Usage:
    from SortNStoreDashboard.caching_config import cache
    
    @cache.cached(timeout=60, key_prefix='tasks_list')
    def get_all_tasks():
        return expensive_query()
    
    @cache.memoize(timeout=300)
    def get_user_tasks(user_id):
        return database.query(user_id)
    
    # Invalidate
    cache.delete_memoized(get_user_tasks, 123)
    cache.clear()
"""

try:
    from flask_caching import Cache
    FLASK_CACHING_AVAILABLE = True
except ImportError:
    FLASK_CACHING_AVAILABLE = False
    Cache = None


# @flask-caching: Centralized cache instance
cache = None


def init_cache(app, config=None):
    """
    Initialize Flask-Caching with Redis backend.
    
    Args:
        app: Flask application instance
        config: Optional cache configuration dict
    
    Returns:
        Cache instance if successful, None otherwise
    """
    global cache
    
    if not FLASK_CACHING_AVAILABLE:
        try:
            from SortNStoreDashboard.structured_logging import get_logger
            log = get_logger(__name__)
            log.warning("flask_caching_not_available", 
                       message="Flask-Caching not installed, using simple dict cache")
        except:
            pass
        
        # Fallback to simple dict cache
        cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
        return cache
    
    try:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        
        # Default configuration - Redis backend
        default_config = {
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': 'redis://localhost:6379/0',
            'CACHE_DEFAULT_TIMEOUT': 300,
            'CACHE_REDIS_DB': 0,
            'CACHE_REDIS_IGNORE_EXCEPTIONS': True,  # Don't fail if Redis down
        }
        
        # Merge with provided config
        if config:
            default_config.update(config)
        
        app.config.update(default_config)
        
        cache = Cache(app)
        
        log.info("flask_caching_initialized", 
                backend=default_config.get('CACHE_TYPE'),
                redis_url=default_config.get('CACHE_REDIS_URL', 'N/A'))
        
        return cache
    
    except Exception as e:
        from SortNStoreDashboard.structured_logging import get_logger
        log = get_logger(__name__)
        log.error("flask_caching_initialization_failed", error=str(e))
        
        # Fallback to simple cache
        cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
        return cache


def get_cache():
    """Get the global cache instance."""
    return cache


def cache_key_builder(*args, **kwargs):
    """
    Build cache key from function arguments.
    
    Handles:
    - Positional arguments
    - Keyword arguments
    - Flask request context
    """
    try:
        from flask import request
        # Include request path in cache key for route-specific caching
        key_parts = [request.path]
    except:
        key_parts = []
    
    key_parts.extend(str(a) for a in args)
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    
    return ':'.join(key_parts)
