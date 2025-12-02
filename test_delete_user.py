#!/usr/bin/env python3
"""Test script to check delete user functionality.

Note: This is an integration script requiring a running server at localhost:5000.
When executed under pytest without a live server, it should be skipped.
"""

import requests
import base64
import json
import socket

def _server_available(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

try:
    import pytest  # type: ignore
    if not _server_available('localhost', 5000):
        pytest.skip("Skipping integration script: server not running at localhost:5000", allow_module_level=True)
except Exception:
    # Not running under pytest or skip failed; proceed (script mode)
    pass

# Configuration
base_url = "http://localhost:5000"
username = "admin"
password = "change_this_password"

# Create auth header
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = {
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/json"
}

# Test 1: Get current users
print("=" * 50)
print("Test 1: Get current users")
response = requests.get(f"{base_url}/api/dashboard/config", headers=headers)
print(f"Status: {response.status_code}")
if response.ok:
    config = response.json()
    users = config.get('users', [])
    print(f"Current users: {json.dumps(users, indent=2)}")
else:
    print(f"Error: {response.text}")

# Test 2: Try to delete a test user if it exists
print("\n" + "=" * 50)
print("Test 2: Try to delete 'test' user")
response = requests.delete(f"{base_url}/api/dashboard/users/test", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
if response.ok:
    print("✓ Delete successful")
else:
    print("✗ Delete failed")

# Test 3: Get users after delete
print("\n" + "=" * 50)
print("Test 3: Get users after delete")
response = requests.get(f"{base_url}/api/dashboard/config", headers=headers)
print(f"Status: {response.status_code}")
if response.ok:
    config = response.json()
    users = config.get('users', [])
    print(f"Users after delete: {json.dumps(users, indent=2)}")
else:
    print(f"Error: {response.text}")
