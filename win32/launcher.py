"""Entry point for PyInstaller-built MComix3 executable.

This launcher is used by PyInstaller as the entry point for the
Windows executable. Imports must be at module level so PyInstaller
can detect them during analysis.
"""
import sys
import os

# Ensure the mcomix package can be found
_bundle_dir = os.path.dirname(os.path.abspath(__file__))
if _bundle_dir not in sys.path:
    sys.path.insert(0, _bundle_dir)

# Module-level imports for PyInstaller detection
import mcomix.run

if __name__ == '__main__':
    mcomix.run.run()
