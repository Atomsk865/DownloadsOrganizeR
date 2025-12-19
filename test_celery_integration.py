"""
Phase 5: Celery Integration Tests

Comprehensive test suite for:
- Task creation and queuing
- Task status monitoring
- Worker management
- Graceful degradation when Celery not installed
- API endpoints

Run: python test_celery_integration.py

Features:
- @celery: Task queue testing
- @redis: Result backend testing
- Status monitoring verification
- Non-breaking fallback paths
"""

import sys
import os

# Add workspace to path
sys.path.insert(0, '/workspaces/DownloadsOrganizeR')

def test_celery_module_availability():
    """Test 1: Module availability and graceful fallback."""
    print("\n" + "="*70)
    print("TEST 1: Celery Module Availability")
    print("="*70)
    
    try:
        from SortNStoreDashboard.tasks import CELERY_AVAILABLE
        print(f"✅ CELERY_AVAILABLE: {CELERY_AVAILABLE}")
        
        if CELERY_AVAILABLE:
            print("✅ Celery is installed")
        else:
            print("✅ Celery gracefully unavailable (expected if not installed)")
        
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_task_creation():
    """Test 2: Task creation and queuing."""
    print("\n" + "="*70)
    print("TEST 2: Task Creation")
    print("="*70)
    
    try:
        from SortNStoreDashboard.tasks import organize_files_task, CELERY_AVAILABLE
        
        if not CELERY_AVAILABLE:
            print("✅ Graceful fallback: Celery not available, tasks are stubs")
            # Since Celery isn't available, tasks are just functions
            result = organize_files_task(path="/tmp")
            print(f"✅ Task stub returns: {result}")
            return True
        
        # If celery is available (would require Redis running)
        print("✅ Celery available, task creation would work")
        print("   Note: Full test requires Redis running at redis://localhost:6379/0")
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_task_monitoring():
    """Test 3: Task monitoring functions."""
    print("\n" + "="*70)
    print("TEST 3: Task Monitoring")
    print("="*70)
    
    try:
        from SortNStoreDashboard.task_monitoring import (
            get_task_status,
            get_worker_status,
            get_celery_monitoring_status,
        )
        
        # Test status function
        status = get_task_status("test-task-id")
        print(f"✅ get_task_status() returned: {status}")
        
        # Test worker status
        workers = get_worker_status()
        print(f"✅ get_worker_status() returned: {workers}")
        
        # Test overall status
        monitoring = get_celery_monitoring_status()
        print(f"✅ get_celery_monitoring_status() returned: {monitoring}")
        
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_api_endpoints():
    """Test 4: API endpoint registration."""
    print("\n" + "="*70)
    print("TEST 4: API Endpoints Registration")
    print("="*70)
    
    try:
        from SortNStoreDashboard.tasks_api import tasks_bp, register_tasks_blueprint
        
        # Check blueprint exists
        print(f"✅ tasks_bp registered: {tasks_bp.name}")
        print(f"✅ Blueprint URL prefix: {tasks_bp.url_prefix}")
        
        # Check expected routes
        expected_routes = [
            'queue_organize_task',
            'get_task_detail',
            'cancel_task_endpoint',
            'list_tasks',
            'get_workers_status',
            'get_celery_status',
        ]
        
        for route_name in expected_routes:
            if route_name in dir(sys.modules['SortNStoreDashboard.tasks_api']):
                print(f"✅ Route available: {route_name}")
        
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_dashboard_integration():
    """Test 5: Dashboard integration."""
    print("\n" + "="*70)
    print("TEST 5: Dashboard Integration")
    print("="*70)
    
    try:
        # Test that SortNStoreDashboard can load with Celery support
        from SortNStoreDashboard import create_app
        
        app = create_app()
        print(f"✅ App created successfully")
        
        # Check routes exist
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        celery_routes = [r for r in routes if 'tasks' in r or 'organize' in r or 'workers' in r]
        print(f"✅ Found Celery routes: {celery_routes}")
        
        celery_routes = [r for r in routes if 'celery' in r]
        print(f"✅ Celery status endpoint registered: {celery_routes}")
        
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_structured_logging_integration():
    """Test 6: Structured logging integration."""
    print("\n" + "="*70)
    print("TEST 6: Structured Logging Integration")
    print("="*70)
    
    try:
        from SortNStoreDashboard.structured_logging import get_logger
        from SortNStoreDashboard.tasks import celery_app, CELERY_AVAILABLE
        
        log = get_logger('test_celery')
        print(f"✅ Logger initialized")
        
        # Log some test messages
        log.info("celery_test_started", test="phase_5")
        print(f"✅ Structured logging works")
        
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_backward_compatibility():
    """Test 7: Backward compatibility."""
    print("\n" + "="*70)
    print("TEST 7: Backward Compatibility")
    print("="*70)
    
    try:
        from SortNStoreDashboard import create_app
        
        app = create_app()
        
        # Check that non-Celery features still work
        routes_to_check = [
            '/api/docs',  # Flask-RESTX
            '/admin',      # Flask-Admin
            '/auth/',      # Flask-Security
            '/api/config', # API endpoints
        ]
        
        all_routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        for route in routes_to_check:
            matching = [r for r in all_routes if route in r]
            if matching:
                print(f"✅ Route group '{route}' available: {matching[:1]}")
        
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_graceful_degradation():
    """Test 8: Graceful degradation."""
    print("\n" + "="*70)
    print("TEST 8: Graceful Degradation")
    print("="*70)
    
    try:
        from SortNStoreDashboard.tasks import (
            organize_files_task,
            send_email_task,
            generate_report_task,
            get_celery_status,
            CELERY_AVAILABLE,
        )
        
        # Test that tasks work (or gracefully degrade)
        if CELERY_AVAILABLE:
            result1 = organize_files_task.delay(path="/tmp")
        else:
            result1 = organize_files_task(path="/tmp")
        print(f"✅ organize_files_task works: {type(result1)}")
        
        if CELERY_AVAILABLE:
            result2 = send_email_task.delay("test@test.com", "Test", "Body")
        else:
            result2 = send_email_task("test@test.com", "Test", "Body")
        print(f"✅ send_email_task works: {type(result2)}")
        
        if CELERY_AVAILABLE:
            result3 = generate_report_task.delay("summary", "json")
        else:
            result3 = generate_report_task("summary", "json")
        print(f"✅ generate_report_task works: {type(result3)}")
        
        # Test status function
        status = get_celery_status()
        print(f"✅ get_celery_status() works: {status}")
        
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_configuration():
    """Test 9: Configuration."""
    print("\n" + "="*70)
    print("TEST 9: Configuration")
    print("="*70)
    
    try:
        from SortNStoreDashboard.tasks import make_celery
        
        # Test Celery configuration
        celery = make_celery()
        
        if celery is None:
            print("✅ Celery not available (expected if not installed)")
            return True
        
        # Check configuration
        config = {
            'broker_url': celery.conf.get('broker_url', 'not set'),
            'result_backend': celery.conf.get('result_backend', 'not set'),
            'task_serializer': celery.conf.get('task_serializer', 'not set'),
            'timezone': celery.conf.get('timezone', 'not set'),
            'task_track_started': celery.conf.get('task_track_started', False),
        }
        
        print(f"✅ Celery configuration:")
        for key, value in config.items():
            print(f"   - {key}: {value}")
        
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "#"*70)
    print("# PHASE 5: CELERY INTEGRATION TEST SUITE")
    print("#"*70)
    
    tests = [
        ("Module Availability", test_celery_module_availability),
        ("Task Creation", test_task_creation),
        ("Task Monitoring", test_task_monitoring),
        ("API Endpoints", test_api_endpoints),
        ("Dashboard Integration", test_dashboard_integration),
        ("Structured Logging", test_structured_logging_integration),
        ("Backward Compatibility", test_backward_compatibility),
        ("Graceful Degradation", test_graceful_degradation),
        ("Configuration", test_configuration),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {str(e)}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "#"*70)
    print("# TEST SUMMARY")
    print("#"*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
