# Logging Analysis Guide

Created: 2025 November 30

## Table of Contents

1. [Overview](#overview)
2. [Log Collection Methods](#log-collection-methods)
   - [Direct Log File Retrieval](#direct-log-file-retrieval)
   - [Real-time Log Streaming](#real-time-log-streaming)
   - [Automated Log Collection](#automated-log-collection)
3. [Log Locations](#log-locations)
4. [Log Analysis Tools](#log-analysis-tools)
5. [Continuous Monitoring](#continuous-monitoring)
6. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

[Return to Table of Contents](#table-of-contents)

## Overview

The pi-netconfig system implements comprehensive logging throughout all modules (Installer, StateMonitor, ConnectionManager, APManager, WebServer, ServiceController) using Python's logging framework with traceback support. This guide covers methods for collecting and analyzing log data from deployed Raspberry Pi systems.

---

[Return to Table of Contents](#table-of-contents)

## Log Collection Methods

### Direct Log File Retrieval

Retrieve log files from the Raspberry Pi to your Mac for offline analysis:

```bash
# SSH into Raspberry Pi
ssh pi@<raspberry-pi-ip>

# Collect systemd service logs
sudo journalctl -u pi-netconfig.service > ~/pi-netconfig.log

# Transfer logs to Mac using scp
scp pi@<raspberry-pi-ip>:/var/log/pi-netconfig/*.log ~/local-analysis/
```

### Real-time Log Streaming

Monitor logs in real-time during debugging sessions:

```bash
# Stream logs directly to Mac terminal
ssh pi@<raspberry-pi-ip> 'sudo journalctl -u pi-netconfig.service -f'

# Stream directly to Mac file (creates persistent connection)
ssh pi@<raspberry-pi-ip> 'sudo journalctl -u pi-netconfig.service -f' > ~/pi-logs/live-stream.log

# Append to existing file
ssh pi@<raspberry-pi-ip> 'sudo journalctl -u pi-netconfig.service -f' >> ~/pi-logs/live-stream.log

# Stream with timestamped filename
ssh pi@<raspberry-pi-ip> 'sudo journalctl -u pi-netconfig.service -f' > ~/pi-logs/stream-$(date +%Y%m%d-%H%M%S).log

# Stream to file AND view in terminal simultaneously
ssh pi@<raspberry-pi-ip> 'sudo journalctl -u pi-netconfig.service -f' | tee ~/pi-logs/live-stream.log
```

**Note**: Direct streaming creates a persistent SSH connection that continuously writes logs to your Mac filesystem in real-time. The connection remains active until terminated with Ctrl+C. The log file on your Mac updates as events occur on the Raspberry Pi.

### Automated Log Collection

Use the following script to automate periodic log collection:

```bash
#!/bin/bash
# save as collect-pi-logs.sh

PI_IP="raspberry-pi.local"
DATE=$(date +%Y%m%d-%H%M%S)
LOG_DIR="$HOME/pi-netconfig-logs/$DATE"

mkdir -p "$LOG_DIR"

# Systemd service logs
ssh pi@$PI_IP 'sudo journalctl -u pi-netconfig.service --no-pager' > "$LOG_DIR/service.log"

# Application logs from syslog
ssh pi@$PI_IP 'sudo cat /var/log/syslog | grep pi-netconfig' > "$LOG_DIR/syslog.log"

# System status snapshot
ssh pi@$PI_IP 'systemctl status pi-netconfig.service' > "$LOG_DIR/status.txt"

echo "Logs collected to $LOG_DIR"
```

Make the script executable:

```bash
chmod +x collect-pi-logs.sh
./collect-pi-logs.sh
```

---

[Return to Table of Contents](#table-of-contents)

## Log Locations

Logs are stored in the following locations on the Raspberry Pi:

- **Systemd Journal**: `/var/log/journal/`
- **Application Logs**: `/var/log/pi-netconfig/` (if configured)
- **Syslog**: `/var/log/syslog`

---

[Return to Table of Contents](#table-of-contents)

## Log Analysis Tools

### Search for Errors

```bash
# Find all errors and exceptions
grep -i "error\|exception\|traceback" ~/pi-netconfig-logs/*/*.log

# Filter by specific module
grep "StateMonitor\|ConnectionManager" ~/pi-netconfig-logs/*/*.log

# Time-based filtering
grep "2025-11-30" ~/pi-netconfig-logs/*/*.log
```

### Module-Specific Analysis

```bash
# StateMonitor events
grep "StateMonitor" ~/pi-netconfig-logs/*/*.log

# Connection attempts
grep "ConnectionManager.*attempt\|connect" ~/pi-netconfig-logs/*/*.log

# Access Point status
grep "APManager.*started\|stopped" ~/pi-netconfig-logs/*/*.log
```

---

[Return to Table of Contents](#table-of-contents)

## Continuous Monitoring

For persistent log monitoring sessions, use tmux:

```bash
# Start monitoring session
ssh pi@<raspberry-pi-ip>
tmux new -s logs
sudo journalctl -u pi-netconfig.service -f

# Detach from session: Ctrl+B, then D
# Reattach later: tmux attach -t logs
```

---

[Return to Table of Contents](#table-of-contents)

## Troubleshooting Common Issues

### Service Not Starting

```bash
# Check service status
ssh pi@<raspberry-pi-ip> 'systemctl status pi-netconfig.service'

# View recent errors
ssh pi@<raspberry-pi-ip> 'sudo journalctl -u pi-netconfig.service -n 50'
```

### Network Connection Failures

```bash
# Check NetworkManager status
grep "nmcli" ~/pi-netconfig-logs/*/*.log

# Verify WiFi scanning
grep "scan.*result" ~/pi-netconfig-logs/*/*.log
```

### Access Point Issues

```bash
# Check AP creation
grep "APManager.*create\|start" ~/pi-netconfig-logs/*/*.log

# Verify dnsmasq status
grep "dnsmasq" ~/pi-netconfig-logs/*/*.log
```

---

[Return to Table of Contents](#table-of-contents)

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-30 | Claude Desktop | Initial documentation |
| 1.1 | 2025-11-30 | Claude Desktop | Enhanced real-time streaming section with direct-to-Mac file streaming capabilities |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
