Created: 2025 November 29

# Pi Network Configuration Tool - User Guide

## Table of Contents

- [1. Introduction](<#1 introduction>)
- [2. Requirements](<#2 requirements>)
- [3. Deployment](<#3 deployment>)
  - [3.1. Installing from Release Package](<#3.1 installing from release package>)
  - [3.2. Post-Installation](<#3.2 post-installation>)
  - [3.3. Updating an Existing Installation](<#3.3 updating an existing installation>)
  - [3.4. Uninstallation](<#3.4 uninstallation>)
- [4. Service Lifecycle Management](<#4 service lifecycle management>)
  - [4.1. Service Status](<#4.1 service status>)
  - [4.2. Service Control](<#4.2 service control>)
  - [4.3. Log Viewing](<#4.3 log viewing>)
- [5. Web Interface Operation](<#5 web interface operation>)
  - [5.1. Accessing the Interface](<#5.1 accessing the interface>)
  - [5.2. Network Configuration](<#5.2 network configuration>)
- [6. Troubleshooting](<#6 troubleshooting>)
  - [6.1. Service Not Starting](<#6.1 service not starting>)
  - [6.2. Access Point Not Visible](<#6.2 access point not visible>)
  - [6.3. Cannot Connect to Web Interface](<#6.3 cannot connect to web interface>)
  - [6.4. WiFi Configuration Not Persisting](<#6.4 wifi configuration not persisting>)
  - [6.5. Connection Fails After Configuration](<#6.5 connection fails after configuration>)
  - [6.6. Import Errors After Installation](<#6.6 import errors after installation>)
- [7. Version History](<#7 version history>)

## 1. Introduction

Pi Network Configuration Tool provides WiFi configuration management for Raspberry Pi and Debian-based systems with automatic fallback to access point mode when no connection is available. The tool operates as a systemd service, continuously monitoring network connectivity and providing a web-based configuration interface when needed.

**Key Features:**

- Self-installing systemd service (runs on first execution)
- Automatic WiFi connectivity monitoring
- Access point mode with web interface (192.168.50.1:8080) when no connection available
- Network scanning and configuration through browser
- Single network profile persistence
- State-based operation (CHECKING → CLIENT ↔ AP_MODE)

The tool is designed for headless Raspberry Pi deployments where physical display and keyboard access is not available, enabling WiFi configuration through the web interface without requiring direct system access.

[Return to Table of Contents](<#table of contents>)

## 2. Requirements

- Raspberry Pi running Debian-based Linux (validated on Debian 13 Trixie)
- NetworkManager (standard in modern Raspbian)
- Python 3.9 or higher
- Root privileges for installation and network operations

[Return to Table of Contents](<#table of contents>)

## 3. Deployment

### 3.1. Installing from Release Package

**Transfer wheel file to target system:**

```bash
scp pi_netconfig-1.0.0-py3-none-any.whl admin@solax-modbus.local:/tmp/
```

**Install on Raspberry Pi:**

```bash
# Connect to Raspberry Pi
ssh admin@solax-modbus.local

# Create installation directory
sudo mkdir -p /opt/pi-netconfig
cd /opt/pi-netconfig

# Create virtual environment
sudo python3 -m venv venv

# Install package into venv
sudo ./venv/bin/pip install /tmp/pi_netconfig-1.0.0-py3-none-any.whl

# Verify installation
./venv/bin/python -c "import pi_netconfig"

# Run installer (creates systemd service)
sudo ./venv/bin/python -m pi_netconfig.installer --install --systemd-mode

# Enable and start service
sudo systemctl enable pi-netconfig
sudo systemctl start pi-netconfig
```

[Return to Table of Contents](<#table of contents>)

### 3.2. Post-Installation

The service starts automatically after installation. If no WiFi connection is available on startup:

1. The system creates an access point named `PiConfig-XXXX` (password: `piconfig123`)
2. Connect to this access point from another device
3. Access web interface at `http://192.168.50.1:8080`
4. Configure WiFi network through the browser interface

**Verify installation:**

```bash
# Check service status
sudo systemctl status pi-netconfig

# Check service file created
ls -l /etc/systemd/system/pi-netconfig.service

# Monitor initial logs
sudo journalctl -u pi-netconfig -n 50
```

Successful installation shows `Active: active (running)` in status, state detection (CLIENT or AP_MODE) in logs, and no error messages in journalctl output.

[Return to Table of Contents](<#table of contents>)

### 3.3. Updating an Existing Installation

```bash
# Connect to Pi
ssh admin@solax-modbus.local

# Stop service
sudo systemctl stop pi-netconfig

# Upgrade package in venv
sudo /opt/pi-netconfig/venv/bin/pip install --upgrade /tmp/pi_netconfig-*.whl

# Start service
sudo systemctl start pi-netconfig

# Verify upgrade
sudo journalctl -u pi-netconfig -n 50
```

[Return to Table of Contents](<#table of contents>)

### 3.4. Uninstallation

**Virtual environment removal (recommended):**

```bash
# Stop and disable service
sudo systemctl stop pi-netconfig
sudo systemctl disable pi-netconfig

# Remove systemd service file
sudo rm -f /etc/systemd/system/pi-netconfig.service
sudo systemctl daemon-reload

# Remove entire venv directory
sudo rm -rf /opt/pi-netconfig

# Remove NetworkManager profiles (optional)
sudo rm -f /etc/NetworkManager/system-connections/PiConfig-*

# Remove user configuration (optional)
rm -rf ~/.pi-netconfig
```

**Verification:**

```bash
# Confirm service removed
sudo systemctl status pi-netconfig  # Should show "Unit pi-netconfig.service could not be found"

# Confirm venv removed
ls /opt/pi-netconfig/  # Should show "No such file or directory"

# Confirm NetworkManager profiles cleaned
nmcli connection show | grep PiConfig  # Should show nothing
```

[Return to Table of Contents](<#table of contents>)

## 4. Service Lifecycle Management

### 4.1. Service Status

```bash
sudo systemctl status pi-netconfig
```

### 4.2. Service Control

```bash
# Restart
sudo systemctl restart pi-netconfig

# Stop
sudo systemctl stop pi-netconfig

# Start
sudo systemctl start pi-netconfig

# Disable auto-start
sudo systemctl disable pi-netconfig

# Enable auto-start
sudo systemctl enable pi-netconfig
```

[Return to Table of Contents](<#table of contents>)

### 4.3. Log Viewing

```bash
# Real-time
sudo journalctl -u pi-netconfig -f

# Recent entries
sudo journalctl -u pi-netconfig -n 100

# Time-based
sudo journalctl -u pi-netconfig --since "1 hour ago"
```

[Return to Table of Contents](<#table of contents>)

## 5. Web Interface Operation

### 5.1. Accessing the Interface

When the system enters access point mode:

1. Connect to WiFi network `PiConfig-XXXX` (password: `piconfig123`)
2. Open browser and navigate to `http://192.168.50.1:8080`

[Return to Table of Contents](<#table of contents>)

### 5.2. Network Configuration

The web interface provides:

- **Network Scanning:** Displays available WiFi networks
- **Network Selection:** Choose target network from scan results
- **Credential Entry:** Enter WiFi password
- **Connection Submission:** Apply configuration and attempt connection

After submitting configuration, the service attempts to connect to the specified network. If successful, the access point shuts down and the system operates in client mode.

[Return to Table of Contents](<#table of contents>)

## 6. Troubleshooting

### 6.1. Service Not Starting

```bash
sudo systemctl status pi-netconfig
sudo journalctl -u pi-netconfig -n 50
```

**Common causes:**
- NetworkManager not running: `sudo systemctl start NetworkManager`
- Python version < 3.9
- Package not installed
- Insufficient privileges (must run as root)

[Return to Table of Contents](<#table of contents>)

### 6.2. Access Point Not Visible

```bash
sudo journalctl -u pi-netconfig | grep "AP_MODE"
nmcli device status
nmcli connection show | grep PiConfig
```

**Common causes:**
- Service in CLIENT mode (WiFi already connected)
- Wireless interface disabled: `nmcli radio wifi on`
- NetworkManager not running
- Insufficient failures recorded (requires 3 consecutive)

[Return to Table of Contents](<#table of contents>)

### 6.3. Cannot Connect to Web Interface

```bash
sudo journalctl -u pi-netconfig | grep "WebServer"
sudo netstat -tlnp | grep 8080
ip addr show
```

**Common causes:**
- Service not in AP_MODE
- Port 8080 blocked by firewall
- Incorrect IP address (should be 192.168.50.1)
- Not connected to the PiConfig access point

[Return to Table of Contents](<#table of contents>)

### 6.4. WiFi Configuration Not Persisting

```bash
cat ~/.pi-netconfig/network_config.json
ls -la ~/.pi-netconfig/
sudo journalctl -u pi-netconfig | grep "config"
```

**Common causes:**
- Insufficient disk space
- File permission issues
- Invalid JSON in configuration file
- NetworkManager profile creation failure

[Return to Table of Contents](<#table of contents>)

### 6.5. Connection Fails After Configuration

```bash
sudo journalctl -u pi-netconfig | grep -A 20 "Configuration received"
nmcli connection show
```

**Common causes:**
- Incorrect password
- Hidden SSID not specified correctly
- WPA3-only network (try WPA2)
- Signal too weak

[Return to Table of Contents](<#table of contents>)

### 6.6. Import Errors After Installation

```bash
/opt/pi-netconfig/venv/bin/pip list | grep pi-netconfig
/opt/pi-netconfig/venv/bin/python -c "import pi_netconfig; print(pi_netconfig.__version__)"
```

**Reinstall if needed:**

```bash
sudo /opt/pi-netconfig/venv/bin/pip install --force-reinstall /tmp/pi_netconfig-1.0.0-py3-none-any.whl
```

[Return to Table of Contents](<#table of contents>)

## 7. Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-07-01 | Restructured as user-facing only: removed development environment, testing, and architecture sections (relocated to docs/development.md); merged deployment, uninstallation, and troubleshooting content from docs/deploy_test-guide.md (deleted); reconciled duplicate service control and troubleshooting entries; corrected OS reference to Debian 13 Trixie |
| 1.1 | 2025-12-04 | Added section numbering |
| 1.0 | 2025-11-29 | Initial user guide creation |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
