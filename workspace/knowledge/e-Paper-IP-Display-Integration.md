# e-Paper IP Display Integration

Created: 2025-12-05

## Table of Contents

1. [Project Overview](<#1 project overview>)
2. [Technical Specifications](<#2 technical specifications>)
3. [Integration with pi-netconfig](<#3 integration with pi-netconfig>)
4. [Test Validation](<#4 test validation>)
5. [Operational Behavior](<#5 operational behavior>)
6. [References](<#6 references>)
7. [Version History](<#version history>)

## 1. Project Overview

The e-Paper IP Display is a companion project deployed on the same Raspberry Pi hardware as pi-netconfig. It provides visual network status feedback using a Waveshare 2.13" Touch e-Paper HAT Version 4.

**Primary Function:** Display current IPv4 address or "No Network" status on physical e-paper screen.

**Integration Status:** Deployed and operational on pi-netconfig test hardware (deb1.local, Debian 13 Trixie).

[Return to Table of Contents](<#table of contents>)

## 2. Technical Specifications

### Hardware
- Waveshare 2.13" Touch e-Paper HAT Version 4
- 40-pin GPIO interface
- SPI interface (display control)
- I²C interface (touch controller)

### Software
- Python 3.9+ application
- Systemd service: `epaper-ip-display.service`
- Root privileges required (GPIO access)
- Dependencies: `python3-pil`, `python3-spidev`, `python3-rpi.gpio`, `fonts-liberation`

### Behavior
- 15-second network polling interval
- Display updates only on IP address change
- Shows "No Network" when no IPv4 connectivity detected
- Clears display on service startup
- Persists across reboots

[Return to Table of Contents](<#table of contents>)

## 3. Integration with pi-netconfig

### Deployment Context

The e-Paper display operates independently but provides complementary functionality to pi-netconfig:

- **CLIENT Mode:** Display shows WiFi-assigned IPv4 address
- **AP Mode:** Display shows "No Network" (AP interface not monitored)
- **Transition States:** Display reflects real-time network status

### Shared Hardware Environment

Both systems operate on:
- Hostname: `deb1.local`
- Platform: Debian GNU/Linux 13 (trixie)
- Network interfaces: WiFi adapter managed by pi-netconfig

### Independence

The e-Paper display service operates autonomously:
- No direct coupling to pi-netconfig state machine
- No shared process communication
- No configuration dependencies
- Independent systemd service lifecycle

[Return to Table of Contents](<#table of contents>)

## 4. Test Validation

### Observed Behavior in pi-netconfig Tests

**CLIENT Mode Test:**
- e-Paper display shows assigned IPv4 address
- Updates occur when DHCP lease obtained
- Confirms successful router connection

**AP Mode Test:**
- Display shows "No Network"
- Confirms no external router connectivity
- Validates isolation of AP-only state

### Test Integration Value

The e-Paper display provides:
1. **Visual confirmation** of network state during manual testing
2. **Independent validation** of connectivity status
3. **Physical feedback** for headless system operation
4. **Debugging aid** for state transition verification

### No Automated Test Coupling

The display is **not integrated** into pytest test suite:
- Tests do not query display state
- Display behavior is observational only
- No test dependencies on display service

[Return to Table of Contents](<#table of contents>)

## 5. Operational Behavior

### Update Mechanism

```
Poll network (every 15s)
  → Query IPv4 address
  → Compare to cached value
  → If changed: update e-paper display
  → If no IP: display "No Network"
```

### State Transitions

| Network State | Display Output |
|--------------|----------------|
| WiFi connected, DHCP assigned | IPv4 address (e.g., "192.168.1.100") |
| WiFi disconnected | "No Network" |
| AP mode active | "No Network" |
| System boot | Cleared display → current state |

### Service Management

```bash
# Check status
sudo systemctl status epaper-ip-display.service

# View logs
journalctl -u epaper-ip-display.service -f

# Restart service
sudo systemctl restart epaper-ip-display.service
```

[Return to Table of Contents](<#table of contents>)

## 6. References

**Project Repository:**
- Location: `/Users/williamwatson/Documents/GitHub/e-Paper-IP-Display`
- Documentation: `docs/` directory
- License: MIT License

**Hardware Documentation:**
- Waveshare e-Paper GitHub: https://github.com/waveshare/e-Paper
- Product wiki: https://www.waveshare.com/wiki/2.13inch_Touch_e-Paper_HAT

**Related pi-netconfig Documentation:**
- Hardware validation: Raspberry Pi platform (deb1.local)
- Test execution: CLIENT/AP mode validation

[Return to Table of Contents](<#table of contents>)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-05 | Initial project knowledge summary |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
