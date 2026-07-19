#!/bin/bash
# AP Mode Testing Script - Realistic Disconnection Scenario
# Disables autoconnect on active profile to trigger AP mode
# Tests web server availability during AP mode
# Safe for headless Pi testing - auto-restores connection after observation

LOG="/tmp/ap-test.log"
AP_IP="192.168.50.1"
WEB_PORT="8080"
ACTIVE_CONN=$(nmcli -t -f NAME connection show --active | grep -v '^lo$' | head -n1)

if [ -z "$ACTIVE_CONN" ]; then
    echo "$(date): ERROR: No active WiFi connection found" >> "$LOG"
    exit 1
fi

echo "$(date): AP mode test starting" >> "$LOG"
echo "$(date): Active connection: $ACTIVE_CONN" >> "$LOG"
echo "$(date): Initial state:" >> "$LOG"
nmcli connection show --active >> "$LOG" 2>&1
nmcli device status >> "$LOG" 2>&1
ip addr show wlan0 >> "$LOG" 2>&1

# Disable autoconnect on active connection
echo "$(date): Disabling autoconnect on $ACTIVE_CONN" >> "$LOG"
nmcli connection modify "$ACTIVE_CONN" connection.autoconnect no >> "$LOG" 2>&1

# Restart pi-netconfig service to trigger state machine
echo "$(date): Restarting pi-netconfig service" >> "$LOG"
systemctl restart pi-netconfig.service >> "$LOG" 2>&1
sleep 5

# Bring down current connection
echo "$(date): Bringing down $ACTIVE_CONN" >> "$LOG"
nmcli connection down "$ACTIVE_CONN" >> "$LOG" 2>&1

# Wait 2 minutes for 3 connection failures (30s each) and AP activation
echo "$(date): Waiting 2 minutes for AP mode activation" >> "$LOG"
sleep 120

# Check state after AP should be active
echo "$(date): State after AP activation window:" >> "$LOG"
nmcli connection show --active >> "$LOG" 2>&1
nmcli device status >> "$LOG" 2>&1
ip addr show wlan0 >> "$LOG" 2>&1
journalctl -u pi-netconfig.service --since "2 minutes ago" >> "$LOG" 2>&1

# Test web server availability
echo "$(date): Testing web server availability" >> "$LOG"
if command -v curl &> /dev/null; then
    echo "$(date): Testing with curl" >> "$LOG"
    curl --connect-timeout 5 --max-time 10 -s -o /dev/null -w "HTTP Status: %{http_code}\n" "http://${AP_IP}:${WEB_PORT}/" >> "$LOG" 2>&1
    curl --connect-timeout 5 --max-time 10 -s "http://${AP_IP}:${WEB_PORT}/" >> "$LOG" 2>&1
elif command -v wget &> /dev/null; then
    echo "$(date): Testing with wget" >> "$LOG"
    wget --timeout=10 --tries=1 -q -O - "http://${AP_IP}:${WEB_PORT}/" >> "$LOG" 2>&1
else
    echo "$(date): WARNING: Neither curl nor wget available for testing" >> "$LOG"
fi

# Check if web server is listening
echo "$(date): Checking port ${WEB_PORT} status:" >> "$LOG"
ss -tuln | grep ":${WEB_PORT}" >> "$LOG" 2>&1

# Observe AP mode for 3 minutes
echo "$(date): Observing AP mode for 3 minutes" >> "$LOG"
sleep 180

# Test web server again before shutdown
echo "$(date): Final web server test before restore" >> "$LOG"
if command -v curl &> /dev/null; then
    curl --connect-timeout 5 --max-time 10 -s -o /dev/null -w "HTTP Status: %{http_code}\n" "http://${AP_IP}:${WEB_PORT}/" >> "$LOG" 2>&1
elif command -v wget &> /dev/null; then
    wget --timeout=10 --tries=1 -q -O - "http://${AP_IP}:${WEB_PORT}/" >> "$LOG" 2>&1
fi

# Check state before restore
echo "$(date): State before connection restore:" >> "$LOG"
nmcli connection show --active >> "$LOG" 2>&1
nmcli device status >> "$LOG" 2>&1
ip addr show wlan0 >> "$LOG" 2>&1

# Restore autoconnect and reconnect
echo "$(date): Re-enabling autoconnect on $ACTIVE_CONN" >> "$LOG"
nmcli connection modify "$ACTIVE_CONN" connection.autoconnect yes >> "$LOG" 2>&1

echo "$(date): Bringing up $ACTIVE_CONN" >> "$LOG"
nmcli connection up "$ACTIVE_CONN" >> "$LOG" 2>&1

# Verify final state
sleep 5
echo "$(date): Final state:" >> "$LOG"
nmcli connection show --active >> "$LOG" 2>&1
nmcli device status >> "$LOG" 2>&1
ip addr show wlan0 >> "$LOG" 2>&1

RESTORED=$(nmcli -t -f NAME connection show --active | grep "$ACTIVE_CONN")
if [ -n "$RESTORED" ]; then
    echo "$(date): Connection restored successfully" >> "$LOG"
else
    echo "$(date): WARNING: Connection not restored, trying again" >> "$LOG"
    nmcli connection up "$ACTIVE_CONN" >> "$LOG" 2>&1
fi

echo "$(date): AP mode test complete" >> "$LOG"
