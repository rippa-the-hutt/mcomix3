#!/usr/bin/env python3
"""Launcher entry point for the bundled MComix3 executable.

This script is the entry point that PyInstaller wraps into MComix3.exe.
When the exe starts, it runs this script which imports and launches
the MComix3 application.
"""
import sys
import os

# Ensure the bundled package directory is on the path
_bundle_dir = os.path.dirname(os.path.abspath(__file__))
if _bundle_dir not in sys.path:
    sys.path.insert(0, _bundle_dir)

from mcomix.run import run
run()
