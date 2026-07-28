#!/usr/bin/env python3
"""Build a Windows executable of MComix3 using PyInstaller.

This script automates building a self-contained Windows .exe of MComix3
with GTK 3 and all dependencies bundled.

Requirements
------------
* Python 3.8+        (3.8 for Windows 7, 3.9+ for Windows 8+)
* PyGObject          pip install pygobject
* PyInstaller        pip install pyinstaller
* Pillow             pip install pillow
* GTK3 Runtime       https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
                      or via MSYS2: pacman -S mingw-w64-x86_64-gtk3

Usage
-----
    python win32/build_exe.py

The bundled application will be written to dist/MComix3/.
"""

import os
import sys
import shutil
import subprocess
import argparse

# Paths
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
DIST_DIR = os.path.join(PROJECT_ROOT, 'dist')
BUILD_DIR = os.path.join(PROJECT_ROOT, 'build')
SPEC_FILE = os.path.join(PROJECT_ROOT, 'win32', 'mcomix3.spec')


def clean():
    """Clean previous build artifacts."""
    for d in (DIST_DIR, BUILD_DIR):
        if os.path.isdir(d):
            print(f"Cleaning {d}...")
            shutil.rmtree(d)


def build_pyinstaller(onefile=False, console=False, icon=None):
    """Run PyInstaller to build the executable."""
    print("=" * 60)
    print("Building MComix3 for Windows with PyInstaller")
    print("=" * 60)

    # Determine Python architecture
    arch = struct_size = struct_calcsize = None  # noqa
    import struct
    is_64bit = struct.calcsize("P") == 8
    arch_name = "x64" if is_64bit else "x86"
    print(f"Python architecture: {arch_name}")

    # Build PyInstaller command
    pyinstaller = shutil.which('pyinstaller') or 'pyinstaller'

    cmd = [
        pyinstaller,
        '--log-level', 'WARN',
        '--name', 'MComix3',
        '--noconfirm',
        '--clean',
        '--additional-hooks-dir', os.path.join(PROJECT_ROOT, 'win32'),
    ]

    if not console:
        cmd.append('--windowed')  # no console window (GUI app)

    if icon and os.path.isfile(icon):
        cmd.extend(['--icon', icon])

    if onefile:
        cmd.append('--onefile')
    else:
        cmd.append('--onedir')

    # Collect all gi modules
    cmd.append('--collect-all')
    cmd.append('gi')

    # Collect all mcomix modules
    cmd.append('--collect-all')
    cmd.append('mcomix')

    # Collect PIL/Pillow
    cmd.append('--collect-submodules')
    cmd.append('PIL')

    # Exclude unnecessary modules to reduce size
    for exclude in (
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
        'matplotlib', 'notebook', 'IPython',
        'tkinter',
    ):
        cmd.extend(['--exclude-module', exclude])

    # Entry point script
    launcher = os.path.join(PROJECT_ROOT, 'win32', 'launcher.py')
    if not os.path.isfile(launcher):
        with open(launcher, 'w') as f:
            f.write('#!/usr/bin/env python3\n')
            f.write('"""Launcher for the bundled MComix3 executable."""\n')
            f.write('import sys\n')
            f.write('import os\n')
            f.write('# Ensure the bundled package is on path\n')
            f.write('sys.path.insert(0, os.path.dirname(__file__))\n')
            f.write('from mcomix.run import run\n')
            f.write('run()\n')
        print(f"Created launcher: {launcher}")

    cmd.append(launcher)

    # Print command
    print(f"\nRunning:\n  {' '.join(cmd)}\n")

    # Execute
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"\nERROR: PyInstaller failed with code {result.returncode}")
        sys.exit(result.returncode)

    print("\nBuild completed successfully!")


def copy_gtk_runtime(runtime_dir=None):
    """If a GTK3 runtime directory is specified, copy DLLs into the dist."""
    if not runtime_dir:
        # Try to auto-detect common GTK3 runtime locations
        candidates = [
            r'C:\gtk3-runtime',
            r'C:\Program Files\GTK3-Runtime',
            os.path.expanduser(r'~\AppData\Local\gtk3-runtime'),
        ]
        if os.name == 'nt':
            for candidate in candidates:
                if os.path.isdir(candidate):
                    runtime_dir = candidate
                    break

    if not runtime_dir or not os.path.isdir(runtime_dir):
        print("GTK3 runtime not found – PyInstaller should have bundled it already.")
        print("If icons or themes are missing, point to a GTK3 runtime with:")
        print("  --gtk-runtime C:\\path\\to\\gtk3-runtime")
        return

    print(f"Copying GTK3 runtime from {runtime_dir}...")
    dist_exe_dir = os.path.join(DIST_DIR, 'MComix3')
    if not os.path.isdir(dist_exe_dir):
        return

    # Copy GTK DLLs
    for root, dirs, files in os.walk(runtime_dir):
        for f in files:
            if f.endswith('.dll'):
                rel = os.path.relpath(root, runtime_dir)
                dst = os.path.join(dist_exe_dir, rel)
                os.makedirs(dst, exist_ok=True)
                shutil.copy2(os.path.join(root, f), dst)

    print("GTK3 runtime files copied.")


def summarize_dist():
    """Print a summary of the distribution directory."""
    dist_exe_dir = os.path.join(DIST_DIR, 'MComix3')
    if not os.path.isdir(dist_exe_dir):
        print("\nNo distribution directory found.")
        return

    total_size = 0
    file_count = 0
    exe_files = []

    for root, dirs, files in os.walk(dist_exe_dir):
        for f in files:
            fp = os.path.join(root, f)
            size = os.path.getsize(fp)
            total_size += size
            file_count += 1
            if f.endswith('.exe'):
                exe_files.append(fp)

    print(f"\n{'=' * 60}")
    print(f"Distribution summary")
    print(f"{'=' * 60}")
    print(f"  Location: {dist_exe_dir}")
    print(f"  Files:    {file_count}")
    print(f"  Size:     {total_size / (1024*1024):.1f} MB")

    for exe in exe_files:
        basename = os.path.basename(exe)
        size_kb = os.path.getsize(exe) / 1024
        print(f"  Executable: {basename} ({size_kb:.0f} KB)")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Build MComix3 Windows executable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--clean', action='store_true', default=True,
                        help='Clean build artifacts before building (default: True)')
    parser.add_argument('--no-clean', action='store_false', dest='clean',
                        help='Do not clean previous build artifacts')
    parser.add_argument('--onefile', action='store_true', default=False,
                        help='Build a single .exe file (larger startup time)')
    parser.add_argument('--console', action='store_true', default=False,
                        help='Show a console window (useful for debugging)')
    parser.add_argument('--icon', default=None,
                        help='Path to a custom .ico file for the executable')
    parser.add_argument('--gtk-runtime', default=None,
                        help='Path to GTK3 runtime directory (for copying DLLs)')

    args = parser.parse_args()

    if args.clean:
        clean()

    build_pyinstaller(
        onefile=args.onefile,
        console=args.console,
        icon=args.icon or os.path.join(PROJECT_ROOT, 'mcomix', 'images', 'mcomix.ico'),
    )

    copy_gtk_runtime(args.gtk_runtime)
    summarize_dist()


if __name__ == '__main__':
    main()
