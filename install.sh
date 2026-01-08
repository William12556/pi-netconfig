#!/bin/bash
# Pi-Netconfig Install Script
# Clean uninstall, fresh install, version verification
# Usage: ./install.sh <wheel-filename>

set -e  # Exit on error

if [ -z "$1" ]; then
    echo "ERROR: Wheel filename required"
    echo "Usage: ./install.sh pi_netconfig-X.Y.Z-py3-none-any.whl"
    exit 1
fi

WHEEL="$1"
VERSION=$(echo "$WHEEL" | cut -d'-' -f2)

echo "==> Installing pi-netconfig version $VERSION"

# Stop service (ignore if not running)
echo "==> Stopping service..."
sudo systemctl stop pi-netconfig || true

# Uninstall existing package
echo "==> Cleaning existing installation..."
sudo /opt/pi-netconfig/venv/bin/pip uninstall -y pi_netconfig 2>/dev/null || true

# Verify venv exists
if [ ! -d "/opt/pi-netconfig/venv" ]; then
    echo "ERROR: Virtual environment not found at /opt/pi-netconfig/venv"
    echo "For first-time installation, use deploy_test-guide.md procedures"
    exit 1
fi

# Clear cache
echo "==> Clearing package cache..."
sudo rm -rf /opt/pi-netconfig/venv/lib/python*/site-packages/pi_netconfig*

# Install new version
echo "==> Installing from /tmp/$WHEEL"
sudo /opt/pi-netconfig/venv/bin/pip install "/tmp/$WHEEL"

# Verify version
echo "==> Verifying installation..."
INSTALLED=$(/opt/pi-netconfig/venv/bin/python -c "import pi_netconfig; print(pi_netconfig.__version__)")

if [ "$INSTALLED" != "$VERSION" ]; then
    echo "ERROR: Version mismatch - expected $VERSION, got $INSTALLED"
    exit 1
fi

# Start service
echo "==> Starting service..."
sudo systemctl start pi-netconfig

echo ""
echo "✓ Installation successful: version $INSTALLED"
echo ""
sudo systemctl status pi-netconfig --no-pager -l | head -10
