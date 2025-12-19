"""
Structured Logging Integration for SortNStore

Provides structured JSON logging using structlog with fallback to standard logging.
Can be optionally enabled via configuration.

Usage:
    from SortNStoreDashboard.structured_logging import get_logger, configure_logging
    
    # Configure once at startup
    configure_logging(use_json=True, log_level="INFO")
    
    # Use in any module
    log = get_logger(__name__)
    log.info("file_organized", 
             filename="report.pdf",
             destination="/Downloads/Documents",
             size_bytes=512000)
"""

import os
import sys
import logging
from typing import Optional, Dict, Any

# Attempt to import structlog; gracefully fallback if not installed
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


def configure_logging(
    use_json: bool = False,
    log_level: str = "INFO",
    log_file: Optional[str] = None
) -> None:
    """
    Configure structured logging for SortNStore.
    
    Args:
        use_json: If True, output JSON. If False, use colored console output.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional file path for log output. If None, uses stdout.
    
    Example:
        configure_logging(use_json=True, log_level="INFO")
    """
    if not STRUCTLOG_AVAILABLE:
        # Fallback to standard logging
        _configure_standard_logging(log_level, log_file)
        return
    
    # Shared processors for both formats
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            ],
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if use_json:
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging to work with structlog
    stream = _get_log_stream(log_file)
    logging.basicConfig(
        format="%(message)s",
        stream=stream,
        level=getattr(logging, log_level.upper()),
    )


def _configure_standard_logging(log_level: str, log_file: Optional[str] = None) -> None:
    """Fallback: Configure standard logging when structlog is not available."""
    stream = _get_log_stream(log_file)
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=stream,
        level=getattr(logging, log_level.upper()),
    )


def _get_log_stream(log_file: Optional[str]):
    """Get file or stdout stream for logging."""
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        return open(log_file, 'a', encoding='utf-8')
    return sys.stdout


def get_logger(name: Optional[str] = None) -> Any:
    """
    Get a logger instance.
    
    Returns structlog logger if available, otherwise standard logging wrapped in adapter.
    
    Args:
        name: Logger name (usually __name__ from calling module).
    
    Returns:
        Logger instance (structlog.BoundLogger or StructuredLoggerAdapter).
    
    Example:
        log = get_logger(__name__)
        log.info("operation_completed", duration_ms=1234)
    """
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        # Create adapter with standard logger directly
        adapter = StructuredLoggerAdapter(name or __name__)
        return adapter


def bind_context(**kwargs) -> Any:
    """
    Bind context variables to all subsequent log calls in this logger.
    
    Args:
        **kwargs: Key-value pairs to bind to context.
    
    Example:
        log = get_logger()
        log = log.bind(user="admin", request_id="req-123")
        log.info("action_performed")  # Will include user and request_id
    """
    if STRUCTLOG_AVAILABLE:
        log = structlog.get_logger()
        return log.bind(**kwargs)
    return None


class StructuredLoggerAdapter:
    """
    Adapter for logging to work uniformly with or without structlog.
    Provides a simple interface that works regardless of structlog availability.
    """
    
    def __init__(self, name: str = __name__):
        self.name = name
        # Always use standard logger as base, not recursive calls to get_logger
        self._logger = logging.getLogger(name)
        self._context: Dict[str, Any] = {}
    
    def bind(self, **kwargs) -> "StructuredLoggerAdapter":
        """Bind context variables."""
        self._context.update(kwargs)
        if STRUCTLOG_AVAILABLE and hasattr(self._logger, 'bind'):
            self._logger = self._logger.bind(**kwargs)
        return self
    
    def _log(self, level: str, msg: str, **kwargs) -> None:
        """Internal logging method."""
        all_kwargs = {**self._context, **kwargs}
        
        if STRUCTLOG_AVAILABLE:
            # Use structlog method
            method = getattr(self._logger, level.lower(), None)
            if method:
                method(msg, **all_kwargs)
        else:
            # Use standard logging with formatted message
            log_method = getattr(self._logger, level.lower(), None)
            if log_method:
                # Format message with kwargs for readability
                # Standard logging doesn't support kwargs, so format as string
                if all_kwargs:
                    kwargs_str = ' | '.join(f'{k}={v}' for k, v in all_kwargs.items())
                    formatted = f"{msg} | {kwargs_str}"
                else:
                    formatted = msg
                log_method(formatted)
    
    def debug(self, msg: str, **kwargs) -> None:
        """Log at DEBUG level."""
        self._log("DEBUG", msg, **kwargs)
    
    def info(self, msg: str, **kwargs) -> None:
        """Log at INFO level."""
        self._log("INFO", msg, **kwargs)
    
    def warning(self, msg: str, **kwargs) -> None:
        """Log at WARNING level."""
        self._log("WARNING", msg, **kwargs)
    
    def error(self, msg: str, **kwargs) -> None:
        """Log at ERROR level."""
        self._log("ERROR", msg, **kwargs)
    
    def critical(self, msg: str, **kwargs) -> None:
        """Log at CRITICAL level."""
        self._log("CRITICAL", msg, **kwargs)


# Convenience functions
def log_info(msg: str, **kwargs) -> None:
    """Log at INFO level."""
    get_logger().info(msg, **kwargs) if STRUCTLOG_AVAILABLE else logging.info(msg)


def log_error(msg: str, **kwargs) -> None:
    """Log at ERROR level."""
    get_logger().error(msg, **kwargs) if STRUCTLOG_AVAILABLE else logging.error(msg)


def log_warning(msg: str, **kwargs) -> None:
    """Log at WARNING level."""
    get_logger().warning(msg, **kwargs) if STRUCTLOG_AVAILABLE else logging.warning(msg)
