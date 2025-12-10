#!/usr/bin/env python3
"""
Test the VT endpoint with the exact same authentication as the browser.
"""

import requests

SERVER = "http://127.0.0.1:5000"
USERNAME = "admin"
PASSWORD = "WorkingComputer97!"  # From the Basic auth header

print("Testing with authentication...")

# Test with Basic Auth (like the browser)
response = requests.post(
    f"{SERVER}/api/recent_files/virustotal",
    json={"path": "C:\\test.txt"},
    auth=(USERNAME, PASSWORD),
    headers={
        "Content-Type": "application/json",
        # Note: CSRF will be missing but let's see what error we get
    }
)

print(f"Status: {response.status_code}")
print(f"URL: {response.url}")
print(f"Response: {response.text[:500]}")

if response.status_code == 404:
    print("\n✗ Still getting 404 with auth!")
    print("This means the route truly isn't registered.")
elif response.status_code == 400:
    print("\n✓ Route exists! (400 = CSRF or config issue)")
elif response.status_code == 403:
    print("\n✓ Route exists! (403 = Permission issue)")
else:
    print(f"\n? Unexpected status: {response.status_code}")
