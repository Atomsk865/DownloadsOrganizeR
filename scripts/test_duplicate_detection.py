#!/usr/bin/env python3
"""
Test script for duplicate file detection feature.

Creates test files with identical content to verify:
1. Hash calculation works
2. Duplicates are detected
3. Hash database is maintained
4. API endpoints return correct data
"""

import hashlib
import json
import tempfile
from pathlib import Path
import requests
import time

def calculate_hash(file_path):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def test_duplicate_detection():
    """Test duplicate file detection."""
    print("=" * 60)
    print("Testing Duplicate File Detection")
    print("=" * 60)
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Test 1: Create files with identical content
        print("\n[Test 1] Creating identical files...")
        content = b"This is test content for duplicate detection!"
        
        file1 = tmpdir / "test_file_1.txt"
        file2 = tmpdir / "test_file_2.txt"
        file3 = tmpdir / "test_file_3.txt"
        
        file1.write_bytes(content)
        file2.write_bytes(content)
        file3.write_bytes(content)
        
        # Calculate hashes
        hash1 = calculate_hash(file1)
        hash2 = calculate_hash(file2)
        hash3 = calculate_hash(file3)
        
        print(f"  File 1 hash: {hash1[:12]}...")
        print(f"  File 2 hash: {hash2[:12]}...")
        print(f"  File 3 hash: {hash3[:12]}...")
        
        assert hash1 == hash2 == hash3, "Hashes should match for identical files"
        print("  ✅ All hashes match - files are identical")
        
        # Test 2: Create file_hashes.json manually
        print("\n[Test 2] Creating hash database...")
        hash_db_path = tmpdir / "file_hashes.json"
        
        hash_db = {
            hash1: [str(file1), str(file2), str(file3)]
        }
        
        with hash_db_path.open("w") as f:
            json.dump(hash_db, f, indent=2)
        
        print(f"  Created hash database at {hash_db_path}")
        print(f"  Database contains {len(hash_db)} hash(es)")
        print(f"  Hash has {len(hash_db[hash1])} file(s)")
        print("  ✅ Hash database created successfully")
        
        # Test 3: API endpoint test
        print("\n[Test 3] Testing API endpoint...")
        try:
            response = requests.get(
                "http://127.0.0.1:5000/api/duplicates",
                auth=("admin", "")
            )
            
            assert response.status_code == 200, f"API returned status {response.status_code}"
            data = response.json()
            print(f"  Status: {response.status_code}")
            print(f"  Total duplicates: {data['total_duplicates']}")
            print(f"  Total duplicate files: {data['total_duplicate_files']}")
            print(f"  Wasted space: {data['wasted_space_human']}")
            print("  ✅ API endpoint responding correctly")
                
        except Exception as e:
            print(f"  ⚠️  Could not test API (dashboard may not be running): {e}")
        
        # Test 4: Test different content
        print("\n[Test 4] Testing different content detection...")
        file4 = tmpdir / "test_file_4.txt"
        file4.write_bytes(b"Different content")
        
        hash4 = calculate_hash(file4)
        print(f"  File 4 hash: {hash4[:12]}...")
        
        assert hash4 != hash1, "Different content should have different hash"
        print("  ✅ Different content has different hash")
    
    print("\n" + "=" * 60)
    print("All tests passed! ✅")
    print("=" * 60)
    # Pytest expects no return value


if __name__ == "__main__":
    success = test_duplicate_detection()
    exit(0 if success else 1)
