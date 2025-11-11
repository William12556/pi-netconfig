Created: 2025 November 11

# StateMonitor Module Design

## Table of Contents

[Project Info](<#project info>)
[Module Overview](<#module overview>)
[Scope](<#scope>)
[Design Constraints](<#design constraints>)
[Component Details](<#component details>)
[State Machine](<#state machine>)
[Interfaces](<#interfaces>)
[Error Handling](<#error handling>)
[Cross References](<#cross references>)
[Version History](<#version history>)

---

## Project Info

**Project:** pi-netconfig  
**Module:** StateMonitor  
**Version:** 1.0.0  
**Date:** 2025-11-11  
**Author:** William Watson  
**Master Design:** [design-0000-master.md](<design-0000-master.md>)

[Return to Table of Contents](<#table of contents>)

---

## Module Overview

**Purpose:** Main state machine managing service operational mode transitions between checking, client, and AP modes.

**Responsibilities:**
- Determine current operational state
- Coordinate transitions between states
- Initialize and shutdown components
- Maintain connection monitoring loop
- Recover from state transition failures

**Context:** Core orchestrator initialized by ServiceController and coordinating all other operational modules.

[Return to Table of Contents](<#table of contents>)

---

## Scope

**In Scope:**
- State enumeration (CHECKING, CLIENT, AP_MODE)
- State transition logic and coordination
- 30-second monitoring loop
- Component initialization and shutdown
- Connection failure detection (3 consecutive failures)
- State recovery mechanisms

**Out of Scope:**
- Actual network operations (delegated to ConnectionManager)
- Access point operations (delegated to APManager)
- Web interface management (delegated to WebServer)
- Installation (handled by Installer)

[Return to Table of Contents](<#table of contents>)

---

## Design Constraints

**Technical:**
- Single asyncio event loop
- Non-blocking operations required
- Must coordinate three independent modules
- State persistence across monitoring cycles

**Implementation:**
- Language: Python 3.11+
- Framework: asyncio
- External libraries: asyncio (stdlib), enum (stdlib)
- Standards: PEP 8 compliance, type hints

**Performance:**
- State check interval: 30 seconds
- State transition time: < 2 seconds
- Failure detection: 3 checks (90 seconds maximum)

[Return to Table of Contents](<#table of contents>)

---

## Component Details

### State Enumeration

```python
from enum import Enum, auto

class SystemState(Enum):
    CHECKING = auto()    # Verifying connection status
    CLIENT = auto()      # Connected to router/AP
    AP_MODE = auto()     # Running as access point
```

### StateMachine Class

**Purpose:** Implement state transitions and mode coordination

**Attributes:**

```python
current_state: SystemState
failure_count: int
connection_manager: ConnectionManager
ap_manager: APManager
web_server: WebServer
monitoring_task: asyncio.Task
shutdown_event: asyncio.Event
```

**Key Methods:**

```python
async def initialize() -> None
```
- Creates component instances
- Initializes shutdown event
- Starts monitoring task
- Raises: StateMonitorError on component initialization failure

```python
async def monitoring_loop() -> None
```
- Infinite loop with 30-second intervals
- Checks connection status
- Evaluates state transitions
- Handles asyncio.CancelledError for graceful shutdown
- No return value (runs until cancelled)

```python
async def check_connection() -> bool
```
- Delegates to ConnectionManager.test_connection()
- Returns: True if connection active
- Raises: StateMonitorError on check failure

```python
async def transition_to_client() -> None
```
- Deactivates AP mode (if active)
- Stops web server
- Resets failure count
- Updates current_state to CLIENT
- Raises: StateMonitorError on transition failure

```python
async def transition_to_ap_mode() -> None
```
- Activates AP mode via APManager
- Starts web server on port 8080
- Updates current_state to AP_MODE
- Raises: StateMonitorError on transition failure

```python
async def handle_state_transition_failure(error: Exception) -> None
```
- Logs error details with traceback
- Attempts recovery to last known good state
- Increments failure count
- Enters degraded mode if recovery fails

```python
async def shutdown() -> None
```
- Sets shutdown event
- Cancels monitoring task
- Deactivates AP (if active)
- Stops web server
- Cleanup component resources

**State Transition Logic:**

```
CHECKING State:
  - Check connection status
  - If connected → transition to CLIENT
  - If not connected → increment failure_count
  - If failure_count >= 3 → transition to AP_MODE

CLIENT State:
  - Check connection every 30 seconds
  - If connection lost → increment failure_count
  - If failure_count >= 3 → transition to AP_MODE
  - If connection maintained → reset failure_count to 0

AP_MODE State:
  - Monitor web server for configuration events
  - On configuration received → attempt connection
  - If connection successful → transition to CLIENT
  - If connection fails → remain in AP_MODE
  - Web server remains active until successful configuration
```

[Return to Table of Contents](<#table of contents>)

---

## State Machine

### State Diagram

```
┌─────────────┐
│  CHECKING   │◄──┐ (boot/initialization)
└──────┬──────┘   │
       │          │
       ├─connected→ ┌──────────┐
       │            │  CLIENT  │
       │            └────┬─────┘
       │                 │
       │            lost │
       │            connection
       │            (3x) │
       │                 │
       │                 ▼
       └─not connected→ ┌──────────┐
         (3x)            │ AP_MODE  │
                         └────┬─────┘
                              │
                              └─config successful→ CLIENT
```

### State Transitions Table

| From State | Event | To State | Actions |
|------------|-------|----------|---------|
| CHECKING | Connection detected | CLIENT | Reset failure count |
| CHECKING | No connection (3x) | AP_MODE | Activate AP, start web server |
| CLIENT | Connection maintained | CLIENT | Reset failure count |
| CLIENT | Connection lost (3x) | AP_MODE | Activate AP, start web server |
| AP_MODE | Config successful + connected | CLIENT | Deactivate AP, stop web server |
| AP_MODE | Config failed | AP_MODE | Remain in AP mode |

[Return to Table of Contents](<#table of contents>)

---

## Interfaces

### Public Functions

```python
async def run() -> None
```
**Purpose:** Main entry point for state monitoring  
**Parameters:** None  
**Returns:** None (runs until shutdown)  
**Raises:** StateMonitorError on critical failures

**Processing:**
1. Initialize components
2. Start monitoring loop
3. Handle shutdown signal
4. Cleanup resources

### Component Interfaces

**To ConnectionManager:**
```python
async def test_connection() -> bool
```
- Called every 30 seconds in all states
- Returns connection status

**To APManager:**
```python
async def activate_ap() -> bool
async def deactivate_ap() -> None
```
- Called during state transitions to/from AP_MODE

**To WebServer:**
```python
async def start_server() -> None
async def stop_server() -> None
async def wait_for_configuration() -> tuple[str, str]
```
- Called during AP_MODE transitions
- wait_for_configuration() blocks until user submits config

**From ServiceController:**
```python
async def shutdown() -> None
```
- Invoked on SIGTERM/SIGINT
- Triggers graceful shutdown

[Return to Table of Contents](<#table of contents>)

---

## Error Handling

### Exception Hierarchy

```python
class StateMonitorError(PiNetConfigError):
    """Base exception for state monitor operations"""
    pass

class StateTransitionError(StateMonitorError):
    """State transition failure"""
    pass

class ComponentInitializationError(StateMonitorError):
    """Component initialization failure"""
    pass
```

### Error Conditions and Handling

**Connection Check Failure:**
- Condition: ConnectionManager.test_connection() raises exception
- Handling: Log warning, treat as connection failure, increment failure_count
- Recovery: Continue monitoring loop

**AP Activation Failure:**
- Condition: APManager.activate_ap() raises APManagerError
- Handling: Log error, attempt recovery to CLIENT state
- Recovery: Retry activation after 60 seconds

**Web Server Start Failure:**
- Condition: WebServer.start_server() raises WebServerError
- Handling: Log critical error, attempt AP deactivation
- Recovery: Enter degraded mode, log instructions for manual intervention

**State Transition Failure:**
- Condition: Any transition method raises exception
- Handling: Log error with traceback, attempt recovery to last known state
- Recovery: If recovery fails, enter degraded mode

**Component Shutdown Failure:**
- Condition: Component cleanup raises exception during shutdown
- Handling: Log error, continue shutdown process (best-effort)
- No exception propagation during shutdown

### Logging

**Level: DEBUG**
- State transition initiation
- Connection check results
- Failure count increments
- Component method calls

**Level: INFO**
- Successful state transitions
- Connection status changes
- Monitoring loop start/stop

**Level: WARNING**
- Connection check failures
- Retry attempts
- Degraded mode entry

**Level: ERROR**
- State transition failures
- Component errors
- Recovery attempts

**Level: CRITICAL**
- Unrecoverable state machine failure
- Component initialization failure
- Shutdown failures

[Return to Table of Contents](<#table of contents>)

---

## Cross References

**Master Design:** [design-0000-master.md](<design-0000-master.md>)

**Related Modules:**
- [ServiceController](<design-0006-servicecontroller.md>) - Initializes StateMonitor
- [ConnectionManager](<design-0003-connectionmanager.md>) - Provides connection testing
- [APManager](<design-0004-apmanager.md>) - Manages AP mode
- [WebServer](<design-0005-webserver.md>) - Provides configuration interface

**Dependencies:**
- asyncio (stdlib)
- enum (stdlib)
- ConnectionManager, APManager, WebServer modules

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-11 | William Watson | Initial module design extracted from master |

[Return to Table of Contents](<#table of contents>)

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
