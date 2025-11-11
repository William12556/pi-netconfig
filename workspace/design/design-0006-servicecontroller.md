Created: 2025 November 11

# ServiceController Module Design

## Table of Contents

[Project Info](<#project info>)
[Module Overview](<#module overview>)
[Scope](<#scope>)
[Design Constraints](<#design constraints>)
[Component Details](<#component details>)
[Execution Modes](<#execution modes>)
[Signal Handling](<#signal handling>)
[Interfaces](<#interfaces>)
[Error Handling](<#error handling>)
[Cross References](<#cross references>)
[Version History](<#version history>)

---

## Project Info

**Project:** pi-netconfig  
**Module:** ServiceController  
**Version:** 1.0.0  
**Date:** 2025-11-11  
**Author:** William Watson  
**Master Design:** [design-0000-master.md](<design-0000-master.md>)

[Return to Table of Contents](<#table of contents>)

---

## Module Overview

**Purpose:** Application entry point managing execution mode detection, installer invocation, logging configuration, and systemd service lifecycle.

**Responsibilities:**
- Determine execution mode (bootstrap vs service)
- Delegate to Installer when service not installed
- Initialize logging infrastructure
- Start StateMonitor event loop
- Handle system signals for graceful shutdown
- Coordinate component cleanup

**Context:** Main entry point invoked by Python interpreter or systemd service manager.

[Return to Table of Contents](<#table of contents>)

---

## Scope

**In Scope:**
- Execution mode detection (bootstrap/service)
- Installer invocation coordination
- Logging configuration and initialization
- Signal handler registration (SIGTERM, SIGINT)
- StateMonitor lifecycle management
- Graceful shutdown coordination
- Exit code management
- Root privilege verification

**Out of Scope:**
- Actual installation operations (delegated to Installer)
- State machine logic (delegated to StateMonitor)
- Network operations (delegated to other modules)
- Service restart logic (handled by systemd)

[Return to Table of Contents](<#table of contents>)

---

## Design Constraints

**Technical:**
- Must work as both standalone script and systemd service
- Requires root privileges for service mode
- Single asyncio event loop for entire application
- Must handle signals gracefully

**Implementation:**
- Language: Python 3.11+
- Framework: asyncio for event loop
- External libraries: logging, signal, asyncio, os, sys (stdlib only)
- Standards: PEP 8 compliance, type hints

**Performance:**
- Startup time: < 5 seconds (excluding installation)
- Shutdown time: < 3 seconds (graceful cleanup)
- Logging initialization: < 1 second

[Return to Table of Contents](<#table of contents>)

---

## Component Details

### ServiceMain Function

**Purpose:** Main entry point and execution flow coordinator

**Signature:**
```python
def main() -> int
```

**Returns:** Exit code (0 = success, 1 = error)

**Processing Logic:**

1. **Mode Detection:**
   - Check if systemd service installed (via Installer.is_service_installed())
   - Determine execution context (manual vs systemd)

2. **Bootstrap Mode (service not installed):**
   - Verify root privileges
   - Call Installer.install()
   - Exit with installer result code

3. **Service Mode (service installed):**
   - Configure logging
   - Verify root privileges
   - Register signal handlers
   - Initialize StateMonitor
   - Start asyncio event loop
   - Wait for shutdown signal
   - Coordinate graceful shutdown
   - Exit with status code

**Key Methods:**

```python
def detect_execution_mode() -> str
```
- Checks for service file existence
- Checks INVOCATION_ID environment variable (systemd indicator)
- Returns: "bootstrap", "service", or "manual"
- No exceptions

```python
def verify_root_privileges() -> bool
```
- Checks effective user ID (os.geteuid())
- Returns: True if root (UID 0)
- Used for both bootstrap and service modes

```python
def configure_logging() -> None
```
- Sets up logging to /var/log/pi-netconfig.log
- Configures format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Sets root logger level to INFO
- Adds console handler for DEBUG (if running in terminal)
- Creates log file if doesn't exist
- Raises: ServiceControllerError on logging setup failure

```python
def register_signal_handlers() -> None
```
- Registers SIGTERM handler for systemd stop
- Registers SIGINT handler for Ctrl+C
- Both signals trigger shutdown_event.set()
- No exceptions

```python
async def run_service() -> None
```
- Creates shutdown_event (asyncio.Event)
- Initializes StateMonitor
- Starts StateMonitor.run()
- Waits for shutdown_event
- Calls StateMonitor.shutdown()
- Raises: ServiceControllerError on critical failures

```python
def signal_handler(signum: int, frame) -> None
```
- Called on SIGTERM or SIGINT
- Logs signal receipt
- Sets shutdown_event
- Allows graceful cleanup

```python
async def graceful_shutdown() -> None
```
- Logs shutdown initiation
- Calls StateMonitor.shutdown()
- Waits for all components to cleanup (timeout: 10 seconds)
- Logs completion or timeout
- Best-effort operation (doesn't raise exceptions)

### Logging Configuration

**Log File:** `/var/log/pi-netconfig.log`

**Format:**
```
2025-11-11 15:30:45 - StateMonitor - INFO - Transitioning to CLIENT mode
2025-11-11 15:30:46 - ConnectionManager - ERROR - Connection failed: timeout
```

**Handlers:**
1. **FileHandler:**
   - Target: /var/log/pi-netconfig.log
   - Level: INFO
   - Rotation: Not implemented (systemd journal handles)

2. **StreamHandler (optional):**
   - Target: sys.stdout
   - Level: DEBUG
   - Only active when running in terminal (not systemd)

**Logger Hierarchy:**
- Root logger: INFO level
- Component loggers: Inherit from root
- Module names used as logger names

[Return to Table of Contents](<#table of contents>)

---

## Execution Modes

### Bootstrap Mode

**Trigger:** Service file does not exist

**Flow:**
1. Detect service not installed
2. Print message: "Service not installed. Starting installation..."
3. Verify root privileges (exit if not root)
4. Call Installer.install()
5. Exit with installer result code
6. Systemd automatically restarts service (now in service mode)

**Exit Codes:**
- 0: Installation successful
- 1: Installation failed or insufficient privileges

### Service Mode

**Trigger:** Service file exists and running under systemd

**Flow:**
1. Detect service installed
2. Configure logging
3. Verify root privileges (exit if not root)
4. Register signal handlers
5. Initialize StateMonitor
6. Enter main event loop
7. Wait for shutdown signal
8. Graceful shutdown
9. Exit with status code

**Exit Codes:**
- 0: Normal shutdown
- 1: Critical error or unhandled exception

### Manual Mode

**Trigger:** Service exists but not running under systemd

**Flow:**
- Same as Service Mode
- Additional console logging (DEBUG level)
- No systemd journal integration
- Useful for development and debugging

[Return to Table of Contents](<#table of contents>)

---

## Signal Handling

### Registered Signals

**SIGTERM (15):**
- Source: `systemctl stop pi-netconfig`
- Purpose: Graceful service shutdown
- Handler: Sets shutdown_event, triggers cleanup

**SIGINT (2):**
- Source: Ctrl+C in terminal
- Purpose: Manual interruption
- Handler: Same as SIGTERM

### Signal Handler Behavior

```python
def signal_handler(signum: int, frame) -> None:
    signal_name = "SIGTERM" if signum == 15 else "SIGINT"
    logger.info(f"Received {signal_name}, initiating shutdown")
    shutdown_event.set()
```

**Non-blocking:** Handler only sets event flag  
**Graceful:** Allows current operations to complete  
**Timeout:** Shutdown enforced after 10 seconds if components unresponsive

### Shutdown Sequence

1. Signal received → handler sets shutdown_event
2. StateMonitor detects event → cancels monitoring loop
3. StateMonitor.shutdown() called:
   - Deactivates AP if active
   - Stops WebServer
   - Cleanup component resources
4. Event loop exits
5. Main function returns exit code
6. Process terminates

[Return to Table of Contents](<#table of contents>)

---

## Interfaces

### Entry Point

```python
if __name__ == "__main__":
    sys.exit(main())
```

**Invocation:**
- Direct: `python3 main.py`
- Systemd: `ExecStart=/usr/bin/python3 /usr/local/bin/pi-netconfig/main.py`

### Public Functions

```python
def main() -> int
```
**Purpose:** Application entry point  
**Parameters:** None  
**Returns:** Exit code (0 or 1)  
**Raises:** None (catches all exceptions, returns error code)

### Component Interactions

**To Installer:**
- `is_service_installed()` - check installation status
- `install()` - perform installation

**To StateMonitor:**
- `__init__()` - create instance
- `run()` - start monitoring loop
- `shutdown()` - graceful cleanup

**From Signal System:**
- Receives SIGTERM/SIGINT
- Sets shutdown_event

[Return to Table of Contents](<#table of contents>)

---

## Error Handling

### Exception Hierarchy

```python
class ServiceControllerError(PiNetConfigError):
    """Base exception for service controller operations"""
    pass

class LoggingConfigurationError(ServiceControllerError):
    """Logging setup failure"""
    pass

class PrivilegeError(ServiceControllerError):
    """Insufficient privileges"""
    pass
```

### Error Conditions and Handling

**Insufficient Privileges:**
- Condition: `os.geteuid() != 0` in service mode
- Handling: Print error message, exit with code 1
- Message: "Service requires root privileges. Run with sudo or via systemd."
- No logging (logger not yet configured)

**Logging Configuration Failure:**
- Condition: Cannot write to /var/log/pi-netconfig.log
- Handling: Print error to stderr, exit with code 1
- Fallback: Attempt console logging only
- Message: "Failed to configure logging: <details>"

**StateMonitor Initialization Failure:**
- Condition: StateMonitor.__init__() raises exception
- Handling: Log critical error, exit with code 1
- Message: "Failed to initialize StateMonitor: <traceback>"

**Unhandled Exception in Event Loop:**
- Condition: Uncaught exception during run_service()
- Handling: Log critical error with traceback, attempt graceful shutdown, exit with code 1
- Ensures: Components cleaned up before exit

**Shutdown Timeout:**
- Condition: Components don't complete cleanup within 10 seconds
- Handling: Log warning, force exit
- Message: "Shutdown timeout. Forcing exit."

**Installer Failure in Bootstrap Mode:**
- Condition: Installer.install() returns False
- Handling: Exit with code 1
- Message: Installer provides details (logged during installation)

### Logging

**Level: DEBUG**
- Execution mode detection
- Signal handler registration
- Component initialization steps
- Event loop state changes

**Level: INFO**
- Service mode activation
- Logging configuration complete
- StateMonitor started
- Signal received
- Shutdown initiated
- Shutdown complete

**Level: WARNING**
- Manual mode detected (not systemd)
- Shutdown timeout approaching
- Component cleanup delays

**Level: ERROR**
- Privilege verification failure
- Component initialization failures
- Event loop exceptions

**Level: CRITICAL**
- Logging configuration failure
- Unrecoverable service error
- Forced exit due to timeout

[Return to Table of Contents](<#table of contents>)

---

## Cross References

**Master Design:** [design-0000-master.md](<design-0000-master.md>)

**Related Modules:**
- [Installer](<design-0001-installer.md>) - Invoked in bootstrap mode
- [StateMonitor](<design-0002-statemonitor.md>) - Primary component managed
- All modules - Indirectly coordinated via StateMonitor

**Dependencies:**
- logging (stdlib) - logging infrastructure
- signal (stdlib) - signal handling
- asyncio (stdlib) - event loop
- os (stdlib) - privilege checking
- sys (stdlib) - exit codes

**System Integration:**
- systemd - service management
- Linux signals - shutdown coordination

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-11 | William Watson | Initial module design extracted from master |

[Return to Table of Contents](<#table of contents>)

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
