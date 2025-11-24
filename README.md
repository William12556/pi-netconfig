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

## Installation

```bash
# Copy required files to Raspberry Pi
scp -r src/ pyproject.toml admin@raspberry-pi:/home/admin/pi-netconfig/

# On Raspberry Pi, create virtual environment
cd /home/admin/pi-netconfig
python3 -m venv pi-netconfig-venv
source pi-netconfig-venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run as root to install service (first execution only)
sudo pi-netconfig-venv/bin/python3 src/main.py

# Service starts automatically after installation
# If no WiFi connection: connect to "PiConfig-XXXX" network (password: piconfig123)
# Access configuration at http://192.168.50.1:8080
```

## Testing

```bash
# On Raspberry Pi with virtual environment activated
cd /home/admin/pi-netconfig
source pi-netconfig-venv/bin/activate
pytest src/tests/
```

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
