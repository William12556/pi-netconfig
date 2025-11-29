Created: 2025 November 29

# Pi Network Configuration Tool - User Guide

## Table of Contents

- [Introduction](<#introduction>)
- [Installation and Environment Setup](<#installation and environment setup>)
  - [Development Environment](<#development environment>)
  - [Running Tests](<#running tests>)
- [Build and Deployment Procedures](<#build and deployment procedures>)
  - [Creating Distribution Package](<#creating distribution package>)
  - [Deployment to Raspberry Pi](<#deployment to raspberry pi>)
  - [Post-Installation](<#post-installation>)
- [Service Lifecycle Management](<#service lifecycle management>)
  - [Service Status](<#service status>)
  - [Service Control](<#service control>)
  - [Log Viewing](<#log viewing>)
- [Web Interface Operation](<#web interface operation>)
  - [Accessing the Interface](<#accessing the interface>)
  - [Network Configuration](<#network configuration>)
- [Testing Execution](<#testing execution>)
  - [Development Testing](<#development testing>)
  - [Deployment Testing](<#deployment testing>)
- [Architecture Description](<#architecture description>)
  - [Operational Modes](<#operational modes>)
  - [System Components](<#system components>)
- [Troubleshooting Guidance](<#troubleshooting guidance>)
  - [Service Not Starting](<#service not starting>)
  - [Access Point Not Visible](<#access point not visible>)
  - [Cannot Connect to Web Interface](<#cannot connect to web interface>)
  - [WiFi Configuration Not Persisting](<#wifi configuration not persisting>)
- [Version History](<#version history>)

## Introduction

Pi Network Configuration Tool provides WiFi configuration management for Raspberry Pi and Debian-based systems with automatic fallback to access point mode when no connection is available. The tool operates as a systemd service, continuously monitoring network connectivity and providing a web-based configuration interface when needed.

**Key Features:**

- Self-installing systemd service (runs on first execution)
- Automatic WiFi connectivity monitoring
- Access point mode with web interface (192.168.50.1:8080) when no connection available
- Network scanning and configuration through browser
- Single network profile persistence
- State-based operation (CHECKING → CLIENT ↔ AP_MODE)

The tool is designed for headless Raspberry Pi deployments where physical display and keyboard access is not available, enabling WiFi configuration through the web interface without requiring direct system access.

**System Requirements:**

- Raspberry Pi running Raspbian Bookworm or Debian-based Linux
- NetworkManager (standard in modern Raspbian)
- Python 3.11 or higher
- Root privileges for installation and network operations

[Return to Table of Contents](<#table of contents>)

## Installation and Environment Setup

### Development Environment

For development work on the codebase, set up a Python virtual environment.

**Initial Setup (one-time):**

```bash
cd /path/to/pi-netconfig
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

The editable installation (`-e` flag) allows imports to work during development without reinstalling after code changes.

### Running Tests

Execute the test suite within the activated virtual environment:

```bash
# With virtual environment activated
pytest src/tests/
```

[Return to Table of Contents](<#table of contents>)

## Build and Deployment Procedures

### Creating Distribution Package

Build the wheel package on your development machine:

```bash
# On development machine (Mac/Linux)
cd /path/to/pi-netconfig
pip install build
python -m build
```

This creates `dist/pi_netconfig-0.2.0-py3-none-any.whl`

### Deployment to Raspberry Pi

**Transfer wheel file to target system:**

```bash
scp dist/pi_netconfig-0.2.0-py3-none-any.whl admin@raspberry-pi:/tmp/
```

**Install on Raspberry Pi:**

```bash
# Connect to Raspberry Pi
ssh admin@raspberry-pi

# Install package
sudo pip install /tmp/pi_netconfig-0.2.0-py3-none-any.whl

# Run installer (first execution only - installs systemd service)
sudo python3 -m pi_netconfig.main
```

### Post-Installation

The service starts automatically after installation. If no WiFi connection is available on startup:

1. The system creates an access point named `PiConfig-XXXX` (password: `piconfig123`)
2. Connect to this access point from another device
3. Access web interface at `http://192.168.50.1:8080`
4. Configure WiFi network through the browser interface

[Return to Table of Contents](<#table of contents>)

## Service Lifecycle Management

### Service Status

Check current service status:

```bash
sudo systemctl status pi-netconfig
```

### Service Control

**Restart service:**

```bash
sudo systemctl restart pi-netconfig
```

**Stop service:**

```bash
sudo systemctl stop pi-netconfig
```

**Start service:**

```bash
sudo systemctl start pi-netconfig
```

**Disable service from auto-start:**

```bash
sudo systemctl disable pi-netconfig
```

**Enable service auto-start:**

```bash
sudo systemctl enable pi-netconfig
```

### Log Viewing

View real-time service logs:

```bash
sudo journalctl -u pi-netconfig -f
```

View recent log entries:

```bash
sudo journalctl -u pi-netconfig -n 100
```

[Return to Table of Contents](<#table of contents>)

## Web Interface Operation

### Accessing the Interface

When the system enters access point mode:

1. Connect to WiFi network `PiConfig-XXXX` (password: `piconfig123`)
2. Open browser and navigate to `http://192.168.50.1:8080`

### Network Configuration

The web interface provides:

- **Network Scanning:** Displays available WiFi networks
- **Network Selection:** Choose target network from scan results
- **Credential Entry:** Enter WiFi password
- **Connection Submission:** Apply configuration and attempt connection

After submitting configuration, the service attempts to connect to the specified network. If successful, the access point shuts down and the system operates in client mode.

[Return to Table of Contents](<#table of contents>)

## Testing Execution

### Development Testing

Run tests in development environment:

```bash
# Activate virtual environment
source venv/bin/activate

# Execute test suite
pytest src/tests/
```

### Deployment Testing

Test on Raspberry Pi after deployment:

```bash
# On Raspberry Pi with virtual environment activated
cd /home/admin/pi-netconfig
source pi-netconfig-venv/bin/activate
pytest src/tests/
```

[Return to Table of Contents](<#table of contents>)

## Architecture Description

### Operational Modes

The system operates as a state machine with three distinct modes:

**CHECKING:**
- Monitors connection status every 30 seconds
- Verifies WiFi connectivity
- Transitions to CLIENT or AP_MODE based on connection state

**CLIENT:**
- Connected to configured WiFi network
- Normal operational mode
- Continues periodic connectivity monitoring

**AP_MODE:**
- Creates access point when no connection available
- Runs web server on port 8080
- Allows network configuration via browser interface
- Transitions to CLIENT mode upon successful configuration

### System Components

**Installer:**
- Self-bootstrapping systemd service setup
- First-run installation of service configuration
- Creates necessary system directories and files

**StateMonitor:**
- Operational state coordination
- Manages state transitions
- Coordinates component activation/deactivation

**ConnectionManager:**
- WiFi client operations
- Network profile management
- Connection establishment and monitoring

**APManager:**
- Access point creation and configuration
- DHCP server management
- Access point lifecycle control

**WebServer:**
- HTML configuration interface on port 8080
- Network scanning endpoint
- Configuration submission handling

**ServiceController:**
- Application lifecycle management
- Component orchestration
- Graceful shutdown handling

[Return to Table of Contents](<#table of contents>)

## Troubleshooting Guidance

### Service Not Starting

**Check service status:**

```bash
sudo systemctl status pi-netconfig
```

**Verify installation:**

```bash
python3 -m pi_netconfig.main --help
```

**Check logs for errors:**

```bash
sudo journalctl -u pi-netconfig -n 50
```

**Common causes:**
- Python version < 3.11
- NetworkManager not installed
- Insufficient privileges
- Configuration file permissions

### Access Point Not Visible

**Verify AP mode activation:**

```bash
sudo journalctl -u pi-netconfig | grep "AP_MODE"
```

**Check NetworkManager status:**

```bash
sudo systemctl status NetworkManager
```

**Verify wireless interface availability:**

```bash
nmcli device status
```

**Common causes:**
- Wireless interface disabled
- NetworkManager not running
- Conflicting network configuration
- Hardware compatibility issues

### Cannot Connect to Web Interface

**Verify service is running:**

```bash
sudo systemctl status pi-netconfig
```

**Check web server logs:**

```bash
sudo journalctl -u pi-netconfig | grep "WebServer"
```

**Verify IP configuration:**

```bash
ip addr show
```

**Common causes:**
- Port 8080 blocked by firewall
- Incorrect IP address (should be 192.168.50.1)
- Web server component failed to start
- Browser cache issues

### WiFi Configuration Not Persisting

**Check configuration file:**

```bash
cat ~/.pi-netconfig/network_config.json
```

**Verify file permissions:**

```bash
ls -la ~/.pi-netconfig/
```

**Check logs for storage errors:**

```bash
sudo journalctl -u pi-netconfig | grep "config"
```

**Common causes:**
- Insufficient disk space
- File permission issues
- Invalid JSON in configuration file
- NetworkManager profile creation failure

[Return to Table of Contents](<#table of contents>)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-29 | Initial user guide creation |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
