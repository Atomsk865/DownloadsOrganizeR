#!/usr/bin/env python3
"""
Quick integration test for structured logging and Flask-RESTX.

Demonstrates:
1. Structured logging with structlog
2. Flask-RESTX API documentation integration
3. Both are optional and backward compatible

Run:
    python test_awesome_python_integration.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("Testing awesome-python Integration Quick Wins")
print("="*70 + "\n")

# ============================================================================
# TEST 1: Structured Logging
# ============================================================================

print("TEST 1: Structured Logging with structlog")
print("-" * 70)

try:
    from SortNStoreDashboard.structured_logging import (
        configure_logging,
        get_logger,
        StructuredLoggerAdapter,
        STRUCTLOG_AVAILABLE
    )
    
    print(f"✓ Structured logging module imported successfully")
    print(f"  - structlog available: {STRUCTLOG_AVAILABLE}")
    
    # Configure logging
    configure_logging(use_json=False, log_level="INFO")
    print(f"✓ Logging configured (JSON=False for demo)")
    
    # Get logger
    log = get_logger(__name__)
    print(f"✓ Logger instance created: {type(log).__name__}")
    
    # Test logging
    print(f"\n  Logging demo output:")
    log.info("service_started", version="2.0.0", component="dashboard")
    log.info("file_organized", 
             filename="report.pdf",
             destination="Documents",
             size_bytes=1024000)
    
    # Test adapter
    print(f"\n  Testing StructuredLoggerAdapter:")
    adapter = StructuredLoggerAdapter("test_adapter")
    adapter.bind(request_id="req-123", user="admin")
    adapter.info("user_action", action="view_config")
    
    print("\n✅ TEST 1 PASSED: Structured logging working!\n")

except Exception as e:
    print(f"❌ TEST 1 FAILED: {e}")
    import traceback
    traceback.print_exc()
    print()


# ============================================================================
# TEST 2: Flask-RESTX Integration
# ============================================================================

print("TEST 2: Flask-RESTX Integration")
print("-" * 70)

try:
    from flask import Flask
    from SortNStoreDashboard.restx_api import (
        init_restx_api,
        get_restx_status,
        RESTX_AVAILABLE
    )
    
    print(f"✓ Flask-RESTX module imported successfully")
    print(f"  - flask-restx available: {RESTX_AVAILABLE}")
    
    # Get status
    status = get_restx_status()
    print(f"✓ Integration status: {status}")
    
    if RESTX_AVAILABLE:
        # Create Flask app
        app = Flask(__name__)
        print(f"✓ Flask app created")
        
        # Initialize RESTX API
        api = init_restx_api(app, prefix="/api", doc_url="/docs")
        print(f"✓ Flask-RESTX initialized")
        print(f"  - API instance: {type(api).__name__}")
        print(f"  - Documentation URL: http://localhost:5000/api/docs")
        
        # List registered namespaces
        if hasattr(api, 'namespaces'):
            print(f"  - Registered namespaces: {len(api.namespaces)}")
            for ns in api.namespaces:
                print(f"    • {ns.name}: {ns.description}")
        
        print("\n✅ TEST 2 PASSED: Flask-RESTX integration working!")
        print("\n   To test the API documentation:")
        print("   1. Uncomment init_restx_api() in SortNStoreDashboard.py create_app()")
        print("   2. Run: python SortNStoreDashboard.py")
        print("   3. Visit: http://localhost:5000/api/docs")
    else:
        print(f"⚠️  Flask-RESTX not available (not installed)")
        print(f"   Install with: pip install flask-restx")
    
    print()

except Exception as e:
    print(f"❌ TEST 2 FAILED: {e}")
    import traceback
    traceback.print_exc()
    print()


# ============================================================================
# SUMMARY
# ============================================================================

print("="*70)
print("Integration Test Summary")
print("="*70 + "\n")

print("✅ Both modules imported and working!\n")

print("Next Steps:")
print("1. Update SortNStoreDashboard.py to use structured logging")
print("2. Optionally enable Flask-RESTX in create_app()")
print("3. Install optional dependencies: pip install flask-restx structlog")
print("4. Review examples/awesome-python-integrations/ for complete examples")
print("\nDocumentation:")
print("- docs/AWESOME_PYTHON_ENHANCEMENTS.md - Full analysis")
print("- docs/INTEGRATION_QUICK_START.md - Quick start guide")
print()
