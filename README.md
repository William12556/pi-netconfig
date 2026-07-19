# Pi Network Configuration Tool

WiFi configuration management for Raspberry Pi/Debian systems with automatic access point fallback.

## Table of Contents

- [1. Overview](<#1 overview>)
- [2. Features](<#2 features>)
- [3. Requirements](<#3 requirements>)
- [4. Quick Start](<#4 quick start>)
  - [4.1. Install via Script](<#4.1 install via script>)
  - [4.2. Manual Installation](<#4.2 manual installation>)
  - [4.3. Configure WiFi](<#4.3 configure wifi>)
- [5. Documentation](<#5 documentation>)
- [6. License](<#6 license>)
- [Version History](<#version history>)

## 1. Overview

Tool manages WiFi connectivity with automatic fallback to access point mode when no connection is available. Designed for headless Raspberry Pi systems without attached displays or keyboards. The system operates as a self-installing systemd service, providing continuous network monitoring and a web-based configuration interface when needed.

[Return to Table of Contents](<#table of contents>)

## 2. Features

- Self-installing systemd service (runs on first execution)
- Automatic WiFi connectivity monitoring
- Access point mode with web interface (192.168.50.1:8080) when no connection available
- Network scanning and configuration through browser
- Single network profile persistence
- State-based operation (CHECKING → CLIENT ↔ AP_MODE)

[Return to Table of Contents](<#table of contents>)

## 3. Requirements

- Raspberry Pi running Debian-based Linux (validated on Debian 13 Trixie)
- NetworkManager (standard in modern Raspbian)
- Python 3.9 or higher
- Root privileges for installation and network operations

[Return to Table of Contents](<#table of contents>)

## 4. Quick Start

### 4.1. Install via Script

Run on the Raspberry Pi. Fetches the latest release, creates the virtual environment, and registers the systemd service:

```bash
curl -fsSL https://github.com/William12556/pi-netconfig/releases/latest/download/install.sh -o install.sh
chmod +x install.sh && ./install.sh
```

Re-running the same command on an existing installation performs an upgrade.

### 4.2. Manual Installation

Alternative for offline installs or a specific local wheel file.

```bash
# Transfer package
scp pi_netconfig-1.0.0-py3-none-any.whl admin@raspberry-pi:/tmp/

# Install on Raspberry Pi
ssh admin@raspberry-pi

# Create virtual environment
sudo mkdir -p /opt/pi-netconfig
cd /opt/pi-netconfig
sudo python3 -m venv venv
sudo ./venv/bin/pip install /tmp/pi_netconfig-1.0.0-py3-none-any.whl

# Run installer (creates and starts systemd service)
sudo ./venv/bin/python -m pi_netconfig.installer --install --systemd-mode
```

### 4.3. Configure WiFi

If no connection is available, the system creates access point `PiConfig-XXXX` (password: `piconfig123`). Connect and navigate to `http://192.168.50.1:8080` to configure network.

[Return to Table of Contents](<#table of contents>)

## 5. Documentation

- **[User Guide](docs/user-guide.md)** — Installation, deployment, service management, web interface, troubleshooting

For development, build, testing, and governance documentation, see **[Development Guide](docs/development.md)**.

[Return to Table of Contents](<#table of contents>)

## 6. License

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1 | 2026-07-01 | Added script-based installation (bin/install.sh via curl) as primary Quick Start method; retained manual wheel installation as alternative |
| 2.0 | 2026-07-01 | Restructured as user-facing only; removed build-from-source and ai/ governance references; corrected OS reference to Debian 13 Trixie; added Development Guide pointer |
| 1.0 | 2025-12-05 | Initial README |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
