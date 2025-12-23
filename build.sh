#!/bin/bash
# Pi-Netconfig Build Script
# Cleans previous builds, updates version, creates distribution package

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Verify python3.11 is available
if ! command -v python3.11 >/dev/null 2>&1; then
    echo "ERROR: python3.11 not found"
    echo "Install: brew install python@3.11"
    exit 1
fi

# Verify build module is available
if ! python3.11 -m build --version >/dev/null 2>&1; then
    echo "ERROR: build module not found for python3.11"
    echo "Install: python3.11 -m pip install build"
    exit 1
fi

# Extract version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)

if [ -z "$VERSION" ]; then
    echo "ERROR: Could not extract version from pyproject.toml"
    exit 1
fi

echo "==> Building pi-netconfig version $VERSION"

# Update __init__.py with version
echo "==> Updating version in __init__.py..."
echo "__version__ = '$VERSION'" > src/pi_netconfig/__init__.py

# Clean previous builds
echo "==> Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/ src/*.egg-info/

# Build distribution
echo "==> Building distribution..."
python3.11 -m build

# Verify wheel exists
WHEEL="dist/pi_netconfig-${VERSION}-py3-none-any.whl"
if [ ! -f "$WHEEL" ]; then
    echo "ERROR: Expected wheel not found: $WHEEL"
    exit 1
fi

echo ""
echo "✓ Build successful: version $VERSION"
ls -lh "$WHEEL"
echo ""
echo "Transfer to Pi: scp dist/pi_netconfig-${VERSION}-py3-none-any.whl admin@deb1:/tmp/"
