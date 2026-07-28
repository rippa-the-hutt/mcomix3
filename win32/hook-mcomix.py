"""PyInstaller hook for MComix3 (Python 3 / GTK 3).

This hook tells PyInstaller what data files, hidden imports, and
binaries need to be bundled with the MComix3 executable.

It is automatically discovered by PyInstaller when placed in the
additional hooks directory (--additional-hooks-dir=win32).
"""

import sys
import os
from PyInstaller.utils.hooks import (
    collect_data_files, collect_submodules, collect_dynamic_libs,
    get_package_paths
)

# ---------------------------------------------------------------------------
# Data files
# ---------------------------------------------------------------------------

# Collect all images (*.png, *.ico) from mcomix.images package.
datas = collect_data_files('mcomix.images', include_py_files=False)

# Collect all translations (*.mo) from mcomix.messages package.
datas += collect_data_files('mcomix.messages', include_py_files=False)

# ---------------------------------------------------------------------------
# Hidden imports – modules that PyInstaller cannot detect statically
# ---------------------------------------------------------------------------

hiddenimports = []

# All MComix submodules
hiddenimports += collect_submodules('mcomix')

# GTK introspection modules used by MComix
hiddenimports += [
    'gi',
    'gi.repository.Gtk',
    'gi.repository.Gdk',
    'gi.repository.GdkPixbuf',
    'gi.repository.Gio',
    'gi.repository.GLib',
    'gi.repository.Pango',
    'gi.repository.PangoCairo',
    'gi.repository.cairo',
]

# Pillow image format plugins – these are loaded dynamically by PIL
hiddenimports += [
    'PIL.Image',
    'PIL.ImageFile',
    'PIL._imaging',
    'PIL.BmpImagePlugin',
    'PIL.GifImagePlugin',
    'PIL.JpegImagePlugin',
    'PIL.PngImagePlugin',
    'PIL.TiffImagePlugin',
    'PIL.IcoImagePlugin',
    'PIL.WebPImagePlugin',
]

# ---------------------------------------------------------------------------
# Binaries – native DLLs that must be bundled alongside the exe
# ---------------------------------------------------------------------------

binaries = []

# Collect GTK3 / PyGObject native DLLs
if sys.platform == 'win32':
    # Collect gi DLLs (libgobject, libglib, etc.)
    try:
        binaries += collect_dynamic_libs('gi')
    except Exception:
        pass

    # Collect GTK3 runtime DLLs from the Python site-packages/gnome directory
    for pkg_name in ('gi', 'PyGObject', 'gtk', 'pygobject'):
        try:
            pkg_paths = get_package_paths(pkg_name)
            for path in pkg_paths:
                # Look for .dll files in the package directory
                for root, dirs, files in os.walk(path):
                    for f in files:
                        if f.endswith('.dll'):
                            binaries.append((
                                os.path.join(root, f),
                                os.path.relpath(root, os.path.dirname(path))
                            ))
        except Exception:
            pass

# ---------------------------------------------------------------------------
# External tool binaries (optional – bundled if present on the build machine)
# ---------------------------------------------------------------------------

def _collect_tool(tool_name, tool_subdir):
    """If <tool_name> is found on PATH, add it to binaries."""
    which = __import__('shutil', fromlist=['which']).which
    exe = which(tool_name)
    if exe is not None:
        binaries.append((exe, tool_subdir))

# Archive backends
_collect_tool('unrar.exe', '.')
_collect_tool('rar.exe', '.')
_collect_tool('7z.exe', '.')
_collect_tool('7z.dll', '.')
_collect_tool('lha.exe', '.')
_collect_tool('mudraw.exe', '.')
_collect_tool('mutool.exe', '.')
