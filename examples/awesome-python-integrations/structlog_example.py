#!/usr/bin/env python3
"""
structlog Integration Example for SortNStore

Purpose: Replace text-based logging with structured JSON logging
Effort: Low (2-4 hours integration)
Benefits:
  - Machine-readable logs (JSON)
  - Better debugging with context
  - Easy log aggregation (ELK, Splunk, CloudWatch)
  - Automatic request ID tracking
  - Performance improvements

Dependencies:
  pip install structlog

Usage:
  python structlog_example.py

Integration Notes:
  - Non-breaking: Works alongside standard logging
  - Opt-in: Can be enabled via config
  - Gradual adoption: Migrate loggers one at a time
  - Production ready: Used by major companies
"""

import structlog
import logging
import sys
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

def configure_structlog(use_json=True, log_level="INFO"):
    """
    Configure structlog for SortNStore
    
    Args:
        use_json: If True, output JSON. If False, output colored console logs
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Shared processors for both formats
    shared_processors = [
        # Add log level to event dict
        structlog.stdlib.add_log_level,
        
        # Add logger name to event dict
        structlog.stdlib.add_logger_name,
        
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        
        # Add caller information (file, line, function)
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            ],
        ),
        
        # Stack trace for exceptions
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if use_json:
        # JSON output for production/log aggregation
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    else:
        # Colored console output for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging to work with structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def demonstrate_basic_logging():
    """Show basic structlog usage"""
    log = structlog.get_logger()
    
    print("\n" + "="*70)
    print("1. BASIC LOGGING")
    print("="*70 + "\n")
    
    # Simple log
    log.info("service_started", version="2.0.0", port=5000)
    
    # Log with multiple fields
    log.info("file_organized",
        filename="document.pdf",
        source="C:\\Users\\Downloads",
        destination="C:\\Users\\Downloads\\Documents",
        size_bytes=1024000,
        category="Documents"
    )
    
    # Warning log
    log.warning("high_memory_usage",
        current_mb=180,
        threshold_mb=200,
        percentage=90
    )
    
    # Error log
    log.error("file_move_failed",
        filename="locked.docx",
        error="Permission denied",
        retry_count=3
    )


def demonstrate_context_binding():
    """Show context binding for automatic field inclusion"""
    log = structlog.get_logger()
    
    print("\n" + "="*70)
    print("2. CONTEXT BINDING")
    print("="*70 + "\n")
    
    # Bind context that will be included in all subsequent logs
    log = log.bind(
        user="admin",
        session_id="abc123",
        request_id="req-456"
    )
    
    # All logs now include user, session_id, request_id automatically
    log.info("config_updated", setting="watch_folder", value="/Downloads")
    log.info("service_restarted", downtime_seconds=2)
    log.info("api_called", endpoint="/api/status", method="GET")


def demonstrate_file_operations_logging():
    """Example of logging file operations"""
    log = structlog.get_logger("file_organizer")
    
    print("\n" + "="*70)
    print("3. FILE OPERATIONS LOGGING")
    print("="*70 + "\n")
    
    # Simulate organizing files
    files = [
        {"name": "photo.jpg", "size": 2048000, "category": "Images"},
        {"name": "report.pdf", "size": 1024000, "category": "Documents"},
        {"name": "video.mp4", "size": 50000000, "category": "Videos"},
    ]
    
    for file_info in files:
        log.info("file_detected",
            file_event="new_file",
            filename=file_info["name"],
            size_bytes=file_info["size"],
            category=file_info["category"],
            action="move"
        )
        
        log.debug("file_analysis",
            filename=file_info["name"],
            extension=Path(file_info["name"]).suffix,
            category_match=file_info["category"]
        )
        
        log.info("file_organized",
            filename=file_info["name"],
            category=file_info["category"],
            status="success"
        )


def demonstrate_error_handling():
    """Example of logging errors with context"""
    log = structlog.get_logger("error_handler")
    
    print("\n" + "="*70)
    print("4. ERROR HANDLING")
    print("="*70 + "\n")
    
    try:
        # Simulate an error
        raise ValueError("Invalid configuration: watch_folder cannot be empty")
    except Exception as e:
        log.error("configuration_error",
            error_type=type(e).__name__,
            error_message=str(e),
            config_key="watch_folder",
            exc_info=True  # Include full stack trace
        )
    
    # Network error example
    log.error("network_path_unreachable",
        path="\\\\nas\\storage",
        retry_count=3,
        next_retry_seconds=30,
        error="Network path not found"
    )


def demonstrate_performance_metrics():
    """Example of logging performance metrics"""
    log = structlog.get_logger("metrics")
    
    print("\n" + "="*70)
    print("5. PERFORMANCE METRICS")
    print("="*70 + "\n")
    
    # System metrics
    log.info("system_metrics",
        metric_type="system",
        cpu_percent=15.5,
        memory_mb=128.7,
        disk_free_gb=250.3,
        uptime_seconds=86400
    )
    
    # Service metrics
    log.info("service_metrics",
        metric_type="service",
        files_organized_today=543,
        total_files_organized=15432,
        average_processing_time_ms=45,
        queue_size=0
    )
    
    # Performance timing
    import time
    start = time.time()
    time.sleep(0.1)  # Simulate work
    duration = time.time() - start
    
    log.info("operation_completed",
        operation="file_scan",
        duration_seconds=duration,
        files_scanned=150,
        performance="normal"
    )


def demonstrate_authentication_logging():
    """Example of logging authentication events"""
    log = structlog.get_logger("auth")
    
    print("\n" + "="*70)
    print("6. AUTHENTICATION LOGGING")
    print("="*70 + "\n")
    
    # Successful login
    log.info("login_success",
        auth_event="authentication",
        user="admin",
        auth_method="basic",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0..."
    )
    
    # Failed login
    log.warning("login_failed",
        auth_event="authentication",
        user="unknown_user",
        auth_method="basic",
        ip_address="192.168.1.105",
        reason="invalid_credentials",
        attempt_count=3
    )
    
    # Session activity
    log.debug("session_activity",
        api_event="api_call",
        user="admin",
        session_id="abc123",
        endpoint="/api/config",
        method="POST",
        response_code=200,
        duration_ms=45
    )


# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

class StructlogAdapter:
    """
    Adapter class to gradually migrate from standard logging to structlog
    
    Usage:
        # Old code (standard logging):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"File moved: {filename}")
        
        # New code (structlog):
        from structlog_adapter import StructlogAdapter
        logger = StructlogAdapter.get_logger(__name__)
        logger.info("file_moved", filename=filename)
    """
    
    @staticmethod
    def get_logger(name):
        """Get a structlog logger"""
        return structlog.get_logger(name)
    
    @staticmethod
    def migrate_logging_call(message, **kwargs):
        """
        Helper to migrate f-string logging to structured logging
        
        Example:
            # Old: logger.info(f"User {username} logged in")
            # New: migrate_logging_call("user_logged_in", username=username)
        """
        return message, kwargs


# ============================================================================
# INTEGRATION INTO SORTNSTORE
# ============================================================================

"""
INTEGRATION GUIDE:

1. Install dependency:
   pip install structlog

2. Add to SortNStoreService.py:
   
   import structlog
   from structlog_config import configure_structlog
   
   # At startup:
   use_json = config.get("structured_logging", False)
   configure_structlog(use_json=use_json)
   
   # Replace standard logger:
   # OLD: logger = logging.getLogger(__name__)
   # NEW: logger = structlog.get_logger(__name__)

3. Migrate logging calls:
   
   # OLD:
   logger.info(f"File organized: {filename} -> {destination}")
   
   # NEW:
   logger.info("file_organized",
       filename=filename,
       destination=destination,
       size_bytes=size,
       category=category
   )

4. Enable in config:
   
   {
     "enhanced_features": {
       "structured_logging": true
     }
   }

5. Configure output format:
   
   # Development (colored console):
   configure_structlog(use_json=False)
   
   # Production (JSON for log aggregation):
   configure_structlog(use_json=True)

MIGRATION STRATEGY:

Phase 1: Add structlog alongside existing logging
  - Install and configure
  - No code changes yet
  - Test in dev environment

Phase 2: Migrate new code
  - Use structlog for all new features
  - Keep old logging working

Phase 3: Migrate critical paths
  - File organization events
  - Authentication
  - Configuration changes
  - Errors

Phase 4: Complete migration
  - Migrate remaining loggers
  - Remove old logging statements
  - Update documentation

BENEFITS FOR SORTNSTORE:

1. Better Debugging:
   - All file movements with complete context
   - Authentication attempts with user/IP/reason
   - Configuration changes with old/new values
   - Errors with full context

2. Production Monitoring:
   - Easy integration with log aggregation tools
   - Query logs like a database
   - Build dashboards from log data
   - Set up alerts on specific events

3. Performance Analysis:
   - Track operation timing
   - Identify bottlenecks
   - Monitor system resources
   - Analyze file organization patterns

4. Security Auditing:
   - Complete authentication audit trail
   - Configuration change tracking
   - API access logs
   - Failed access attempts

EXAMPLE QUERIES (with JSON logs):

# Find all failed file moves:
jq 'select(.event=="file_move_failed")' logs.json

# Count files organized by category:
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' logs.json

# Find slow operations (>1 second):
jq 'select(.duration_seconds > 1)' logs.json

# Authentication failures from specific IP:
jq 'select(.event=="login_failed" and .ip_address=="192.168.1.105")' logs.json
"""


# ============================================================================
# RUN EXAMPLE
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("structlog Integration Example for SortNStore")
    print("="*70)
    
    # Choose output format
    print("\nOutput format:")
    print("1. JSON (for production/log aggregation)")
    print("2. Colored console (for development)")
    choice = input("\nSelect format (1 or 2, default=2): ").strip() or "2"
    
    use_json = choice == "1"
    configure_structlog(use_json=use_json, log_level="DEBUG")
    
    print("\n" + "="*70)
    print(f"Using {'JSON' if use_json else 'colored console'} output format")
    print("="*70)
    
    # Run demonstrations
    demonstrate_basic_logging()
    demonstrate_context_binding()
    demonstrate_file_operations_logging()
    demonstrate_error_handling()
    demonstrate_performance_metrics()
    demonstrate_authentication_logging()
    
    print("\n" + "="*70)
    print("Example completed!")
    print("="*70)
    print("\nNext steps:")
    print("1. Review the structured log output above")
    print("2. Compare with your current text-based logs")
    print("3. See integration notes in the code")
    print("4. Try enabling JSON output (option 1)")
    print("5. Test in your SortNStore development environment")
    print("\n" + "="*70 + "\n")
