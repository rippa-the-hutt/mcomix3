FROM ubuntu:22.04 AS builder
LABEL description="MComix3 Windows cross-build environment"
ENV DEBIAN_FRONTEND=noninteractive

RUN dpkg --add-architecture i386 && apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates wget xvfb wine wine32 xauth python3 python3-pip unzip zstd curl \
    && rm -rf /var/lib/apt/lists/*

ENV WINEPREFIX=/wine WINEARCH=win32 \
    WINEDLLOVERRIDES="winemenubuilder.exe=d;mscoree=d;mshtml=d" \
    WINEDEBUG=-all DISPLAY=:99.0

RUN rm -rf /wine /tmp/.X99-lock && Xvfb :99 -screen 0 1024x768x16 & \
    wine wineboot --init && wineserver -w

# Python 3.11 embeddable
ARG PYTHON_VERSION=3.11.9
ARG PYTHON_ZIP=python-${PYTHON_VERSION}-embed-win32.zip
RUN wget -qL https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_ZIP} -O /tmp/${PYTHON_ZIP} && \
    mkdir -p /wine/drive_c/Python311 && unzip -q /tmp/${PYTHON_ZIP} -d /wine/drive_c/Python311 && \
    sed -i 's/^#import site/import site/' /wine/drive_c/Python311/python311._pth 2>/dev/null || true && \
    rm /tmp/${PYTHON_ZIP}

# Install pip
RUN wget -qL https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py && \
    rm -f /tmp/.X99-lock && Xvfb :99 -screen 0 1024x768x16 & sleep 1 && \
    wine C:\\Python311\\python.exe /tmp/get-pip.py --no-warn-script-location && \
    wineserver -w && rm /tmp/get-pip.py

# Install packages
RUN rm -f /tmp/.X99-lock && Xvfb :99 -screen 0 1024x768x16 & sleep 1 && \
    wine C:\\Python311\\python.exe -m pip install pyinstaller pillow && \
    wineserver -w

ENV WINEPATH="C:\\Python311;C:\\Python311\\Scripts"
WORKDIR /src
COPY win32/docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
