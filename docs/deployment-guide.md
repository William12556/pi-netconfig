# Pi-Netconfig Deployment Guide

## Table of Contents

- [Overview](<#overview>)
- [Development Environment Setup](<#development environment setup>)
- [Building Distribution Package](<#building distribution package>)
- [Raspberry Pi Deployment](<#raspberry pi deployment>)
- [Service Management](<#service management>)
- [Troubleshooting](<#troubleshooting>)
- [Version History](<#version history>)

## Overview

This guide covers deployment of pi-netconfig to Raspberry Pi using Python wheel distribution. The deployment process separates development and production environments while maintaining consistent import behavior across both contexts.

**Deployment Method:** Python wheel package distribution

**Target Platform:** Raspberry Pi running Raspbian Bookworm or Debian-based Linux

[Return to Table of Contents](<#table of contents>)

## Development Environment Setup

### Prerequisites

- Python 3.9 or higher
- Git (for repository access)
- Virtual environment support

### Initial Setup

```bash
# Clone repository
cd /path/to/workspace
git clone <repository-url> pi-netconfig
cd pi-netconfig

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package in editable mode with development dependencies
pip install -e ".[dev]"
```

### Development Workflow

The package structure uses `src/` layout with setuptools configuration in `pyproject.toml`. Editable installation (`-e` flag) allows code changes to be immediately available without reinstallation.

**Running Tests:**

```bash
# From repository root with venv activated
pytest src/tests/
```

**Import Behavior:**

All modules import correctly in development due to editable package installation:
```python
from pi_netconfig.statemonitor import StateMonitor
from pi_netconfig.connectionmanager import ConnectionManager
```

[Return to Table of Contents](<#table of contents>)

## Building Distribution Package

### Install Build Tools

```bash
# In development environment
pip install build
```

### Build Wheel

```bash
# From repository root
python -m build
```

**Output:**
```
dist/
├── pi_netconfig-0.2.0-py3-none-any.whl
└── pi_netconfig-0.2.0.tar.gz
```

The `.whl` file is the distribution package for deployment.

### Build Artifacts

- **Wheel file**: Platform-independent Python package containing all source code
- **Source distribution**: Compressed source archive (optional, not required for deployment)

### Version Management

Version is defined in `pyproject.toml`:
```toml
[project]
version = "0.2.0"
```

Update version before building new releases.

[Return to Table of Contents](<#table of contents>)

## Raspberry Pi Deployment

### Prerequisites

Raspberry Pi must have:
- NetworkManager installed and running
- Python 3.9 or higher
- Root access (for systemd service installation)
- Network connectivity for initial pip installation

### Transfer Distribution

```bash
# From development machine
scp dist/pi_netconfig-0.2.0-py3-none-any.whl admin@raspberry-pi:/tmp/
```

Replace `admin@raspberry-pi` with appropriate username and hostname.

### Install Package

```bash
# On Raspberry Pi
ssh admin@raspberry-pi
sudo pip install /tmp/pi_netconfig-0.2.0-py3-none-any.whl
```

**Installation Location:**

Package installs to system Python site-packages (typically `/usr/local/lib/python3.x/site-packages/`).

### Run Installer

First execution installs the systemd service:

```bash
sudo python3 -m pi_netconfig.main
```

**Installer Actions:**
1. Verifies root privileges
2. Detects if running as systemd service
3. If not service: installs systemd unit file and enables service
4. Exits after installation (systemd starts service automatically)

### Service Startup

After installation, systemd starts the service automatically. The service:
1. Initializes state machine
2. Tests WiFi connection
3. If connected: operates in CLIENT mode
4. If disconnected (3 consecutive failures): activates AP_MODE

### Access Point Mode

When no WiFi connection available:

**SSID:** `PiConfig-<MAC>`  
**Password:** `piconfig123`  
**Web Interface:** `http://192.168.50.1:8080`

Connect to access point and navigate to web interface to configure WiFi credentials.

[Return to Table of Contents](<#table of contents>)

## Service Management

### SystemD Commands

```bash
# Check service status
sudo systemctl status pi-netconfig

# View service logs
sudo journalctl -u pi-netconfig -f

# Restart service
sudo systemctl restart pi-netconfig

# Stop service
sudo systemctl stop pi-netconfig

# Start service
sudo systemctl start pi-netconfig

# Disable service (prevent automatic start)
sudo systemctl disable pi-netconfig

# Enable service (automatic start on boot)
sudo systemctl enable pi-netconfig
```

### Log Files

Service logs to journald. Access logs:

```bash
# Tail logs (follow mode)
sudo journalctl -u pi-netconfig -f

# View last 100 lines
sudo journalctl -u pi-netconfig -n 100

# View logs since boot
sudo journalctl -u pi-netconfig -b

# View logs with timestamps
sudo journalctl -u pi-netconfig --since "1 hour ago"
```

### Service File Location

`/etc/systemd/system/pi-netconfig.service`

### Configuration Persistence

WiFi credentials stored in NetworkManager configuration:
`/etc/NetworkManager/system-connections/`

[Return to Table of Contents](<#table of contents>)

## Troubleshooting

### Import Errors

**Symptom:** `ImportError: cannot import name 'StateMonitor' from 'statemonitor'`

**Cause:** Package not properly installed

**Solution:**
```bash
# Verify installation
pip list | grep pi-netconfig

# Reinstall if missing
sudo pip install --force-reinstall /tmp/pi_netconfig-0.2.0-py3-none-any.whl
```

### Service Fails to Start

**Check Status:**
```bash
sudo systemctl status pi-netconfig
```

**Check Logs:**
```bash
sudo journalctl -u pi-netconfig -n 50
```

**Common Issues:**
- Missing NetworkManager: `sudo apt install network-manager`
- Permission errors: Service must run as root
- Python version: Requires Python 3.9+

### Access Point Not Appearing

**Verify AP Manager:**
```bash
# Check if AP interface created
nmcli device status

# Check connection profiles
nmcli connection show
```

**Manual AP Activation:**
```bash
# Access Pi via ethernet or existing WiFi
sudo systemctl restart pi-netconfig
sudo journalctl -u pi-netconfig -f
```

### Web Interface Unreachable

**Verify Service State:**
```bash
# Check if service in AP_MODE
sudo journalctl -u pi-netconfig | grep "AP_MODE"

# Verify web server port
sudo netstat -tlnp | grep 8080
```

**Firewall Check:**
```bash
# If firewall enabled, allow port 8080
sudo ufw allow 8080/tcp
```

### Package Update Deployment

```bash
# On development machine - build new version
python -m build

# Transfer to Pi
scp dist/pi_netconfig-0.2.0-py3-none-any.whl admin@raspberry-pi:/tmp/

# On Pi - stop service, upgrade, restart
sudo systemctl stop pi-netconfig
sudo pip install --upgrade /tmp/pi_netconfig-0.2.0-py3-none-any.whl
sudo systemctl start pi-netconfig
```

[Return to Table of Contents](<#table of contents>)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-27 | Initial deployment guide with wheel distribution method |

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
