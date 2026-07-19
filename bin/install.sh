#!/bin/bash
# Pi-Netconfig Install Script
#
# Usage:
#   ./install.sh                              # fetch latest release from GitHub
#   ./install.sh <version>                    # fetch specific version from GitHub
#   ./install.sh <path-to-wheel>              # install from local wheel file
#
# First-time install: creates venv, installs package, registers systemd
#   service via `python -m pi_netconfig.installer --install --systemd-mode`.
# Upgrade: stops service, cleans existing install, reinstalls, verifies,
#   restarts.

set -e  # Exit on error

INSTALL_DIR="/opt/pi-netconfig"
VENV_DIR="$INSTALL_DIR/venv"
GITHUB_REPO="William12556/pi-netconfig"
GITHUB_API="https://api.github.com/repos/${GITHUB_REPO}/releases"

# ---------------------------------------------------------------------------
# Resolve wheel: local file, specific version, or latest release
# ---------------------------------------------------------------------------
WHEEL_PATH=""

if [ -z "$1" ] || [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    # No argument or version string: download from GitHub releases
    if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
        echo "ERROR: curl or wget required for GitHub download"
        exit 1
    fi

    if [ -z "$1" ]; then
        echo "==> Fetching latest release from GitHub..."
        RELEASE_URL="${GITHUB_API}/latest"
    else
        echo "==> Fetching release $1 from GitHub..."
        RELEASE_URL="${GITHUB_API}/tags/$1"
    fi

    if command -v curl >/dev/null 2>&1; then
        RELEASE_JSON=$(curl -fsSL "$RELEASE_URL")
    else
        RELEASE_JSON=$(wget -qO- "$RELEASE_URL")
    fi

    WHEEL_URL=$(echo "$RELEASE_JSON" | grep -o '"browser_download_url": *"[^"]*\.whl"' | grep -o 'https://[^"]*')
    VERSION=$(echo "$RELEASE_JSON" | grep -o '"tag_name": *"[^"]*"' | grep -o '[0-9][^"]*')

    if [ -z "$WHEEL_URL" ]; then
        echo "ERROR: Could not find wheel asset in release"
        exit 1
    fi

    WHEEL_PATH="/tmp/pi_netconfig-${VERSION}-py3-none-any.whl"
    echo "==> Downloading wheel: $WHEEL_URL"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$WHEEL_URL" -o "$WHEEL_PATH"
    else
        wget -qO "$WHEEL_PATH" "$WHEEL_URL"
    fi

elif [ -f "$1" ]; then
    # Local wheel file
    if [[ "$1" = /* ]]; then
        WHEEL_PATH="$1"
    else
        WHEEL_PATH="$(pwd)/$1"
    fi
    VERSION=$(basename "$WHEEL_PATH" | cut -d'-' -f2)

else
    echo "ERROR: Argument is not a file or version string: $1"
    echo "Usage: ./install.sh [version|path-to-wheel]"
    exit 1
fi

if [ ! -f "$WHEEL_PATH" ]; then
    echo "ERROR: Wheel file not found: $WHEEL_PATH"
    exit 1
fi

echo "==> Installing pi-netconfig version $VERSION"
echo "==> Install directory: $INSTALL_DIR"

# ---------------------------------------------------------------------------
# First-time install: venv absent
# ---------------------------------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "==> No existing installation found. Performing first-time install."

    if ! command -v python3 >/dev/null 2>&1; then
        echo "ERROR: python3 not found"
        exit 1
    fi

    echo "==> Creating virtual environment at $VENV_DIR"
    sudo mkdir -p "$INSTALL_DIR"
    sudo python3 -m venv "$VENV_DIR"

    echo "==> Installing from $WHEEL_PATH"
    sudo "$VENV_DIR/bin/pip" install "$WHEEL_PATH"

    echo "==> Verifying installation..."
    INSTALLED=$(sudo "$VENV_DIR/bin/python" -c "import pi_netconfig; print(pi_netconfig.__version__)")

    if [ "$INSTALLED" != "$VERSION" ]; then
        echo "ERROR: Version mismatch - expected $VERSION, got $INSTALLED"
        exit 1
    fi

    echo "==> Registering systemd service..."
    sudo "$VENV_DIR/bin/python" -m pi_netconfig.installer --install --systemd-mode

    echo ""
    echo "✓ Installation successful: version $INSTALLED"
    echo ""
    sudo systemctl status pi-netconfig --no-pager -l | head -10
    exit 0
fi

# ---------------------------------------------------------------------------
# Upgrade: venv present
# ---------------------------------------------------------------------------
echo "==> Existing installation found. Performing upgrade."

echo "==> Stopping service..."
sudo systemctl stop pi-netconfig || true

echo "==> Cleaning existing installation..."
sudo "$VENV_DIR/bin/pip" uninstall -y pi_netconfig 2>/dev/null || true

echo "==> Clearing package cache..."
sudo rm -rf "$VENV_DIR"/lib/python*/site-packages/pi_netconfig*

echo "==> Installing from $WHEEL_PATH"
sudo "$VENV_DIR/bin/pip" install "$WHEEL_PATH"

echo "==> Verifying installation..."
INSTALLED=$(sudo "$VENV_DIR/bin/python" -c "import pi_netconfig; print(pi_netconfig.__version__)")

if [ "$INSTALLED" != "$VERSION" ]; then
    echo "ERROR: Version mismatch - expected $VERSION, got $INSTALLED"
    exit 1
fi

echo "==> Starting service..."
sudo systemctl start pi-netconfig

echo ""
echo "✓ Installation successful: version $INSTALLED"
echo ""
sudo systemctl status pi-netconfig --no-pager -l | head -10
