#!/usr/bin/env python3
"""
Compatibility shim: tray app renamed to SortNStoreTrayApp.py.
This wrapper keeps legacy entry points working.
"""
from SortNStoreTrayApp import main

if __name__ == "__main__":
    main()
