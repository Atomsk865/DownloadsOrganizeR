#!/usr/bin/env python3
"""
Compatibility shim: batch organizer renamed to BatchSortNStore.py.
"""
import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from BatchSortNStore import main

if __name__ == "__main__":
    main()
