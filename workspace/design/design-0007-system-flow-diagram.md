Created: 2025 November 11

# Pi Network Configuration Tool - System Flow Diagram

## Table of Contents

[Purpose](<#purpose>)
[Overview](<#overview>)
[System Flow Diagram](<#system flow diagram>)
[Flow Description](<#flow description>)
  - [Boot Sequence](<#boot sequence>)
  - [State Transitions](<#state transitions>)
  - [Client Mode Operation](<#client mode operation>)
  - [AP Mode Operation](<#ap mode operation>)
  - [Configuration Flow](<#configuration flow>)
  - [Error Handling](<#error handling>)
[Related Design Documents](<#related design documents>)
[Version History](<#version history>)

---

## Purpose

This document provides a comprehensive visual representation of the Pi Network Configuration Tool's operational flow, illustrating the interactions between core components and the system's state machine behavior.

[Return to Table of Contents](<#table of contents>)

## Overview

The system flow diagram maps the complete lifecycle of the network configuration tool, from boot initialization through state transitions, monitoring loops, configuration operations, and error recovery procedures. This visualization complements the master design document by showing the dynamic runtime behavior of the system.

**Source Design**: [Master Design](<design-0000-master.md>)

[Return to Table of Contents](<#table of contents>)

## System Flow Diagram

```mermaid
flowchart TD
    Start([System Boot]) --> Init[ServiceController:<br/>Initialize Logging & Signals]
    Init --> SM[StateMonitor:<br/>Enter CHECKING State]
    
    SM --> Check{ConnectionManager:<br/>Test Connection<br/>ping 8.8.8.8, 1.1.1.1}
    
    Check -->|Connected| Client[STATE: CLIENT<br/>Monitor every 30s]
    Check -->|Failed| Count{Failed<br/>Attempts<br/>>= 3?}
    
    Count -->|No| Wait1[Wait 10s]
    Wait1 --> Check
    
    Count -->|Yes| StartAP[APManager:<br/>Activate AP Mode]
    StartAP --> APConfig[Configure:<br/>SSID: PiConfig-XXXX<br/>Pass: piconfig123<br/>IP: 192.168.50.1/24]
    
    APConfig --> WebStart[WebServer:<br/>Start HTTP on :8080]
    WebStart --> AP[STATE: AP_MODE<br/>Await Configuration]
    
    AP --> WebUI{User Accesses<br/>Configuration<br/>Interface?}
    
    WebUI -->|GET /| Serve[Serve HTML<br/>Configuration Page]
    WebUI -->|GET /api/scan| Scan[ConnectionManager:<br/>Scan Networks<br/>nmcli dev wifi list]
    WebUI -->|POST /api/configure| Apply[ConnectionManager:<br/>Apply Configuration<br/>nmcli connection add]
    WebUI -->|GET /api/status| Status[Return Current<br/>State & Connection Info]
    
    Serve --> AP
    Scan --> ScanResult[Return JSON:<br/>Network List]
    ScanResult --> AP
    Status --> AP
    
    Apply --> Persist[Persist Config:<br/>/etc/pi-netconfig/config.json]
    Persist --> Deactivate[APManager:<br/>Deactivate AP]
    Deactivate --> Connect[ConnectionManager:<br/>Attempt Connection]
    
    Connect --> TestNew{Connection<br/>Successful?}
    TestNew -->|Yes| Client
    TestNew -->|No| Error[Log Error:<br/>Invalid Credentials]
    Error --> StartAP
    
    Client --> Monitor[Monitor Loop:<br/>Check every 30s]
    Monitor --> MonTest{Connection<br/>Active?}
    
    MonTest -->|Yes| Monitor
    MonTest -->|No| FailCount{3 Consecutive<br/>Failures?}
    
    FailCount -->|No| Monitor
    FailCount -->|Yes| Recovery[Log Warning:<br/>Connection Lost]
    Recovery --> StartAP
    
    Init -.->|SIGTERM/SIGINT| Shutdown[ServiceController:<br/>Graceful Shutdown]
    Shutdown --> Cleanup[Deactivate AP<br/>Stop WebServer<br/>Close Connections]
    Cleanup --> Exit([Exit with Code 0])
    
    Check -.->|Exception| ErrLog[Log Error with<br/>Traceback]
    ErrLog --> Retry{Retry<br/>Possible?}
    Retry -->|Yes| Wait2[Exponential<br/>Backoff]
    Wait2 --> Check
    Retry -->|No| Critical[Log Critical Error]
    Critical --> Exit
    
    style Start fill:#e1f5e1
    style Exit fill:#ffe1e1
    style Client fill:#e1e5ff
    style AP fill:#fff4e1
    style SM fill:#f0e1ff
```

[Return to Table of Contents](<#table of contents>)

## Flow Description

### Boot Sequence

1. **System Boot**: ServiceController initializes logging and signal handlers
2. **State Initialization**: StateMonitor enters CHECKING state
3. **Connection Test**: ConnectionManager attempts to verify internet connectivity

### State Transitions

The system operates in two primary states:

**CLIENT Mode**: System has active WiFi connection and monitors connectivity every 30 seconds

**AP_MODE**: System creates temporary access point for configuration when no connection available

### Client Mode Operation

- Connection monitor runs every 30 seconds
- Tests connectivity via ping to external hosts
- Tracks consecutive failures
- Transitions to AP mode after 3 consecutive failures

### AP Mode Operation

- APManager activates access point with SSID format `PiConfig-XXXX`
- WebServer starts on port 8080
- System awaits user configuration via web interface
- Four API endpoints available:
  - `GET /` - Configuration HTML page
  - `GET /api/scan` - Network scan results
  - `POST /api/configure` - Apply network settings
  - `GET /api/status` - Current system state

### Configuration Flow

1. User submits network credentials via web interface
2. Configuration persisted to `/etc/pi-netconfig/config.json`
3. APManager deactivates access point
4. ConnectionManager attempts connection with new credentials
5. On success: transition to CLIENT mode
6. On failure: log error and return to AP mode

### Error Handling

- All exceptions logged with traceback
- Exponential backoff for retryable errors
- Critical errors trigger graceful shutdown
- Signal handlers (SIGTERM/SIGINT) ensure clean deactivation

[Return to Table of Contents](<#table of contents>)

## Related Design Documents

- [Master Design](<design-0000-master.md>) - Complete system architecture
- [StateMonitor Design](<design-0002-statemonitor.md>) - State machine implementation
- [ConnectionManager Design](<design-0003-connectionmanager.md>) - Network operations
- [APManager Design](<design-0004-apmanager.md>) - Access point management
- [WebServer Design](<design-0005-webserver.md>) - HTTP interface
- [ServiceController Design](<design-0006-servicecontroller.md>) - Service lifecycle
- [Systemd Service Diagram](<design-0008-systemd-service-diagram.md>) - Service integration

[Return to Table of Contents](<#table of contents>)

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-11 | William Watson | Initial creation |

[Return to Table of Contents](<#table of contents>)

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
