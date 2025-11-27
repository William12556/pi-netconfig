# Pi Network Configuration Tool

HTML based WiFi configuration management for Raspberry Pi/Debian systems.

## Overview

Tool manages WiFi connectivity with automatic fallback to access point mode when no connection is available.

## Features

- Self-installing systemd service (runs on first execution)
- Automatic WiFi connectivity monitoring
- Access point mode with web interface (192.168.50.1:8080) when no connection available
- Network scanning and configuration through browser
- Single network profile persistence
- State-based operation (CHECKING → CLIENT ↔ AP_MODE)

## Requirements

- Raspberry Pi running Raspbian Bookworm or Debian-based Linux
- NetworkManager (standard in modern Raspbian)
- Python 3.11 or higher
- Root privileges for installation and network operations

## Development Setup

**Initial Setup (one-time):**

```bash
cd /path/to/pi-netconfig
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

Editable installation (`-e` flag) makes imports work during development without reinstalling after code changes.

**Running Tests:**

```bash
# With virtual environment activated
pytest src/tests/
```

## Building for Deployment

**Create Distribution Package:**

```bash
# On development machine (Mac/Linux)
cd /path/to/pi-netconfig
pip install build
python -m build
```

Creates `dist/pi_netconfig-0.2.0-py3-none-any.whl`

## Deployment to Raspberry Pi

**Transfer and Install on Raspberry Pi:**

```bash
# Transfer wheel file
scp dist/pi_netconfig-0.2.0-py3-none-any.whl admin@raspberry-pi:/tmp/

# On Raspberry Pi
ssh admin@raspberry-pi
sudo pip install /tmp/pi_netconfig-0.2.0-py3-none-any.whl

# Run installer (first execution only - installs systemd service)
sudo python3 -m pi_netconfig.main
```

**Post-Installation:**

Service starts automatically. If no WiFi connection available:
1. Connect to access point: `PiConfig-XXXX` (password: `piconfig123`)
2. Access web interface: `http://192.168.50.1:8080`
3. Configure WiFi network through browser

**Service Management:**

```bash
# Check status
sudo systemctl status pi-netconfig

# View logs
sudo journalctl -u pi-netconfig -f

# Restart service
sudo systemctl restart pi-netconfig

# Stop service
sudo systemctl stop pi-netconfig
```

## Testing

```bash
# On Raspberry Pi with virtual environment activated
cd /home/admin/pi-netconfig
source pi-netconfig-venv/bin/activate
pytest src/tests/
```

### Test Status

**Current Pass Rate: 164/165 (99.4%)**

Module test results:
- APManager: 24/24 (100%)
- ConnectionManager: 19/19 (100%)
- Installer: 17/17 (100%)
- ServiceController: 44/44 (100%)
- StateMonitor: 24/25 (96%) - 1 async timing test pending fix
- WebServer: 27/27 (100%)

Known issue:
- issue-0007: StateMonitor async test timing race condition (non-blocking)

## Architecture

State machine managing three operational modes:
- **CHECKING**: Monitors connection status every 30 seconds
- **CLIENT**: Connected to configured WiFi network
- **AP_MODE**: Creates access point with web interface for configuration

Components:
- Installer: Self-bootstrapping systemd service setup
- StateMonitor: Operational state coordination
- ConnectionManager: WiFi client operations
- APManager: Access point creation
- WebServer: HTML configuration interface (port 8080)
- ServiceController: Application lifecycle management

## Important Notice
This software is currently very unproven and in early development stages. The implementation is experimental in nature, serving as a learning exercise in AI-assisted development workflows, protocol-driven project management, and cross-platform embedded systems development. **Actual fitness for purpose is not guaranteed.**

This project represents a first attempt at AI-supported software development using Claude Desktop and Claude Code from anthropic.com. The objective is to establish a sort of AI orchestration framework to guide software development. A kind of AI wrangler if you will.

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
