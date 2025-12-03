Created: 2025 December 01

# Hardware Deployment Validation Procedure

## Table of Contents

- [Overview](<#overview>)
- [Prerequisites](<#prerequisites>)
- [Phase 1: Package Build and Transfer](<#phase 1 package build and transfer>)
- [Phase 2: Installation and Service Verification](<#phase 2 installation and service verification>)
- [Phase 3: CLIENT Mode Validation](<#phase 3 client mode validation>)
- [Phase 4: AP Mode Validation](<#phase 4 ap mode validation>)
- [Phase 5: Configuration Interface Testing](<#phase 5 configuration interface testing>)
- [Phase 6: State Transition Validation](<#phase 6 state transition validation>)
- [Validation Checklist](<#validation checklist>)
- [Issue Documentation](<#issue documentation>)
- [Success Criteria](<#success criteria>)
- [Version History](<#version history>)

[Return to Table of Contents](<#table of contents>)

## Overview

This procedure validates pi-netconfig v0.2.0 deployment on Raspberry Pi hardware. The validation confirms all design specifications are met under actual NetworkManager operation and verifies resolution of previously documented issues.

**Objective**: Confirm production readiness through systematic hardware testing

**Duration**: Approximately 2-3 hours

**Prerequisites**: Raspberry Pi with NetworkManager, network access, development machine

[Return to Table of Contents](<#table of contents>)

## Prerequisites

### Hardware Requirements

- Raspberry Pi (tested on Pi 3/4/5 running Raspbian Bookworm)
- WiFi adapter (built-in or USB)
- Ethernet cable (for initial access)
- Power supply
- SD card with Raspbian Bookworm installed

### Network Requirements

- WiFi network for CLIENT mode testing (SSID and password required)
- Device for connecting to AP mode (laptop/phone)
- Development machine with SSH access to Pi

### Software Requirements

**On Development Machine:**
- Git repository clone
- Python 3.9+ with build tools
- SSH client

**On Raspberry Pi:**
- Python 3.9+
- NetworkManager installed and running
- Root access

### Verification Commands

```bash
# On Raspberry Pi - verify prerequisites
python3 --version  # Should show 3.9 or higher
systemctl status NetworkManager  # Should show active (running)
nmcli device status  # Should show WiFi interface
```

[Return to Table of Contents](<#table of contents>)

## Phase 1: Package Build and Transfer

### Step 1.1: Build Distribution Package

```bash
# On development machine
cd /path/to/pi-netconfig

# Activate virtual environment
source venv/bin/activate

# Build wheel package
python -m build

# Verify build artifacts
ls -lh dist/
# Expected output:
# pi_netconfig-0.2.0-py3-none-any.whl
# pi_netconfig-0.2.0.tar.gz
```

**Validation Point**: Wheel file exists with correct version number

### Step 1.2: Transfer Package to Pi

```bash
# Replace admin@raspberry-pi with your Pi's credentials
scp dist/pi_netconfig-0.2.0-py3-none-any.whl admin@raspberry-pi:/tmp/

# Verify transfer
ssh admin@raspberry-pi "ls -lh /tmp/pi_netconfig-0.2.0-py3-none-any.whl"
```

**Validation Point**: Package successfully transferred to Pi

### Step 1.3: Document Environment

```bash
# On Raspberry Pi
ssh admin@raspberry-pi

# Document system information
cat /etc/os-release > /tmp/validation-environment.txt
python3 --version >> /tmp/validation-environment.txt
nmcli --version >> /tmp/validation-environment.txt
ip addr show >> /tmp/validation-environment.txt
```

**Expected Output**:
- Raspbian Bookworm or similar
- Python 3.9+
- NetworkManager version
- Network interface list

[Return to Table of Contents](<#table of contents>)

## Phase 2: Installation and Service Verification

### Step 2.1: Install Package

```bash
# On Raspberry Pi (as root)
sudo pip install /tmp/pi_netconfig-0.2.0-py3-none-any.whl

# Verify installation
pip list | grep pi-netconfig
# Expected: pi-netconfig    0.2.0
```

**Validation Point**: Package installed without errors

### Step 2.2: Run Installer

```bash
# Execute main module to trigger installation
sudo python3 -m pi_netconfig.main

# Verify systemd service created
sudo systemctl status pi-netconfig
```

**Expected Output**:
```
● pi-netconfig.service - Pi Network Configuration Service
     Loaded: loaded (/etc/systemd/system/pi-netconfig.service; enabled)
     Active: active (running) since ...
```

**Validation Points**:
- Service file created at `/etc/systemd/system/pi-netconfig.service`
- Service enabled (starts on boot)
- Service active and running

### Step 2.3: Verify Service Startup

```bash
# Monitor service logs
sudo journalctl -u pi-netconfig -f
```

**Expected Log Sequence**:
1. `Starting Pi Network Configuration Service...`
2. `Initializing StateMonitor...`
3. `Starting monitoring loop...`
4. State transition to either CLIENT or AP_MODE

**Validation Point**: Service starts without errors and begins state monitoring

### Step 2.4: Check Initial State

```bash
# View last 50 log lines
sudo journalctl -u pi-netconfig -n 50

# Look for state transitions
sudo journalctl -u pi-netconfig | grep "State:"
```

**Expected**: Service determines initial state (CLIENT if connected, AP_MODE if not)

[Return to Table of Contents](<#table of contents>)

## Phase 3: CLIENT Mode Validation

### Step 3.1: Verify Network Connection

**Prerequisite**: Pi must be connected to WiFi network

```bash
# Check current connections
nmcli connection show --active

# Verify internet connectivity
ping -c 4 8.8.8.8
```

**Validation Point**: Pi has active WiFi connection

### Step 3.2: Monitor CLIENT Mode Operation

```bash
# Watch service logs
sudo journalctl -u pi-netconfig -f
```

**Expected Behavior**:
1. Service performs periodic connection checks
2. Connection tests succeed
3. Failure count remains at 0
4. Service stays in CLIENT state

**Duration**: Observe for 5 minutes

**Validation Points**:
- No unexpected state transitions
- Connection checks execute successfully
- No errors in logs
- Service stable in CLIENT mode

### Step 3.3: Verify No AP Active

```bash
# Check for access point profiles
nmcli connection show | grep PiConfig

# Verify no AP interface
nmcli device status
```

**Expected**: No PiConfig access point visible

[Return to Table of Contents](<#table of contents>)

## Phase 4: AP Mode Validation

### Step 4.1: Force AP Mode Transition

```bash
# Disconnect from WiFi to trigger AP mode
sudo nmcli connection down <current-connection-name>

# Or disable WiFi radio
sudo nmcli radio wifi off
sudo nmcli radio wifi on

# Monitor state transition
sudo journalctl -u pi-netconfig -f
```

**Expected Log Sequence**:
1. Connection check failures
2. `failure_count` incrementing (should reach 3)
3. `Transitioning to AP_MODE`
4. AP profile creation
5. AP activation

**Timing**: Should transition after 3 consecutive failures

### Step 4.2: Verify AP Creation

```bash
# Check access point profile
nmcli connection show | grep PiConfig

# Verify AP interface active
nmcli device status

# Get AP details
nmcli connection show <PiConfig-XXXX>
```

**Expected Output**:
- Connection name: `PiConfig-<MAC>`
- SSID: `PiConfig-<MAC>`
- IP address: 192.168.50.1
- Security: WPA2-PSK
- Password: `piconfig123`

**Validation Points**:
- AP profile created successfully
- Interface activated
- Correct IP address assigned

### Step 4.3: Verify Web Server

```bash
# Check web server listening
sudo netstat -tlnp | grep 8080

# Or using ss
sudo ss -tlnp | grep 8080
```

**Expected Output**:
```
tcp  0  0  192.168.50.1:8080  0.0.0.0:*  LISTEN  <pid>/python3
```

**Validation Point**: Web server bound to 192.168.50.1:8080

[Return to Table of Contents](<#table of contents>)

## Phase 5: Configuration Interface Testing

### Step 5.1: Connect to Access Point

**From test device (laptop/phone):**

1. Scan for WiFi networks
2. Connect to `PiConfig-<MAC>`
3. Enter password: `piconfig123`
4. Verify connection established

**Validation Point**: Successfully connected to AP

### Step 5.2: Access Web Interface

**Open browser on test device:**

```
http://192.168.50.1:8080
```

**Expected**: HTML configuration page displays

**Validation Points**:
- Page loads without errors
- Form fields present:
  - SSID input
  - Password input
  - Scan button
  - Save button

### Step 5.3: Test Network Scanning

**In web interface:**

1. Click "Scan for Networks" button
2. Observe network list populates

**Expected**:
- Available WiFi networks listed
- Signal strengths shown
- Security types indicated

**Validation Point**: Network scan executes and displays results

### Step 5.4: Test Configuration Submission

**In web interface:**

1. Select target WiFi network (or enter SSID manually)
2. Enter WiFi password
3. Click "Save Configuration"
4. Observe response

**Expected Behavior**:
1. Form submits successfully
2. Configuration saved message displays
3. Service begins connection attempt
4. Pi disconnects from AP mode (AP interface deactivates)
5. Pi connects to configured network

**Monitor from Pi console:**
```bash
sudo journalctl -u pi-netconfig -f
```

**Expected Log Sequence**:
1. Configuration received
2. Profile creation
3. Connection attempt
4. State transition from AP_MODE to CLIENT
5. Connection success

**Validation Points**:
- Configuration accepted by service
- Profile created in NetworkManager
- Successful connection to target network
- Automatic return to CLIENT mode

[Return to Table of Contents](<#table of contents>)

## Phase 6: State Transition Validation

### Step 6.1: Test CLIENT → AP Transition

**Scenario**: Simulate connection loss

```bash
# While in CLIENT mode, disconnect network
sudo nmcli connection down <wifi-connection>

# Monitor state transition
sudo journalctl -u pi-netconfig -f
```

**Expected Behavior**:
1. Connection checks begin failing
2. Failure count increments (3 failures required)
3. Service transitions to AP_MODE
4. Access point activates
5. Web server starts

**Validation Points**:
- Transition occurs after 3 failures
- AP activates correctly
- Web interface accessible

### Step 6.2: Test AP → CLIENT Transition

**Scenario**: Configure valid network via web interface

**Expected Behavior**:
1. Configuration submitted through web interface
2. Service creates connection profile
3. Service attempts connection
4. On success: transition to CLIENT mode
5. AP deactivates
6. Web server stops

**Validation Points**:
- Automatic transition to CLIENT
- AP cleanly deactivated
- Service stable in CLIENT mode

### Step 6.3: Test Service Restart Behavior

```bash
# While in CLIENT mode with active connection
sudo systemctl restart pi-netconfig

# Monitor startup
sudo journalctl -u pi-netconfig -f
```

**Expected Behavior**:
1. Service starts
2. Detects existing connection
3. Enters CLIENT mode immediately
4. Continues monitoring

**Validation Point**: Service correctly resumes operational state

### Step 6.4: Test Boot Behavior

```bash
# Reboot Pi while connected to WiFi
sudo reboot

# After reboot, check service
sudo systemctl status pi-netconfig
sudo journalctl -u pi-netconfig -n 50
```

**Expected Behavior**:
1. Service starts automatically on boot
2. Detects WiFi connection
3. Enters CLIENT mode
4. Operates normally

**Validation Points**:
- Service enabled and auto-starts
- Correct state detection
- Normal operation after boot

[Return to Table of Contents](<#table of contents>)

## Validation Checklist

### Installation Phase
- [ ] Package builds successfully
- [ ] Package transfers to Pi
- [ ] Package installs without errors
- [ ] Systemd service created
- [ ] Service enabled and active

### CLIENT Mode
- [ ] Service detects WiFi connection
- [ ] Enters CLIENT state
- [ ] Performs periodic connection checks
- [ ] Remains stable in CLIENT mode
- [ ] No AP interface created
- [ ] No web server active

### AP Mode
- [ ] Transitions to AP after 3 failures
- [ ] AP profile created correctly
- [ ] AP activates with correct SSID
- [ ] AP uses correct IP (192.168.50.1)
- [ ] AP password works (piconfig123)
- [ ] Web server starts on port 8080

### Web Interface
- [ ] HTML page loads correctly
- [ ] Form fields present and functional
- [ ] Network scan works
- [ ] Configuration submission succeeds
- [ ] Error handling appropriate

### State Transitions
- [ ] CLIENT → AP transition works
- [ ] AP → CLIENT transition works
- [ ] Service restart maintains state
- [ ] Boot behavior correct

### Integration
- [ ] NetworkManager commands execute
- [ ] Connection profiles persist
- [ ] No permission errors
- [ ] Logs clear and informative
- [ ] No crashes or exceptions

[Return to Table of Contents](<#table of contents>)

## Issue Documentation

### Recording Issues

If validation failures occur, document using T03 Issue template:

**Required Information**:
- Issue title and description
- Steps to reproduce
- Expected vs actual behavior
- Log excerpts
- System environment details

**Create Issue Document**:
```bash
# In workspace/issue/
cp ../governance/templates/t03_issue_template.md issue-NNNN-description.md
```

### Log Collection

```bash
# Capture complete service logs
sudo journalctl -u pi-netconfig > /tmp/pi-netconfig-validation.log

# Transfer to development machine for analysis
scp admin@raspberry-pi:/tmp/pi-netconfig-validation.log ./workspace/test/result/
```

### NetworkManager State

```bash
# Capture NetworkManager state
nmcli connection show > /tmp/nm-connections.txt
nmcli device status > /tmp/nm-devices.txt

# Transfer for analysis
scp admin@raspberry-pi:/tmp/nm-*.txt ./workspace/test/result/
```

[Return to Table of Contents](<#table of contents>)

## Success Criteria

### Deployment Success

**All criteria must be met**:

1. **Installation**: Package installs cleanly, service starts automatically
2. **CLIENT Mode**: Stable operation with active WiFi connection
3. **AP Mode**: Correct activation on connection failure
4. **Web Interface**: Accessible and functional
5. **Configuration**: Successfully configures WiFi credentials
6. **State Transitions**: All transitions execute correctly
7. **Persistence**: Service survives reboot and maintains configuration
8. **Integration**: NetworkManager operations execute without errors

### Performance Expectations

- Connection check interval: ~30 seconds
- AP activation: < 10 seconds after 3rd failure
- Web page load: < 2 seconds
- Configuration save: < 5 seconds
- State transition: < 15 seconds

### Documentation Deliverables

Upon successful validation:

1. **Test Results**: Document in `workspace/test/result/`
2. **Issue Resolution**: Close any resolved issues
3. **Deployment Notes**: Update deployment guide with findings
4. **Version Tag**: Create git tag for validated release

[Return to Table of Contents](<#table of contents>)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-01 | Initial hardware validation procedure for v0.2.0 |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
