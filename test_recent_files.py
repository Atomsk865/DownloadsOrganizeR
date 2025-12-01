"""
Test script to demonstrate the Recent Files feature.

This script simulates file movements and verifies the tracking system.
Run this after starting Organizer.py to test the feature.
"""

import json
import os
from pathlib import Path
from datetime import datetime


def test_file_moves_json():
    """Test that file_moves.json is being created and updated properly."""
    file_moves_path = Path("C:/Scripts/file_moves.json")
    
    print("Testing file_moves.json...")
    print(f"Expected location: {file_moves_path}")
    
    if not file_moves_path.exists():
        print("❌ file_moves.json does not exist yet.")
        print("   Try moving a file to Downloads to trigger creation.")
        return False
    
    try:
        with open(file_moves_path, 'r', encoding='utf-8') as f:
            moves = json.load(f)
        
        print(f"✅ file_moves.json found with {len(moves)} entries")
        
        if moves:
            print("\nMost recent file movement:")
            latest = moves[0]
            print(f"  Filename: {latest['filename']}")
            print(f"  Category: {latest['category']}")
            print(f"  Timestamp: {latest['timestamp']}")
            print(f"  From: {latest['original_path']}")
            print(f"  To: {latest['destination_path']}")
            
            # Check if file still exists
            if os.path.exists(latest['destination_path']):
                print(f"  ✅ File exists at destination")
            else:
                print(f"  ⚠️  File not found at destination")
        else:
            print("  No file movements recorded yet")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing file_moves.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file_moves.json: {e}")
        return False


def test_api_endpoints():
    """Instructions for testing API endpoints."""
    print("\n" + "="*60)
    print("Testing API Endpoints")
    print("="*60)
    print("\n1. Start the dashboard:")
    print("   python OrganizerDashboard.py")
    print("\n2. Open browser to http://localhost:5000")
    print("\n3. Login with credentials (default: admin / change_this_password)")
    print("\n4. Look for 'Recent File Movements' card")
    print("\n5. Click 'Open' or 'Show' buttons to test file interaction")
    print("\n6. Test API directly with curl:")
    print("   curl -u admin:change_this_password http://localhost:5000/api/recent_files")


def create_test_file():
    """Create a test file in Downloads to trigger organizer."""
    try:
        username = os.environ.get("USERNAME", "")
        if not username:
            print("❌ Cannot determine username")
            return False
        
        downloads = Path(f"C:/Users/{username}/Downloads")
        if not downloads.exists():
            print(f"❌ Downloads folder not found: {downloads}")
            return False
        
        test_file = downloads / "organizer_test.txt"
        with open(test_file, 'w') as f:
            f.write(f"Test file created at {datetime.now()}\n")
        
        print(f"\n✅ Created test file: {test_file}")
        print("   It should be moved to Documents folder shortly...")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test file: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Recent Files Feature Test")
    print("="*60)
    
    # Test 1: Check file_moves.json
    test_file_moves_json()
    
    # Test 2: Create test file
    print("\n" + "="*60)
    print("Would you like to create a test file? (yes/no)")
    response = input("> ").lower()
    if response in ['yes', 'y']:
        create_test_file()
    
    # Test 3: API endpoint instructions
    test_api_endpoints()
    
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)
