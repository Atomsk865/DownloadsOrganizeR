#!/usr/bin/env python3
"""
Diagnostic script to check which routes are registered in the Flask app.
Run this on Windows to verify the VirusTotal endpoint is available.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("SortNStore Route Diagnostics")
print("=" * 70)

print("\n1. Testing module import...")
try:
    from SortNStoreDashboard.routes.api_recent_files import routes_api_recent_files
    print(f"   ✓ api_recent_files module imported successfully")
    print(f"   ✓ Blueprint name: {routes_api_recent_files.name}")
except Exception as e:
    print(f"   ✗ Failed to import api_recent_files: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n2. Creating Flask app...")
try:
    from SortNStoreDashboard import create_app
    app = create_app()
    print("   ✓ Flask app created successfully")
except Exception as e:
    print(f"   ✗ Failed to create app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3. Checking registered routes...")
recent_files_routes = []
all_routes = []

for rule in app.url_map.iter_rules():
    all_routes.append(rule.rule)
    if 'recent_files' in rule.rule or 'virustotal' in rule.rule:
        recent_files_routes.append({
            'path': rule.rule,
            'methods': sorted(rule.methods - {'HEAD', 'OPTIONS'}),
            'endpoint': rule.endpoint
        })

if recent_files_routes:
    print(f"   ✓ Found {len(recent_files_routes)} recent_files/virustotal routes:")
    for route in sorted(recent_files_routes, key=lambda x: x['path']):
        methods = ', '.join(route['methods'])
        print(f"      {route['path']:45s} [{methods}]")
else:
    print("   ✗ No recent_files routes found!")

print(f"\n   Total routes registered: {len(all_routes)}")

print("\n4. Testing endpoints with test client...")
with app.test_client() as client:
    
    # Test 1: Test endpoint (no auth required)
    print("\n   a) Testing /api/recent_files/test")
    try:
        resp = client.get('/api/recent_files/test')
        print(f"      Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"      Response: {resp.get_json()}")
            print("      ✓ Test endpoint works")
        else:
            print(f"      ✗ Unexpected status code")
    except Exception as e:
        print(f"      ✗ Error: {e}")
    
    # Test 2: Status endpoint (no auth required)
    print("\n   b) Testing /api/recent_files/status")
    try:
        resp = client.get('/api/recent_files/status')
        print(f"      Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.get_json()
            print(f"      VT Enabled: {data.get('virustotal_enabled')}")
            print(f"      VT Configured: {data.get('virustotal_configured')}")
            print("      ✓ Status endpoint works")
        else:
            print(f"      ✗ Unexpected status code")
    except Exception as e:
        print(f"      ✗ Error: {e}")
    
    # Test 3: VirusTotal endpoint (requires auth)
    print("\n   c) Testing /api/recent_files/virustotal")
    try:
        resp = client.post('/api/recent_files/virustotal', 
                          json={'path': 'test.txt'})
        print(f"      Status: {resp.status_code}")
        if resp.status_code == 401:
            print("      ✓ Route exists (returned 401 Unauthorized as expected)")
        elif resp.status_code == 400:
            print("      ✓ Route exists (returned 400 Bad Request - missing config)")
        elif resp.status_code == 404:
            print("      ✗ Route NOT FOUND (404) - This is the problem!")
        else:
            print(f"      Response: {resp.get_json()}")
    except Exception as e:
        print(f"      ✗ Error: {e}")

print("\n5. Checking blueprint registration...")
try:
    # Check if blueprint is in app's blueprints
    if 'routes_api_recent_files' in app.blueprints:
        print("   ✓ routes_api_recent_files blueprint is registered")
        bp = app.blueprints['routes_api_recent_files']
        print(f"   ✓ Blueprint URL prefix: {bp.url_prefix or '(none)'}")
    else:
        print("   ✗ routes_api_recent_files blueprint NOT registered!")
        print(f"   Registered blueprints: {list(app.blueprints.keys())}")
except Exception as e:
    print(f"   ✗ Error checking blueprints: {e}")

print("\n" + "=" * 70)
print("Diagnostics complete!")
print("=" * 70)

print("\n6. Live server test (if running)...")
print("   If your server is running on http://127.0.0.1:5000, test with:")
print("   curl http://127.0.0.1:5000/api/recent_files/test")
print("   curl http://127.0.0.1:5000/api/recent_files/status")
print("\n   If these work but /virustotal doesn't, check authentication.")
