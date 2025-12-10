#!/usr/bin/env python3
"""
Compatibility shim: main service script renamed to SortNStoreService.py.
This wrapper keeps legacy entry points working.
"""
from SortNStoreService import main

if __name__ == "__main__":
    main()
