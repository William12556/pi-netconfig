# Pi Network Configuration Tool

WiFi configuration management for Raspberry Pi/Debian systems with automatic access point fallback.

## Overview

Tool manages WiFi connectivity with automatic fallback to access point mode when no connection is available. Designed for headless Raspberry Pi systems without attached displays or keyboards. The system operates as a self-installing systemd service, providing continuous network monitoring and a web-based configuration interface when needed.

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

## Quick Start

**Build distribution package:**

```bash
cd /path/to/pi-netconfig
pip install build
python -m build
```

**Deploy to Raspberry Pi:**

```bash
# Transfer package
scp dist/pi_netconfig-0.2.0-py3-none-any.whl admin@raspberry-pi:/tmp/

# Install on Raspberry Pi
ssh admin@raspberry-pi
sudo pip install /tmp/pi_netconfig-0.2.0-py3-none-any.whl

# Run installer (first execution only)
sudo python3 -m pi_netconfig.main
```

**Configure WiFi:**

If no connection is available, the system creates access point `PiConfig-XXXX` (password: `piconfig123`). Connect and navigate to `http://192.168.50.1:8080` to configure network.

## Documentation

Complete installation, deployment, and operational procedures are documented in:

- **[User Guide](docs/user-guide.md)** - Installation, deployment, service management, testing, architecture, and troubleshooting

Additional technical documentation:

- **[Design Documentation](ai/)** - Architecture specifications, change management, and governance

## Important Notice

**Actual fitness for purpose is not guaranteed.**

## License

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
