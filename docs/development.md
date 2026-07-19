Created: 2026 July 01

# Pi Network Configuration Tool - Development Guide

## Table of Contents

- [1. Introduction](<#1 introduction>)
- [2. Development Environment Setup](<#2 development environment setup>)
  - [2.1. Initial Setup](<#2.1 initial setup>)
  - [2.2. Running Unit Tests](<#2.2 running unit tests>)
- [3. Building from Source](<#3 building from source>)
  - [3.1. Creating Distribution Package](<#3.1 creating distribution package>)
  - [3.2. Publishing a Release](<#3.2 publishing a release>)
- [4. Hardware Deployment Testing](<#4 hardware deployment testing>)
  - [4.1. Deploying to Test Hardware](<#4.1 deploying to test hardware>)
  - [4.2. Validation Checklist](<#4.2 validation checklist>)
  - [4.3. AP Mode Testing Reference](<#4.3 ap mode testing reference>)
- [5. Architecture Description](<#5 architecture description>)
  - [5.1. Operational Modes](<#5.1 operational modes>)
  - [5.2. System Components](<#5.2 system components>)
- [6. Governance Framework](<#6 governance framework>)
- [7. Version History](<#7 version history>)

## 1. Introduction

This document covers development environment setup, build procedures, hardware validation testing, and architecture reference for pi-netconfig. For installation and operation of a released package, see the [User Guide](user-guide.md).

[Return to Table of Contents](<#table of contents>)

## 2. Development Environment Setup

### 2.1. Initial Setup

```bash
cd /path/to/pi-netconfig
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

The editable installation (`-e` flag) allows imports to work during development without reinstalling after code changes.

[Return to Table of Contents](<#table of contents>)

### 2.2. Running Unit Tests

```bash
# With virtual environment activated
pytest src/tests/

# With coverage
pytest src/tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

[Return to Table of Contents](<#table of contents>)

## 3. Building from Source

### 3.1. Creating Distribution Package

```bash
cd /path/to/pi-netconfig
./bin/build.sh
```

`bin/build.sh` reads the version from `pyproject.toml`, cleans prior build artifacts, stamps `src/pi_netconfig/__init__.py`, and builds the wheel at `dist/pi_netconfig-<version>-py3-none-any.whl`.

[Return to Table of Contents](<#table of contents>)

### 3.2. Publishing a Release

Requires `gh` CLI, authenticated (`gh auth login`).

```bash
./bin/release.sh
```

`bin/release.sh` builds the wheel via `bin/build.sh`, then publishes a GitHub release tagged `v<version>` with two assets: the wheel and `bin/install.sh`. `bin/install.sh` is the script referenced in the root [README](<../README.md#4.1 install via script>) — it fetches the release, performs first-time install or upgrade, and registers the systemd service.

[Return to Table of Contents](<#table of contents>)

## 4. Hardware Deployment Testing

### 4.1. Deploying to Test Hardware

Prerequisite: package deployed per [User Guide §3.1](<user-guide.md#3.1 installing from release package>).

```bash
# Check service startup
sudo systemctl status pi-netconfig
sudo journalctl -u pi-netconfig -n 50

# Verify state (should show CLIENT or AP_MODE)
sudo journalctl -u pi-netconfig | grep "State:"
```

**CLIENT mode validation** (WiFi connected):

```bash
nmcli connection show --active

# Monitor for 5 minutes - should remain stable
sudo journalctl -u pi-netconfig -f
```

Expected: connection checks succeed, no state transitions.

**AP mode validation** (force by disabling WiFi):

```bash
sudo nmcli radio wifi off
sudo nmcli radio wifi on

sudo journalctl -u pi-netconfig -f
```

Expected log sequence: 3 consecutive connection check failures, `Transitioning to AP_MODE`, AP profile creation, web server start.

```bash
nmcli connection show | grep PiConfig
nmcli device status
sudo netstat -tlnp | grep 8080
```

**Web interface validation:**

1. Connect to `PiConfig-XXXX` (password: `piconfig123`)
2. Browse to `http://192.168.50.1:8080`
3. Click "Scan for Networks" — networks should populate
4. Select network, enter password, submit
5. Monitor Pi logs for connection attempt and CLIENT transition

**State transition validation:**

```bash
# CLIENT -> AP
sudo nmcli connection down <wifi-connection>
sudo journalctl -u pi-netconfig -f
```

Expected: 3 failures, transition to AP_MODE. AP → CLIENT is validated by configuring a valid network via the web interface and confirming AP deactivation.

**Service restart and boot persistence:**

```bash
sudo systemctl restart pi-netconfig
sudo journalctl -u pi-netconfig -f

sudo reboot
# After reboot
sudo systemctl status pi-netconfig
```

Expected: service detects current network state and continues operation without manual intervention.

[Return to Table of Contents](<#table of contents>)

### 4.2. Validation Checklist

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

### 4.3. AP Mode Testing Reference

Command-level reference for forcing and verifying AP mode transitions, web server endpoints, and log patterns: [ap-mode-test-commands.md](ap-mode-test-commands.md).

[Return to Table of Contents](<#table of contents>)

## 5. Architecture Description

### 5.1. Operational Modes

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

[Return to Table of Contents](<#table of contents>)

### 5.2. System Components

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

## 6. Governance Framework

Design, change management, issue tracking, and AI-assisted development process are governed by the framework in `ai/`. See [ai/governance.md](../ai/governance.md) for protocol reference and [ai/primer.md](../ai/primer.md) for a condensed operational summary.

[Return to Table of Contents](<#table of contents>)

## 7. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-07-01 | Replaced manual build steps with bin/build.sh; added §3.2 Publishing a Release documenting bin/release.sh and its relationship to bin/install.sh |
| 1.0 | 2026-07-01 | Initial development guide; consolidated from docs/user-guide.md (development environment, testing, architecture sections) and docs/deploy_test-guide.md (build, hardware validation testing) as part of user/developer documentation split |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
