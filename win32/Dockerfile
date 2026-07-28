# Docker image for building MComix3 Windows executable from Linux.
#
# Builds a Wine-based Windows Python 3 environment with GTK3 + PyGObject,
# so the build system is fully automated and reproducible.
#
# Usage:
#   docker build -t mcomix3-winbuild -f win32/Dockerfile .
#   docker run --rm -v "$PWD":/src mcomix3-winbuild
#

FROM ubuntu:22.04 AS builder

LABEL description="MComix3 Windows cross-build environment"

ENV DEBIAN_FRONTEND=noninteractive

# ------------------------------------------------------------------
# Base system: Wine, Xvfb (headless display for Wine), Python 3 for
# the build script itself, and download tools.
# ------------------------------------------------------------------
RUN dpkg --add-architecture i386 && apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    xvfb \
    wine \
    wine32 \
    xauth \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------
# Wine prefix setup (Windows 10, 32-bit)
# ------------------------------------------------------------------
ENV WINEPREFIX=/wine \
    WINEARCH=win32 \
    WINEDLLOVERRIDES="winemenubuilder.exe=d;mscoree=d;mshtml=d" \
    DISPLAY=:99.0

RUN rm -rf /wine /tmp/.X99-lock && Xvfb :99 -screen 0 1024x768x16 & \
    wine wineboot --init && \
    wineserver -w

# Install Python 3.8 for Windows (32-bit) using the official installer.
# The installer-based approach worked reliably on Ubuntu 22.04 / Wine 6.
# Use Python 3.10 embeddable package (zip) - extract on Linux, then bootstrap pip.
# The EXE installer doesn't work in Wine 6.0.3, but the zip works natively.
ARG PYTHON_VERSION=3.10.11
ARG PYTHON_ZIP=python-${PYTHON_VERSION}-embed-win32.zip

RUN apt-get update && apt-get install -y --no-install-recommends unzip && \
    wget -qL https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_ZIP} \
         -O /tmp/${PYTHON_ZIP} && \
    mkdir -p /wine/drive_c/Python310 && \
    unzip -q /tmp/${PYTHON_ZIP} -d /wine/drive_c/Python310 && \
    # Enable pip by modifying the _pth file
    sed -i 's/^#import site/import site/' /wine/drive_c/Python310/python310._pth 2>/dev/null || true && \
    rm /tmp/${PYTHON_ZIP}

# Install pip using get-pip.py for Python 3.10
RUN wget -qL https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py && \
    rm -f /tmp/.X99-lock && Xvfb :99 -screen 0 1024x768x16 & sleep 1 && \
    wine C:\\Python310\\python.exe /tmp/get-pip.py --no-warn-script-location && \
    wineserver -w && \
    rm /tmp/get-pip.py



# Download GTK3 runtime from MSYS2 mingw32 repo
RUN apt-get update && apt-get install -y --no-install-recommends p7zip-full curl zstd && \
    echo "Downloading GTK3 packages..." && \
    mkdir -p /tmp/gtk3-root && \
    for url in \
        "https://github.com/wingtk/gtk3-bundle/releases/download/continuous/gtk3-3.24.38-2024-03-30-msvc-win32.zip" \
        "https://github.com/wingtk/gtk3-bundle/releases/latest/download/gtk3-win32.zip"; \
    do \
        curl -fL "$url" -o /tmp/gtk3.zip 2>/dev/null && break; \
    done || true && \
    if [ -f /tmp/gtk3.zip ] && [ -s /tmp/gtk3.zip ]; then \
        unzip -q /tmp/gtk3.zip -d /tmp/gtk3-root && \
        cp -r /tmp/gtk3-root/* /wine/drive_c/GTK3-Runtime/ 2>/dev/null || true && \
        rm -rf /tmp/gtk3.zip; \
    else \
        echo "WARNING: Could not download GTK3 runtime - will try pip install pygobject==3.48.2 anyway"; \
    fi
# Add GTK3 runtime to Wine's PATH
ENV WINEPATH="C:\Python310;C:\Python310\Scripts;C:\Program Files\GTK3-Runtime\bin"

# Install PyGObject, PyInstaller, Pillow via pip
# PyGObject 3.48.x has pre-built wheels for Python 3.9 on Windows
RUN rm -f /tmp/.X99-lock && Xvfb :99 -screen 0 1024x768x16 & sleep 1 && \
    wine python -m pip install --upgrade pip && \
    # Explicit platform targeting to find pre-built wheels
    wine python -m pip install \
        pyinstaller \
        pillow && \
    # Download pygobject wheel on Linux side (correct platform detection), then install in Wine
    apt-get install -y --no-install-recommends python3-pip && \
    python3 -m pip download --only-binary :all: --no-deps \
        --python-version 3.10 --platform win32 --implementation cp \
        --abi cp310 --dest /tmp/pygobject-wheel pygobject 2>/dev/null || true && \
    for whl in /tmp/pygobject-wheel/pygobject*.whl; do \
        if [ -f "$whl" ]; then \
            cp "$whl" /wine/drive_c/ && \
            wine python -m pip install "C:\\$(basename $whl)" && \
            echo "pygobject installed from $(basename $whl)"; \
        fi; \
    done && \
    rm -rf /tmp/pygobject-wheel /wine/drive_c/pygobject*.whl && \
    wineserver -w
WORKDIR /src
COPY win32/docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
