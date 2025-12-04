"""Centralized cache instance for the dashboard."""

# Placeholder that will be initialized by create_app()
cache = None


def init_cache(cache_instance):
    """Initialize the global cache instance."""
    global cache
    cache = cache_instance


def get_cache():
    """Get the global cache instance."""
    return cache
