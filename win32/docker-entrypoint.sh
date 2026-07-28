#!/bin/bash
#
# Entry point for the MComix3 Windows build container.
#
set -e

echo "=============================================="
echo " MComix3 Windows Build Container"
echo "=============================================="

# Start Xvfb for headless Wine display
rm -f /tmp/.X99-lock
Xvfb :99 -screen 0 1024x768x16 &
sleep 1

# Extract build version
VERSION=$(python3 -c "from mcomix.constants import VERSION; print(VERSION)" 2>/dev/null || \
          grep 'VERSION' /src/mcomix/constants.py | head -1 | cut -d'"'"'" -f2)
echo "Building MComix3 version ${VERSION} for Windows..."

# Run the PyInstaller build
echo ""
echo "--- Running PyInstaller ---"
wine python -m PyInstaller \
    --paths /src \
    --onefile \
    --log-level WARN \
    --name "MComix3-${VERSION}" \
    --noconfirm \
    --clean \
    --windowed \
    --additional-hooks-dir win32 \
    --icon mcomix/images/mcomix.ico \
    --collect-all gi \
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
