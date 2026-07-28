#!/bin/bash
#
# Build MComix3 Windows executable from Linux using Docker.
#
# This script builds a Docker image with a complete Wine + Python 3.8
# + GTK3 + PyGObject + PyInstaller environment, then runs it to produce
# a Windows .exe in the dist/ directory.
#
# Usage:
#   ./win32/docker-build.sh          # Full build (image + exe)
#   ./win32/docker-build.sh --no-build  # Skip image build, just run
#   ./win32/docker-build.sh --shell     # Open shell in build container
#
# Prerequisites: Docker
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
IMAGE_NAME="mcomix3-winbuild"
SKIP_BUILD=false
SHELL_MODE=false

# Parse arguments
for arg in "$@"; do
    case "$arg" in
        --no-build) SKIP_BUILD=true ;;
        --shell)    SHELL_MODE=true ;;
        --help)
            echo "Usage: $0 [--no-build] [--shell]"
            echo ""
            echo "  --no-build   Skip Docker image build, just run container"
            echo "  --shell      Open an interactive shell in the container"
            exit 0
            ;;
    esac
done

# ------------------------------------------------------------------
# Build the Docker image
# ------------------------------------------------------------------
if [ "$SKIP_BUILD" = false ]; then
    echo "=============================================="
    echo " Building Docker image: ${IMAGE_NAME}"
    echo " (This may take a while on first run...)"
    echo "=============================================="
    echo ""

    docker build \
        --tag "${IMAGE_NAME}" \
        --file "${SCRIPT_DIR}/Dockerfile" \
        "${PROJECT_DIR}"

    echo ""
    echo "Docker image built successfully."
    echo ""
fi

# ------------------------------------------------------------------
# Run the build
# ------------------------------------------------------------------
if [ "$SHELL_MODE" = true ]; then
    echo "Starting interactive shell..."
    docker run --rm -it \
        -v "${PROJECT_DIR}:/src" \
        --entrypoint /bin/bash \
        "${IMAGE_NAME}"
else
    echo "=============================================="
    echo " Building MComix3 Windows executable..."
    echo "=============================================="
    echo ""

    docker run --rm \
        -v "${PROJECT_DIR}:/src" \
        "${IMAGE_NAME}"

    echo ""
    echo "Windows executable should be at:"
    echo "  ${PROJECT_DIR}/dist/"
    echo ""
    echo "To rebuild without rebuilding the image:"
    echo "  ./win32/docker-build.sh --no-build"
fi
