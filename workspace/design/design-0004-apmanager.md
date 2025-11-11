Created: 2025 November 11

# APManager Module Design

## Table of Contents

[Project Info](<#project info>)
[Module Overview](<#module overview>)
[Scope](<#scope>)
[Design Constraints](<#design constraints>)
[Component Details](<#component details>)
[Data Design](<#data design>)
[Interfaces](<#interfaces>)
[Error Handling](<#error handling>)
[Cross References](<#cross references>)
[Version History](<#version history>)

---

## Project Info

**Project:** pi-netconfig  
**Module:** APManager  
**Version:** 1.0.0  
**Date:** 2025-11-11  
**Author:** William Watson  
**Master Design:** [design-0000-master.md](<design-0000-master.md>)

[Return to Table of Contents](<#table of contents>)

---

## Module Overview

**Purpose:** Create and manage local WiFi access point for configuration when no router connection exists.

**Responsibilities:**
- Activate WiFi interface in AP mode
- Generate predictable SSID based on device MAC address
- Configure DHCP for connected clients
- Manage AP connection profile lifecycle
- Deactivate AP when switching to client mode

**Context:** Invoked by StateMonitor when transitioning to AP_MODE and when returning to CLIENT mode.

[Return to Table of Contents](<#table of contents>)

---

## Scope

**In Scope:**
- Access point creation via NetworkManager
- SSID generation (PiConfig-XXXX format)
- WPA2 security configuration
- DHCP server configuration (192.168.50.x)
- AP profile activation/deactivation
- MAC address extraction for SSID uniqueness
- Fallback to open AP on WPA2 failure

**Out of Scope:**
- Custom SSID or password configuration
- Multiple simultaneous AP profiles
- Bridge mode or NAT configuration
- Traffic filtering or firewall rules
- Connection client management
- Bandwidth throttling

[Return to Table of Contents](<#table of contents>)

---

## Design Constraints

**Technical:**
- Must use NetworkManager for AP mode
- Single WiFi interface (cannot run AP + client simultaneously)
- Requires root privileges for network operations
- AP and client modes are mutually exclusive

**Implementation:**
- Language: Python 3.11+
- Framework: asyncio for async operations
- External libraries: subprocess, re (stdlib only)
- Standards: PEP 8 compliance, type hints

**Performance:**
- AP activation: < 10 seconds
- AP deactivation: < 3 seconds
- SSID generation: < 1 second

[Return to Table of Contents](<#table of contents>)

---

## Component Details

### AccessPoint Class

**Purpose:** Manage NetworkManager AP connection profile lifecycle

**Attributes:**

```python
ap_ssid: Optional[str]        # Generated SSID (PiConfig-XXXX)
ap_password: str              # Fixed password: piconfig123
ap_profile_name: str          # NetworkManager connection name
ap_active: bool               # Current AP activation status
interface: str                # WiFi interface name (typically wlan0)
```

**Key Methods:**

```python
async def get_wifi_interface() -> str
```
- Executes: `nmcli -t -f DEVICE,TYPE device status`
- Parses output to find wifi interface
- Returns: Interface name (e.g., wlan0)
- Raises: APManagerError if no wifi interface found

```python
async def get_mac_address() -> str
```
- Executes: `nmcli -t -f GENERAL.HWADDR device show {interface}`
- Extracts MAC address
- Returns: MAC address (format: XX:XX:XX:XX:XX:XX)
- Raises: APManagerError if MAC cannot be determined

```python
def generate_ssid() -> str
```
- Gets MAC address
- Extracts last 4 hex digits
- Format: `PiConfig-XXXX` (e.g., PiConfig-A1B2)
- Returns: Generated SSID
- Raises: APManagerError if MAC extraction fails

```python
async def create_ap_profile() -> None
```
- Generates SSID if not already generated
- Executes: `nmcli con add type wifi ifname {interface} con-name {profile} autoconnect no ssid {ssid} mode ap`
- Executes: `nmcli con modify {profile} 802-11-wireless.mode ap`
- Executes: `nmcli con modify {profile} 802-11-wireless-security.key-mgmt wpa-psk`
- Executes: `nmcli con modify {profile} 802-11-wireless-security.psk {password}`
- Executes: `nmcli con modify {profile} ipv4.method shared ipv4.addresses 192.168.50.1/24`
- Raises: APManagerError on profile creation failure

```python
async def delete_ap_profile() -> None
```
- Executes: `nmcli con delete id {profile}`
- Silently succeeds if profile doesn't exist
- Raises: APManagerError on unexpected deletion failure

```python
async def activate_ap() -> bool
```
- Checks if AP already active (return True)
- Creates AP profile if not exists
- Activates profile: `nmcli con up id {profile}`
- Sets ap_active = True
- Returns: True on success
- Raises: APManagerError on activation failure

```python
async def deactivate_ap() -> None
```
- Checks if AP currently active
- Deactivates: `nmcli con down id {profile}`
- Sets ap_active = False
- Does not delete profile (kept for reuse)
- Raises: APManagerError on deactivation failure

```python
async def fallback_to_open_ap() -> bool
```
- Attempts to create open (no password) AP
- Called when WPA2 AP creation fails
- Modifies security: removes wpa-psk requirement
- Returns: True if open AP created successfully
- Raises: APManagerError if open AP also fails

```python
def get_ap_ssid() -> str
```
- Returns: Current AP SSID
- Raises: APManagerError if SSID not generated

```python
def is_active() -> bool
```
- Returns: ap_active status

[Return to Table of Contents](<#table of contents>)

---

## Data Design

### AP Configuration

**SSID Format:**
- Pattern: `PiConfig-XXXX`
- XXXX: Last 4 hexadecimal digits of WiFi MAC address
- Example: `PiConfig-A1B2` for MAC ending in A1:B2

**Security:**
- Protocol: WPA2-PSK
- Password: `piconfig123` (fixed)
- Fallback: Open network (no password) if WPA2 fails

**Network Configuration:**
- IP Address: 192.168.50.1/24
- DHCP Range: 192.168.50.2 - 192.168.50.254
- Method: Shared (NetworkManager built-in DHCP server)
- Gateway: 192.168.50.1 (Pi itself)

**Connection Profile:**
- Name: `pi-netconfig-ap`
- Type: wifi
- Mode: ap
- Autoconnect: no (manually controlled)
- Interface: Dynamic (detected at runtime)

### State Tracking

**ap_active Boolean:**
- True: AP is currently active
- False: AP is inactive
- Used for idempotent activate/deactivate operations

[Return to Table of Contents](<#table of contents>)

---

## Interfaces

### Public Functions

```python
async def activate_ap() -> bool
```
**Purpose:** Enable access point mode  
**Parameters:** None  
**Returns:** True if AP activated successfully  
**Raises:** APManagerError on activation failure

```python
async def deactivate_ap() -> None
```
**Purpose:** Disable access point mode  
**Parameters:** None  
**Returns:** None  
**Raises:** APManagerError on deactivation failure

```python
def get_ap_ssid() -> str
```
**Purpose:** Get current AP SSID  
**Parameters:** None  
**Returns:** AP network name  
**Raises:** APManagerError if SSID not generated

```python
def is_active() -> bool
```
**Purpose:** Check if AP currently active  
**Parameters:** None  
**Returns:** AP activation status  
**Raises:** None

### Component Interactions

**From StateMonitor:**
- `activate_ap()` - called when transitioning to AP_MODE
- `deactivate_ap()` - called when transitioning to CLIENT
- `is_active()` - called to verify state

**From WebServer:**
- `get_ap_ssid()` - called to display SSID in status
- `is_active()` - called for status endpoint

**To NetworkManager (via nmcli):**
- AP profile creation and modification
- Connection activation and deactivation
- Device and interface queries

[Return to Table of Contents](<#table of contents>)

---

## Error Handling

### Exception Hierarchy

```python
class APManagerError(PiNetConfigError):
    """Base exception for AP manager operations"""
    pass

class APActivationError(APManagerError):
    """AP activation failure"""
    pass

class InterfaceDetectionError(APManagerError):
    """WiFi interface detection failure"""
    pass

class ProfileCreationError(APManagerError):
    """AP profile creation failure"""
    pass
```

### Error Conditions and Handling

**No WiFi Interface Found:**
- Condition: nmcli device list contains no wifi interface
- Handling: Raise InterfaceDetectionError
- Recovery: Enter degraded mode, log critical error
- Message: "No WiFi interface detected. Check hardware."

**MAC Address Extraction Failure:**
- Condition: nmcli output cannot be parsed for MAC
- Handling: Raise APManagerError
- Recovery: Generate fallback SSID (PiConfig-0000)
- Log: Warning with nmcli output

**AP Profile Creation Failure:**
- Condition: nmcli con add returns non-zero exit code
- Handling: Raise ProfileCreationError with stderr
- Recovery: Attempt fallback to open AP
- Log: Error with full command and output

**AP Activation Failure:**
- Condition: nmcli con up returns non-zero exit code
- Handling: Raise APActivationError with stderr
- Recovery: StateMonitor retries after delay
- Log: Error with connection profile details

**AP Deactivation Failure:**
- Condition: nmcli con down returns non-zero exit code
- Handling: Log warning, continue (best-effort)
- Recovery: Not critical, may self-resolve on next activation
- Log: Warning with error details

**WPA2 Security Failure:**
- Condition: AP creation succeeds but activation fails
- Handling: Attempt fallback_to_open_ap()
- Recovery: Create open network without password
- Log: Warning about open network security risk

**Interface Busy:**
- Condition: Interface in use by client connection during AP activation
- Handling: Raise APActivationError
- Recovery: Ensure client connection deactivated first (StateMonitor coordination)
- Log: Error with interface status

### Logging

**Level: DEBUG**
- nmcli command execution and output
- MAC address extraction
- SSID generation
- Profile operations (create/modify/delete)

**Level: INFO**
- Successful AP activation
- Successful AP deactivation
- SSID assigned
- IP configuration applied

**Level: WARNING**
- Fallback to open AP
- AP deactivation failures (non-critical)
- MAC address extraction issues with fallback

**Level: ERROR**
- AP activation failures
- Profile creation failures
- Interface detection failures
- nmcli command failures

**Level: CRITICAL**
- No WiFi interface found
- Unable to create any AP (WPA2 and open both fail)
- Unrecoverable AP manager state

[Return to Table of Contents](<#table of contents>)

---

## Cross References

**Master Design:** [design-0000-master.md](<design-0000-master.md>)

**Related Modules:**
- [StateMonitor](<design-0002-statemonitor.md>) - Coordinates AP mode transitions
- [WebServer](<design-0005-webserver.md>) - Runs on AP network (192.168.50.1:8080)
- [ConnectionManager](<design-0003-connectionmanager.md>) - Mutually exclusive with AP mode

**Dependencies:**
- subprocess (stdlib) - nmcli execution
- re (stdlib) - MAC address parsing
- NetworkManager (system service) - AP mode implementation

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-11 | William Watson | Initial module design extracted from master |

[Return to Table of Contents](<#table of contents>)

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
