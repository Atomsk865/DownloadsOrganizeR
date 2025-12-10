#!/usr/bin/env python3
"""
Entry point wrapper for SortNStoreService (formerly Organizer.py).
Maintains compatibility with legacy calls while using the new naming.
"""
import sys
from pathlib import Path

# Add src to path to allow imports
project_root = Path(__file__).parent
src_path = project_root / "src"
if src_path not in sys.path:
    sys.path.insert(0, str(src_path))

from sortnstore.organizer import main

if __name__ == "__main__":
    main()
