Created: 2025 December 23

# AP Mode Testing Commands

Quick reference for testing pi-netconfig AP mode transitions and web server functionality.

## Force Transition to AP Mode

### Disconnect from Router
```bash
# Bring down the router connection
sudo nmcli con down MyRouter

# Verify only loopback is active
nmcli con show --active

# Monitor state transition (should transition to AP mode after 3 failures = ~90 seconds)
tail -f /var/log/pi-netconfig.log | grep -E "state=|Transitioning|WebServer"
```

### Expected Log Sequence
```
Connection check: disconnected, state=CLIENT, failures=0
Connection failure count: 1
Connection check: disconnected, state=CLIENT, failures=1
Connection failure count: 2
Connection check: disconnected, state=CLIENT, failures=2
Connection failure count: 3
Transitioning to AP_MODE
AP profile 'pi-netconfig-ap' already exists
Access point activated successfully
Web server started on 0.0.0.0:8080
Successfully transitioned to AP_MODE
```

## Verify AP Mode Active

### Check Network Status
```bash
# Verify AP connection is active
nmcli con show --active | grep pi-netconfig-ap

# Check WiFi interface status
nmcli device status

# Verify AP is broadcasting
nmcli device wifi list | grep PiConfig
```

### Check System State
```bash
# Verify current state is AP_MODE
tail -20 /var/log/pi-netconfig.log | grep "state="

# Check service is running
sudo systemctl status pi-netconfig
```

## Test Web Server

### From Connected Device

Connect to the AP:
- **SSID:** `PiConfig-XXXX` (where XXXX = last 4 MAC characters)
- **Password:** `piconfig123`
- **Gateway:** `192.168.50.1`

```bash
# Check web server is listening (from Pi console)
sudo netstat -tlnp | grep 8080

# Alternative: check with ss
sudo ss -tlnp | grep 8080

# Test web server response (from Pi)
curl -I http://localhost:8080

# Test from connected device (replace with your device IP)
curl -I http://192.168.50.1:8080
```

### Expected Web Server Response
```
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.13.5
Date: Tue, 23 Dec 2025 13:00:00 GMT
Content-Type: text/html; charset=utf-8
Cache-Control: no-cache
```

### Test Web Interface (Browser)

1. Open browser on device connected to AP
2. Navigate to: `http://192.168.50.1:8080/`
3. Should see "WiFi Configuration" page
4. Click "Scan Networks" button
5. Should populate network list

### Test API Endpoints

```bash
# From device connected to AP

# Test scan endpoint
curl http://192.168.50.1:8080/api/scan

# Test status endpoint
curl http://192.168.50.1:8080/api/status

# Test configuration endpoint (replace SSID and password)
curl -X POST http://192.168.50.1:8080/api/configure \
  -H "Content-Type: application/json" \
  -d '{"ssid":"TestNetwork","password":"testpassword"}'
```

## Return to CLIENT Mode

### Reconnect to Router
```bash
# Bring up router connection
sudo nmcli con up MyRouter

# Monitor transition (should detect connectivity within 30 seconds)
tail -f /var/log/pi-netconfig.log | grep -E "state=|Transitioning|connected"
```

### Expected Log Sequence
```
Connection check: connected, state=AP_MODE, failures=X
Transitioning to CLIENT mode
Access point deactivated successfully (or error if already down)
Shutting down web server
Web server stopped
Successfully transitioned to CLIENT mode
Connection check: connected, state=CLIENT, failures=0
```

### Verify CLIENT Mode
```bash
# Check active connections (should show MyRouter, not pi-netconfig-ap)
nmcli con show --active

# Verify web server stopped
sudo netstat -tlnp | grep 8080
# (should return nothing)

# Check log confirms CLIENT mode
tail -10 /var/log/pi-netconfig.log | grep "state="
```

## Troubleshooting

### Web Server Not Starting
```bash
# Check if port 8080 is already in use
sudo netstat -tlnp | grep 8080

# Check for web server errors in log
grep -i webserver /var/log/pi-netconfig.log | tail -20

# Verify AP is actually active
nmcli con show --active | grep pi-netconfig-ap
```

### AP Not Activating
```bash
# Check AP profile exists
nmcli con show | grep pi-netconfig-ap

# Check for AP activation errors
grep -i apmanager /var/log/pi-netconfig.log | tail -20

# Verify WiFi interface is available
nmcli device status | grep wifi
```

### State Not Transitioning
```bash
# Check failure count incrementing
tail -f /var/log/pi-netconfig.log | grep "failure"

# Verify connection test is running
tail -f /var/log/pi-netconfig.log | grep "Connection check"

# Check service is running
sudo systemctl status pi-netconfig
```

## Quick Test Cycle

Complete test cycle (AP mode → CLIENT mode → AP mode):

```bash
# 1. Start in CLIENT mode, force to AP mode
sudo nmcli con down MyRouter
sleep 100  # Wait for 3 failures + transition
curl -I http://localhost:8080  # Should succeed

# 2. Return to CLIENT mode
sudo nmcli con up MyRouter
sleep 35  # Wait for connection detection + transition
sudo netstat -tlnp | grep 8080  # Should be empty

# 3. Verify logs show complete cycle
tail -100 /var/log/pi-netconfig.log | grep -E "Transitioning|Successfully transitioned"
```

## Network Priority Configuration

Ensure router takes priority during boot:

```bash
# Set router to higher priority
sudo nmcli con modify MyRouter connection.autoconnect-priority 100

# Disable AP auto-connect (let pi-netconfig control it)
sudo nmcli con modify pi-netconfig-ap connection.autoconnect no

# Verify settings
nmcli con show MyRouter | grep priority
nmcli con show pi-netconfig-ap | grep autoconnect
```

---

**Notes:**
- Connection checks occur every 30 seconds
- Transition to AP mode requires 3 consecutive failures (≈90 seconds)
- Transition to CLIENT mode occurs on first successful connectivity check
- Web server binds to 0.0.0.0:8080 (accessible from all interfaces)
- AP network uses 192.168.50.0/24 subnet

---

## Version History

| Version | Date | Changes |
|---------|------|---------||
| 1.0 | 2025-12-23 | Initial command reference |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
