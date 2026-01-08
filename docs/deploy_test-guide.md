Created: 2025 December 03

# Pi-Netconfig Deploy & Test Guide

## Table of Contents

- [1. Quick Start](<#1 quick start>)
- [2. Build and Deploy](<#2 build and deploy>)
- [3. Service Operations](<#3 service operations>)
- [4. Uninstallation](<#4 uninstallation>)
- [5. Testing](<#5 testing>)
- [6. Troubleshooting](<#6 troubleshooting>)
- [7. Version History](<#7 version history>)

[Return to Table of Contents](<#table of contents>)

## 1. Quick Start

### 1.1. Prerequisites Check

**On development Mac:**
```bash
# Verify you're in project root
pwd  # Should show: /Users/williamwatson/Documents/GitHub/pi-netconfig

# Verify build tools available
python3 --version  # Should be 3.9+
python3 -m pip show build  # Should show package info
```

**On Raspberry Pi:**
```bash
# Verify NetworkManager running
sudo systemctl status NetworkManager

# Verify Python version
python3 --version  # Should be 3.9+

# Verify wireless interface exists
nmcli device status | grep wifi
```

### 1.2. Build Package

**Working directory: Project root on Mac**
```bash
cd /Users/williamwatson/Documents/GitHub/pi-netconfig

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build distribution
python3 -m build

# Verify output
ls -lh dist/  # Should show: pi_netconfig-1.0.0-py3-none-any.whl
```

### 1.3. Deploy to Pi

**Working directory: Project root on Mac**
```bash
# Transfer package
scp dist/pi_netconfig-*.whl admin@deb1:/tmp/

# Connect to Pi
ssh admin@deb1
```

**Working directory: Any directory on Pi**
```bash
# Create installation directory
sudo mkdir -p /opt/pi-netconfig
cd /opt/pi-netconfig

# Create virtual environment
sudo python3 -m venv venv

# Install package into venv
sudo python3 -m venv venv

# Configure and start service
sudo ./venv/bin/python -m pi_netconfig.installer --install --systemd-mode
sudo systemctl enable pi-netconfig
sudo systemctl start pi-netconfig
```

### 1.4. Verify Installation

```bash
# Check service status
sudo systemctl status pi-netconfig

# Monitor logs
sudo journalctl -u pi-netconfig -f
```

If no WiFi available, service creates AP `PiConfig-XXXX` (password: `piconfig123`). Access web interface at `http://192.168.50.1:8080`.

[Return to Table of Contents](<#table of contents>)

## 2. Build and Deploy

### 2.1. Prerequisites

**Development machine:**
- Python 3.9+
- Build tools: `pip install build`
- Git repository clone
- Working directory: Project root (`/Users/williamwatson/Documents/GitHub/pi-netconfig`)

**Raspberry Pi:**
- Debian-based OS (tested on Debian 12)
- NetworkManager running and enabled
- Python 3.9+
- Wireless interface available
- Root/sudo access
- Sufficient disk space (100MB minimum)

### 2.2. Build Distribution

**Working directory: Project root on Mac**
```bash
# Navigate to project root
cd /Users/williamwatson/Documents/GitHub/pi-netconfig

# Verify location
pwd  # Should output: /Users/williamwatson/Documents/GitHub/pi-netconfig

# Install build tools (one-time)
pip install build

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build wheel
python3 -m build

# Verify output
ls -lh dist/  # Should show: pi_netconfig-1.0.0-py3-none-any.whl
```

### 2.3. Transfer to Pi

**Working directory: Project root on Mac**
```bash
# Transfer package (adjust hostname as needed)
scp dist/pi_netconfig-*.whl admin@deb1:/tmp/

# Verify transfer
ssh admin@deb1 'ls -lh /tmp/pi_netconfig-*.whl'
```

### 2.4. Install on Pi

**Working directory: Any directory on Pi**
```bash
# Connect to Pi
ssh admin@deb1

# Create installation directory
sudo mkdir -p /opt/pi-netconfig
cd /opt/pi-netconfig

# Create virtual environment
sudo python3 -m venv venv

# Verify venv creation
ls -la venv/  # Should show bin/, lib/, etc.

# Install package into venv
sudo ./venv/bin/pip install /tmp/pi_netconfig-*.whl

# Verify installation
./venv/bin/python -c "import pi_netconfig"

# Run installer (creates systemd service)
sudo ./venv/bin/python -m pi_netconfig.installer --install --systemd-mode

# Enable and start service
sudo systemctl enable pi-netconfig
sudo systemctl start pi-netconfig
```

**Verify installation:**
```bash
# Check service status
sudo systemctl status pi-netconfig

# Check service file created
ls -l /etc/systemd/system/pi-netconfig.service

# Monitor initial logs
sudo journalctl -u pi-netconfig -n 50
```

Service starts automatically. Successful installation shows:
- `Active: active (running)` in status
- State detection (CLIENT or AP_MODE) in logs
- No error messages in journalctl output

### 2.5. Update Deployment

**Working directory: Project root on Mac**
```bash
# Build new version
cd /Users/williamwatson/Documents/GitHub/pi-netconfig
rm -rf dist/ build/ *.egg-info/
python3 -m build

# Transfer to Pi
scp dist/pi_netconfig-*.whl admin@deb1:/tmp/
```

**Working directory: Any directory on Pi**
```bash
# Connect to Pi
ssh admin@deb1

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

## 3. Service Operations

### 3.1. Control Commands

```bash
# Status
sudo systemctl status pi-netconfig

# Start/stop/restart
sudo systemctl start pi-netconfig
sudo systemctl stop pi-netconfig
sudo systemctl restart pi-netconfig

# Enable/disable auto-start
sudo systemctl enable pi-netconfig
sudo systemctl disable pi-netconfig
```

### 3.2. Log Access

**Real-time monitoring:**
```bash
sudo journalctl -u pi-netconfig -f
```

**Recent entries:**
```bash
sudo journalctl -u pi-netconfig -n 100
```

**Time-based:**
```bash
sudo journalctl -u pi-netconfig --since "1 hour ago"
sudo journalctl -u pi-netconfig --since "2025-12-03 10:00"
```

**Stream to Mac:**
```bash
# Direct streaming (persistent connection)
ssh pi@raspberry-pi 'sudo journalctl -u pi-netconfig -f' > ~/pi-logs/stream.log

# Stream and view simultaneously
ssh pi@raspberry-pi 'sudo journalctl -u pi-netconfig -f' | tee ~/pi-logs/stream.log
```

**Collect logs:**
```bash
# On Pi
ssh pi@raspberry-pi 'sudo journalctl -u pi-netconfig --no-pager' > pi-netconfig.log

# Transfer to Mac
scp pi@raspberry-pi:~/pi-netconfig.log ./
```

### 3.3. Configuration Locations

- Service file: `/etc/systemd/system/pi-netconfig.service`
- WiFi profiles: `/etc/NetworkManager/system-connections/`
- User config: `~/.pi-netconfig/network_config.json`

[Return to Table of Contents](<#table of contents>)

## 4. Uninstallation

### 4.1. Prerequisites Check

**Working directory: Any directory on Pi**
```bash
# Verify installation exists
sudo systemctl status pi-netconfig  # Check if service exists
ls -la /opt/pi-netconfig/  # Check if venv exists
```

### 4.2. Virtual Environment Removal (Recommended)

**Working directory: Any directory on Pi**
```bash
# Stop and disable service
sudo systemctl stop pi-netconfig
sudo systemctl disable pi-netconfig

# Remove systemd service file
sudo rm -f /etc/systemd/system/pi-netconfig.service
sudo systemctl daemon-reload

# Uninstall from venv (optional - removes only package)
sudo /opt/pi-netconfig/venv/bin/pip uninstall -y pi-netconfig

# Remove entire venv directory (recommended - removes everything)
sudo rm -rf /opt/pi-netconfig

# Remove NetworkManager profiles (optional)
sudo rm -f /etc/NetworkManager/system-connections/PiConfig-*

# Remove user configuration (optional)
rm -rf ~/.pi-netconfig
```

### 4.3. System-Wide Removal (Not Recommended)

**Note:** Only use if package was installed system-wide. This violates Debian PEP 668 policy.

**Working directory: Any directory on Pi**
```bash
# Stop and disable service
sudo systemctl stop pi-netconfig
sudo systemctl disable pi-netconfig

# Remove systemd service file
sudo rm -f /etc/systemd/system/pi-netconfig.service
sudo systemctl daemon-reload

# Uninstall package (requires --break-system-packages on Debian 12+)
sudo pip uninstall -y pi-netconfig

# Remove NetworkManager profiles (optional)
sudo rm -f /etc/NetworkManager/system-connections/PiConfig-*

# Remove user configuration (optional)
rm -rf ~/.pi-netconfig
```

### 4.4. Verification

**Working directory: Any directory on Pi**
```bash
# Confirm service removed
sudo systemctl status pi-netconfig  # Should show "Unit pi-netconfig.service could not be found"

# Confirm service file removed
ls /etc/systemd/system/pi-netconfig.service  # Should show "No such file or directory"

# Confirm venv removed
ls /opt/pi-netconfig/  # Should show "No such file or directory"

# Confirm package removed from venv (if only package uninstalled)
/opt/pi-netconfig/venv/bin/pip list | grep pi-netconfig  # Should show nothing

# Confirm package not importable
python3 -c "import pi_netconfig"  # Should fail with ModuleNotFoundError

# Confirm NetworkManager profiles cleaned
nmcli connection show | grep PiConfig  # Should show nothing

# Confirm user config removed
ls ~/.pi-netconfig/  # Should show "No such file or directory"
```

[Return to Table of Contents](<#table of contents>)

## 5. Testing

### 5.1. Development Tests (Mac)

**Working directory: Project root on Mac**
```bash
# Navigate to project root
cd /Users/williamwatson/Documents/GitHub/pi-netconfig

# Verify location
pwd  # Should output: /Users/williamwatson/Documents/GitHub/pi-netconfig
```

**Setup (one-time):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
deactivate
```

**Run tests (activate venv each new terminal session):**
```bash
source venv/bin/activate

# Run tests
pytest src/tests/

# With coverage
pytest src/tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Deactivate when done
deactivate
```

### 5.2. Hardware Validation (Pi)

**Prerequisites: Package deployed per [Build and Deploy](<#build and deploy>)**

**Working directory: Any directory on Pi**

**After deployment, verify core functionality:**

```bash
# Check service startup
sudo systemctl status pi-netconfig
sudo journalctl -u pi-netconfig -n 50

# Verify state (should show CLIENT or AP_MODE)
sudo journalctl -u pi-netconfig | grep "State:"
```

**CLIENT mode validation:**

WiFi must be connected.

```bash
# Check active connection
nmcli connection show --active

# Monitor for 5 minutes - should remain stable
sudo journalctl -u pi-netconfig -f
```

Expected: Connection checks succeed, no state transitions.

**AP mode validation:**

Force AP mode by disabling WiFi.

```bash
# Disconnect WiFi
sudo nmcli radio wifi off
sudo nmcli radio wifi on

# Monitor state transition
sudo journalctl -u pi-netconfig -f
```

Expected log sequence:
1. Connection check failures (3 consecutive)
2. `Transitioning to AP_MODE`
3. AP profile creation
4. Web server starts

Verify AP:
```bash
nmcli connection show | grep PiConfig
nmcli device status
sudo netstat -tlnp | grep 8080
```

Expected: AP active, web server listening on 192.168.50.1:8080

**Web interface validation:**

From test device:
1. Connect to `PiConfig-XXXX` (password: `piconfig123`)
2. Browse to `http://192.168.50.1:8080`
3. Click "Scan for Networks" - networks should populate
4. Select network, enter password, submit
5. Monitor Pi logs for connection attempt and CLIENT transition

**State transition validation:**

Test CLIENT → AP:
```bash
# While in CLIENT, disconnect
sudo nmcli connection down <wifi-connection>
sudo journalctl -u pi-netconfig -f
```

Expected: 3 failures, transition to AP_MODE

Test AP → CLIENT:
- Configure valid network via web interface
- Monitor transition to CLIENT mode
- Verify AP deactivates

**Service restart:**
```bash
sudo systemctl restart pi-netconfig
sudo journalctl -u pi-netconfig -f
```

Expected: Service detects current network state, continues operation

**Boot persistence:**
```bash
sudo reboot
# After reboot
sudo systemctl status pi-netconfig
```

Expected: Service starts automatically, correct state detection

### 5.3. Validation Checklist

**Installation:**
- [ ] Package installs without errors
- [ ] Systemd service created and enabled
- [ ] Service active and running

**CLIENT Mode:**
- [ ] Detects WiFi connection
- [ ] Connection checks succeed
- [ ] Stable operation (5+ minutes)
- [ ] No unexpected transitions

**AP Mode:**
- [ ] Transitions after 3 failures
- [ ] AP created with correct SSID
- [ ] Web server accessible (192.168.50.1:8080)
- [ ] Password authentication works

**Web Interface:**
- [ ] Page loads
- [ ] Network scan functions
- [ ] Configuration submission succeeds
- [ ] State transition to CLIENT

**Transitions:**
- [ ] CLIENT → AP works
- [ ] AP → CLIENT works
- [ ] Service restart maintains state
- [ ] Boot auto-start functions

[Return to Table of Contents](<#table of contents>)

## 6. Troubleshooting

### 6.1. Service Won't Start

**Check status:**
```bash
sudo systemctl status pi-netconfig
sudo journalctl -u pi-netconfig -n 50
```

**Common causes:**
- NetworkManager not running: `sudo systemctl start NetworkManager`
- Python < 3.9: `python3 --version`
- Package not installed: `pip list | grep pi-netconfig`
- Permission errors: Must run as root

### 6.2. Access Point Not Visible

**Verify AP activation:**
```bash
sudo journalctl -u pi-netconfig | grep "AP_MODE"
nmcli device status
nmcli connection show | grep PiConfig
```

**Common causes:**
- Service in CLIENT mode (WiFi connected)
- Wireless interface disabled: `nmcli radio wifi on`
- NetworkManager stopped: `sudo systemctl start NetworkManager`
- Insufficient failures (requires 3 consecutive)

### 6.3. Web Interface Unreachable

**Check web server:**
```bash
sudo journalctl -u pi-netconfig | grep "WebServer"
sudo netstat -tlnp | grep 8080
ip addr show
```

**Common causes:**
- Service not in AP_MODE
- Firewall blocking port 8080: `sudo ufw allow 8080/tcp`
- Wrong IP (should be 192.168.50.1)
- Not connected to PiConfig AP

### 6.4. Connection Fails After Configuration

**Check logs:**
```bash
sudo journalctl -u pi-netconfig | grep -A 20 "Configuration received"
```

**Verify profile:**
```bash
nmcli connection show
sudo cat /etc/NetworkManager/system-connections/<profile>
```

**Common causes:**
- Incorrect password
- Hidden SSID not specified correctly
- WPA3-only network (try WPA2)
- Signal too weak

### 6.5. Import Errors After Install

**Verify installation:**
```bash
pip list | grep pi-netconfig
python3 -c "import pi_netconfig; print(pi_netconfig.__version__)"
```

**Reinstall if needed:**
```bash
sudo pip install --force-reinstall /tmp/pi_netconfig-1.0.0-py3-none-any.whl
```

### 6.6. Log Analysis Patterns

**Find errors:**
```bash
sudo journalctl -u pi-netconfig | grep -i "error\|exception\|traceback"
```

**Connection attempts:**
```bash
sudo journalctl -u pi-netconfig | grep "connect"
```

**State changes:**
```bash
sudo journalctl -u pi-netconfig | grep "State:"
```

**NetworkManager operations:**
```bash
sudo journalctl -u pi-netconfig | grep "nmcli"
```

[Return to Table of Contents](<#table of contents>)

## 7. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.3 | 2025-12-04 | Added section numbering |
| 1.2 | 2025-12-03 | Added explicit working directory context and prerequisite checks throughout |
| 1.1 | 2025-12-03 | Added uninstallation procedures |
| 1.0 | 2025-12-03 | Consolidated deployment and testing guide |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
