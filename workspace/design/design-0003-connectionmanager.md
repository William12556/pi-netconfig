Created: 2025 November 11

# ConnectionManager Module Design

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
**Module:** ConnectionManager  
**Version:** 1.1.0  
**Date:** 2025-11-12  
**Author:** William Watson  
**Master Design:** [design-0000-master.md](<design-0000-master.md>)

[Return to Table of Contents](<#table of contents>)

---

## Module Overview

**Purpose:** Manage WiFi client mode connections including connectivity testing, network scanning, configuration, and persistence.

**Responsibilities:**
- Test active internet connectivity
- Scan for available WiFi networks
- Configure and activate WiFi connections via NetworkManager
- Persist single network configuration to JSON
- Parse nmcli command output

**Context:** Invoked by StateMonitor for connection checks and by WebServer for network scanning and configuration.

[Return to Table of Contents](<#table of contents>)

---

## Scope

**In Scope:**
- Internet connectivity testing (ping external hosts)
- WiFi network scanning via nmcli
- NetworkManager connection profile management
- Single network configuration persistence
- SSID and password validation
- nmcli output parsing

**Out of Scope:**
- Multiple network profile management
- Priority-based connection selection
- Ethernet configuration
- VPN management
- Network diagnostics beyond connectivity
- Manual connection management

[Return to Table of Contents](<#table of contents>)

---

## Design Constraints

**Technical:**
- Must use NetworkManager (nmcli) for all WiFi operations
- Single network configuration (last successful connection only)
- Non-blocking async operations required
- Must handle nmcli command failures gracefully
- Thread-safe operations (all public methods protected with lock)

**Implementation:**
- Language: Python 3.11+
- Framework: asyncio for async operations
- External libraries: subprocess, socket, json, pathlib (stdlib only)
- Standards: PEP 8 compliance, type hints

**Performance:**
- Connectivity test: < 3 seconds (2 hosts, 1-second timeout each)
- Network scan: < 5 seconds
- Configuration application: < 10 seconds

[Return to Table of Contents](<#table of contents>)

---

## Component Details

### ConnectionTester Class

**Purpose:** Verify active internet connectivity by testing reachability of known hosts

**Key Methods:**

```python
async def test_connection() -> bool
```
- Tests connectivity to 8.8.8.8 and 1.1.1.1 (Google DNS and Cloudflare DNS)
- Uses socket connection with 1-second timeout per host
- Returns: True if either host is reachable
- Raises: ConnectionManagerError if socket operations fail critically

**Processing Logic:**
1. Attempt socket connection to 8.8.8.8:53 (timeout: 1s)
2. If successful → return True
3. If failed → attempt 1.1.1.1:53 (timeout: 1s)
4. If successful → return True
5. If both failed → return False

### NetworkScanner Class

**Purpose:** Scan and parse available WiFi networks using nmcli

**Key Methods:**

```python
async def scan_networks() -> List[NetworkInfo]
```
- Executes: `nmcli -t -f SSID,SIGNAL,SECURITY,FREQ dev wifi list`
- Parses terse output format
- Returns: List of NetworkInfo objects sorted by signal strength (descending)
- Raises: ConnectionManagerError on nmcli failure

```python
def parse_nmcli_output(output: str) -> List[NetworkInfo]
```
- Splits output by lines
- Parses each line format: `SSID:SIGNAL:SECURITY:FREQ`
- Creates NetworkInfo objects
- Filters duplicates (keeps strongest signal per SSID)
- Returns: Parsed network list

**NetworkInfo Data Structure:**
```python
@dataclass
class NetworkInfo:
    ssid: str
    signal_strength: int  # 0-100
    security: str         # WPA2, WPA3, Open, etc.
    frequency: str        # 2.4GHz or 5GHz
```

### ConfigManager Class

**Purpose:** Apply and persist NetworkManager configurations

**Thread Safety:** All public methods protected by class-level threading.Lock to prevent race conditions during concurrent operations

**Key Methods:**

```python
async def configure_network(ssid: str, password: str) -> bool
```
- Validates SSID and password
- Removes existing connection profile (if exists)
- Creates new NetworkManager connection
- Activates connection
- Persists configuration to JSON on success
- Returns: True if configuration and connection successful
- Raises: ConnectionManagerError on validation or nmcli failure

```python
def validate_credentials(ssid: str, password: str) -> None
```
- Validates SSID: 1-32 characters, no special shell characters
- Validates password: 8-63 characters for WPA2/WPA3
- Raises: ConfigurationError with specific validation failure message

```python
async def create_connection_profile(ssid: str, password: str) -> None
```
- Executes: `nmcli con add type wifi ssid {ssid} wifi-sec.key-mgmt wpa-psk wifi-sec.psk {password}`
- Raises: ConnectionManagerError on profile creation failure

```python
async def activate_connection(ssid: str) -> None
```
- Executes: `nmcli con up id {ssid}`
- Waits up to 10 seconds for connection establishment
- Raises: ConnectionManagerError on activation failure

```python
async def delete_connection_profile(ssid: str) -> None
```
- Executes: `nmcli con delete id {ssid}` with check=False
- Gracefully handles non-existent profiles (ignores errors)
- Only raises ConnectionManagerError on critical failures

```python
def persist_configuration(ssid: str) -> None
```
- Writes configuration to `/etc/pi-netconfig/config.json`
- Format: `{"configured_ssid": ssid, "last_connected": ISO8601_timestamp, "ap_password": "piconfig123"}`
- Creates parent directory `/etc/pi-netconfig/` if not exists using `mkdir(parents=True, exist_ok=True)`
- Sets ap_password to default "piconfig123" (WiFi credentials managed by NetworkManager, not persisted)
- Raises: ConnectionManagerError on file write failure

```python
def load_configuration() -> Optional[str]
```
- Reads `/etc/pi-netconfig/config.json`
- Returns: configured_ssid or None if file doesn't exist
- Raises: ConnectionManagerError on JSON parse failure

[Return to Table of Contents](<#table of contents>)

---

## Data Design

### NetworkInfo Data Class

```python
@dataclass
class NetworkInfo:
    ssid: str
    signal_strength: int
    security: str
    frequency: str
```

**Attributes:**
- `ssid`: Network identifier (1-32 characters)
- `signal_strength`: Signal quality (0-100)
- `security`: Security type (WPA2, WPA3, Open, WEP)
- `frequency`: Band (2.4GHz or 5GHz)

### Configuration File

**Location:** `/etc/pi-netconfig/config.json`

**Format:**
```json
{
  "configured_ssid": "MyNetwork",
  "last_connected": "2025-11-11T15:30:00Z",
  "ap_password": "piconfig123"
}
```

**Fields:**
- `configured_ssid`: Last successfully configured network (nullable)
- `last_connected`: ISO 8601 timestamp of last successful connection
- `ap_password`: Access point mode password (always "piconfig123", WiFi passwords not persisted)

### Validation Rules

**SSID:**
- Length: 1-32 characters
- Allowed: Alphanumeric, spaces, hyphens, underscores
- Forbidden: Shell special characters: `;`, `&`, `|`, `$`, `` ` ``, `\`, `"`, `'`

**Password:**
- Length: 8-63 characters for WPA2/WPA3
- No length restriction for Open networks
- Forbidden: Shell special characters (same as SSID)

[Return to Table of Contents](<#table of contents>)

---

## Interfaces

### Public Functions

```python
async def test_connection() -> bool
```
**Purpose:** Verify active internet connectivity  
**Parameters:** None  
**Returns:** True if connection active  
**Raises:** ConnectionManagerError on critical failure

```python
async def scan_networks() -> List[NetworkInfo]
```
**Purpose:** Scan for available WiFi networks  
**Parameters:** None  
**Returns:** List of NetworkInfo sorted by signal strength  
**Raises:** ConnectionManagerError on scan failure

```python
async def configure_network(ssid: str, password: str) -> bool
```
**Purpose:** Apply WiFi configuration  
**Parameters:**
- `ssid`: Target network SSID
- `password`: Network password  
**Returns:** True if configuration successful  
**Raises:** ConnectionManagerError on configuration failure

```python
def load_configuration() -> Optional[str]
```
**Purpose:** Load last configured network  
**Parameters:** None  
**Returns:** Configured SSID or None  
**Raises:** ConnectionManagerError on JSON parse failure

### Component Interactions

**From StateMonitor:**
- `test_connection()` - called every 30 seconds
- `configure_network()` - called after AP mode configuration

**From WebServer:**
- `scan_networks()` - called on GET /api/scan
- `configure_network()` - called on POST /api/configure
- `load_configuration()` - called on GET /api/status

**To NetworkManager (via nmcli):**
- Network scanning
- Connection profile management
- Connection activation

[Return to Table of Contents](<#table of contents>)

---

## Error Handling

### Exception Hierarchy

```python
class ConnectionManagerError(PiNetConfigError):
    """Base exception for connection manager operations"""
    pass

class ConfigurationError(ConnectionManagerError):
    """Configuration validation or application failure"""
    pass

class NetworkScanError(ConnectionManagerError):
    """Network scan operation failure"""
    pass

class ConnectivityTestError(ConnectionManagerError):
    """Connectivity test failure"""
    pass
```

### Error Conditions and Handling

**nmcli Command Failure:**
- Condition: `subprocess.run()` returns non-zero exit code
- Handling: Raise ConnectionManagerError with command, exit code, stderr
- Recovery: Caller (StateMonitor/WebServer) handles retry logic

**Invalid Credentials:**
- Condition: Validation fails (length, characters)
- Handling: Raise ConfigurationError with specific validation message
- Recovery: Return error to WebServer for user correction

**Connection Activation Timeout:**
- Condition: Connection not established within 10 seconds
- Handling: Raise ConnectionManagerError with timeout details
- Recovery: Remain in or return to AP_MODE

**Configuration File Read/Write Error:**
- Condition: File operations raise IOError
- Handling: Raise ConnectionManagerError with file path and error
- Recovery: Non-critical, continue operation without persistence

**Network Scan No Results:**
- Condition: nmcli returns empty output
- Handling: Return empty list (not an error)
- Recovery: User sees "No networks found" in web interface

**Socket Connection Failure:**
- Condition: Both connectivity test hosts unreachable
- Handling: Return False (not an error - normal disconnected state)
- Recovery: StateMonitor increments failure_count

### Logging

**Level: DEBUG**
- nmcli command execution and output
- Socket connection attempts
- Configuration file operations
- Validation checks

**Level: INFO**
- Successful network scans (count)
- Successful configuration application
- Connection activation
- Configuration persistence

**Level: WARNING**
- Connectivity test failures (both hosts)
- Network scan returned no results
- Configuration file read failures (non-critical)

**Level: ERROR**
- nmcli command failures
- Configuration validation failures
- Connection activation failures
- JSON parse errors

[Return to Table of Contents](<#table of contents>)

---

## Cross References

**Master Design:** [design-0000-master.md](<design-0000-master.md>)

**Related Modules:**
- [StateMonitor](<design-0002-statemonitor.md>) - Primary consumer for connection testing
- [WebServer](<design-0005-webserver.md>) - Consumer for scanning and configuration
- [APManager](<design-0004-apmanager.md>) - Coordinates mode switching

**Dependencies:**
- subprocess (stdlib) - nmcli execution
- socket (stdlib) - connectivity testing
- json (stdlib) - configuration persistence
- pathlib (stdlib) - file operations
- NetworkManager (system service) - WiFi management

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-11 | William Watson | Initial module design extracted from master |
| 1.1.0 | 2025-11-12 | William Watson | Updated per [change-0001](<../change/change-0001-connectionmanager-defect-corrections.md>): Added thread safety requirements, corrected persist_configuration signature (removed password parameter), clarified ap_password usage, added directory creation requirement, specified graceful nmcli delete error handling |

[Return to Table of Contents](<#table of contents>)

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
