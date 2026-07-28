#!/bin/bash
set -e
echo "=============================================="
echo " MComix3 Windows Build Container"
echo "=============================================="
rm -f /tmp/.X99-lock
Xvfb :99 -screen 0 1024x768x16 &
sleep 1
VERSION=$(python3 -c "from mcomix.constants import VERSION; print(VERSION)" 2>/dev/null || \
          grep 'VERSION' /src/mcomix/constants.py | head -1 | cut -d'"' -f2)
echo "Building MComix3 version ${VERSION} for Windows..."
echo ""
echo "--- Checking Python environment ---"
wine C:\\Python311\\python.exe -c "
import sys
print('Python:', sys.version)
try:
    import gi
    print('PyGObject:', gi.__version__)
except ImportError:
    print('Note: gi module not available (GTK support disabled)')
    print('To add GTK support, pip install pygobject on the target Windows machine.')
" 2>&1
echo ""
echo "--- Running PyInstaller ---"
wine C:\\Python311\\python.exe -m PyInstaller \
    --paths /src \
    --onefile \
    --log-level WARN \
    --name "MComix3-${VERSION}" \
    --noconfirm \
    --clean \
    --windowed \
    --additional-hooks-dir win32 \
    --icon mcomix/images/mcomix.ico \
    --collect-all mcomix \
    --collect-submodules PIL \
    --exclude-module PyQt5 \
    --exclude-module PyQt6 \
    --exclude-module PySide2 \
    --exclude-module PySide6 \
    --exclude-module matplotlib \
    --exclude-module tkinter \
    --exclude-module IPython \
    --exclude-module notebook \
    win32/launcher.py
echo ""
echo "================================================"
echo " Build complete!"
echo " Output: /src/dist/MComix3-${VERSION}/"
echo "================================================"
