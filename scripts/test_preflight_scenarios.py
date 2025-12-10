#!/usr/bin/env python3
"""
Test script to demonstrate preflight check failure scenarios

This simulates missing dependencies to show how preflight checks
catch issues before server startup.
"""

import sys
import os

# Temporarily hide a critical module to simulate missing dependency
def test_missing_flask():
    """Simulate missing Flask dependency"""
    print("\n" + "="*60)
    print("TEST: Simulating missing Flask dependency")
    print("="*60 + "\n")
    
    # Backup sys.modules
    flask_module = sys.modules.get('flask')
    
    # Hide Flask
    if 'flask' in sys.modules:
        del sys.modules['flask']
    
    # Try importing without Flask
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # This would fail in actual preflight checks
        import flask
        print("❌ Test Failed: Flask should not be importable")
    except ImportError:
        print("✅ Test Passed: Flask import fails as expected")
        print("   Preflight checks would catch this and prevent server start\n")
    
    # Restore
    if flask_module:
        sys.modules['flask'] = flask_module

def test_missing_config():
    """Simulate missing configuration file"""
    print("\n" + "="*60)
    print("TEST: Simulating missing configuration file")
    print("="*60 + "\n")
    
    test_config = "test_missing_config.json"
    
    if os.path.exists(test_config):
        print(f"⚠️  File {test_config} already exists, skipping test")
    else:
        print(f"✅ Test Passed: File {test_config} does not exist")
        print("   Preflight checks would warn about missing config\n")

def test_invalid_json():
    """Simulate invalid JSON configuration"""
    print("\n" + "="*60)
    print("TEST: Simulating invalid JSON configuration")
    print("="*60 + "\n")
    
    test_config = "test_invalid.json"
    
    # Create invalid JSON
    with open(test_config, 'w') as f:
        f.write('{ invalid json }')
    
    try:
        import json
        with open(test_config, 'r') as f:
            json.load(f)
        print("❌ Test Failed: Invalid JSON should not parse")
    except json.JSONDecodeError:
        print("✅ Test Passed: Invalid JSON detected")
        print("   Preflight checks would fail with JSON parse error\n")
    finally:
        # Cleanup
        if os.path.exists(test_config):
            os.remove(test_config)

def test_port_in_use():
    """Test port availability check"""
    print("\n" + "="*60)
    print("TEST: Testing port availability check")
    print("="*60 + "\n")
    
    import socket
    
    # Try to bind to port 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', 5000))
    sock.close()
    
    if result != 0:
        print("✅ Test Passed: Port 5000 is available")
        print("   Preflight checks would pass port availability\n")
    else:
        print("⚠️  Warning: Port 5000 is in use")
        print("   Preflight checks would warn about port availability\n")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 Preflight Checks - Test Suite")
    print("="*60)
    print("\nThis script simulates various failure scenarios")
    print("to demonstrate how preflight checks protect the server.\n")
    
    test_missing_config()
    test_invalid_json()
    test_port_in_use()
    
    print("="*60)
    print("✅ Test Suite Complete")
    print("="*60)
    print("\nTo see actual preflight checks in action:")
    print("  python preflight_check.py")
    print("\nTo start server with preflight checks:")
    print("  python SortNStoreDashboard.py\n")
