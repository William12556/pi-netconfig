#!/bin/bash
# Pi-Netconfig Build Script
# Cleans previous builds and creates fresh distribution package

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Cleaning previous builds..."
cd "$PROJECT_ROOT"
rm -rf dist/ build/ *.egg-info/ src/*.egg-info/

echo "==> Building distribution..."
python3 -m build

echo "==> Build complete!"
echo ""
ls -lh dist/

echo ""
echo "Distribution ready in dist/"
echo "Transfer to Pi: scp dist/pi_netconfig-*.whl admin@deb1:/tmp/"
