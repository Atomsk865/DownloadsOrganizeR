"""SortNStore - Main package for file organization service and web dashboard.

Modules:
    organizer: Core file organization service
    tray_app: Windows system tray application
    dashboard: Flask web dashboard server
    dashboard_app: Flask application package with routes and configuration
"""

__version__ = "1.0.0"
__author__ = "Richard Dennett"
__license__ = "MIT"

# Import main components for easy access
try:
    from .organizer import Organizer
except ImportError:
    pass

try:
    from .dashboard import create_app
except ImportError:
    pass

__all__ = ["__version__", "__author__", "__license__"]
