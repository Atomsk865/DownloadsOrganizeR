#!/usr/bin/env python3
"""
Test the live running server to see what routes are actually available.
"""

import requests
import json

SERVER = "http://127.0.0.1:5000"

print("=" * 70)
print("Testing Live Server Routes")
print("=" * 70)

# Test 1: Test endpoint
print("\n1. Testing /api/recent_files/test")
try:
    resp = requests.get(f"{SERVER}/api/recent_files/test", timeout=5)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   Response: {resp.json()}")
        print("   ✓ Test endpoint works")
    else:
        print(f"   ✗ Unexpected status: {resp.text[:200]}")
except requests.exceptions.ConnectionError:
    print("   ✗ Server not running on port 5000")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Status endpoint
print("\n2. Testing /api/recent_files/status")
try:
    resp = requests.get(f"{SERVER}/api/recent_files/status", timeout=5)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        print("   ✓ Status endpoint works")
    else:
        print(f"   ✗ Unexpected status: {resp.text[:200]}")
except requests.exceptions.ConnectionError:
    print("   ✗ Server not running on port 5000")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: VirusTotal endpoint
print("\n3. Testing /api/recent_files/virustotal (POST)")
try:
    resp = requests.post(
        f"{SERVER}/api/recent_files/virustotal",
        json={'path': 'C:\\test.txt'},
        headers={'Content-Type': 'application/json'},
        timeout=5
    )
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 404:
        print("   ✗ Route NOT FOUND (404) - The route is not registered!")
        print(f"   Response: {resp.text[:500]}")
    elif resp.status_code == 401:
        print("   ✓ Route exists (needs authentication)")
    elif resp.status_code == 400:
        print("   ✓ Route exists (returned 400 - config issue)")
        print(f"   Response: {resp.json()}")
    else:
        print(f"   Status: {resp.status_code}")
        try:
            print(f"   Response: {resp.json()}")
        except:
            print(f"   Response: {resp.text[:500]}")
except requests.exceptions.ConnectionError:
    print("   ✗ Server not running on port 5000")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 70)
print("If test and status work but virustotal returns 404,")
print("the running server is using OLD CODE.")
print("=" * 70)
