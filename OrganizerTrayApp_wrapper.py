#!/usr/bin/env python3
"""
Backward compatibility wrapper for OrganizerTrayApp.py

This script maintains compatibility with existing installation scripts
that reference OrganizerTrayApp.py from the root directory.
"""
import sys
from pathlib import Path

# Add src to path to allow imports
project_root = Path(__file__).parent
src_path = project_root / "src"
if src_path not in sys.path:
    sys.path.insert(0, str(src_path))

from sortnstore.tray_app import main

if __name__ == "__main__":
    main()
