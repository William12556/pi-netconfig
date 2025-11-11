Created: 2025 November 11

# Installer Module Design

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
**Module:** Installer  
**Version:** 1.0.0  
**Date:** 2025-11-11  
**Author:** William Watson  
**Master Design:** [design-0000-master.md](<design-0000-master.md>)

[Return to Table of Contents](<#table of contents>)

---

## Module Overview

**Purpose:** Self-installation mechanism that detects existing systemd service installation and configures the system on first run.

**Responsibilities:**
- Detect if systemd service already installed
- Create required directories and files
- Copy application to installation location
- Generate and install systemd unit file
- Enable and start systemd service
- Verify installation success

**Context:** Invoked by ServiceController on first application run when systemd service not detected.

[Return to Table of Contents](<#table of contents>)

---

## Scope

**In Scope:**
- Service file detection at `/etc/systemd/system/pi-netconfig.service`
- Directory creation: `/usr/local/bin/pi-netconfig/`, `/etc/pi-netconfig/`, `/var/log/`
- File operations: copy script to installation location
- Systemd unit file generation
- Systemd service enablement and activation
- Root privilege verification
- Installation rollback on failure

**Out of Scope:**
- Application updates or upgrades
- Service removal/uninstallation
- Configuration file management (handled by ConnectionManager)
- Runtime operation (handled by other modules)

[Return to Table of Contents](<#table of contents>)

---

## Design Constraints

**Technical:**
- Requires root privileges for all operations
- Must work with systemd (standard on Raspbian Bookworm)
- Must handle partial installation failures
- Single execution model (run once, then exit)

**Implementation:**
- Language: Python 3.11+
- External libraries: subprocess, shutil, os, pathlib (stdlib only)
- Standards: PEP 8 compliance, type hints

**Performance:**
- Installation completion: < 30 seconds
- Clean failure and rollback: < 5 seconds

[Return to Table of Contents](<#table of contents>)

---

## Component Details

### InstallationDetector Class

**Purpose:** Check for existing systemd service installation

**Key Methods:**

```python
def is_service_installed() -> bool
```
- Checks for existence of `/etc/systemd/system/pi-netconfig.service`
- Returns True if service file exists
- Raises: InstallerError if filesystem access fails

```python
def get_current_script_path() -> Path
```
- Returns absolute path of currently executing script
- Used for self-copy operation
- Raises: InstallerError if path cannot be determined

### SystemdInstaller Class

**Purpose:** Perform installation steps and systemd configuration

**Key Methods:**

```python
def verify_root_privileges() -> bool
```
- Checks effective user ID == 0
- Returns True if running as root
- No exceptions (returns False on non-root)

```python
def create_directories() -> None
```
- Creates: `/usr/local/bin/pi-netconfig/`, `/etc/pi-netconfig/`, `/var/log/`
- Sets proper permissions (755 for directories)
- Raises: InstallerError on creation failure

```python
def copy_application() -> None
```
- Copies current script to `/usr/local/bin/pi-netconfig/main.py`
- Sets executable permissions (755)
- Raises: InstallerError on copy failure

```python
def generate_systemd_unit() -> str
```
- Returns systemd unit file content as string
- Template includes:
  - `[Unit]` section with description and network dependency
  - `[Service]` section with ExecStart, restart policy
  - `[Install]` section with WantedBy=multi-user.target
- No exceptions

```python
def install_systemd_unit(unit_content: str) -> None
```
- Writes unit file to `/etc/systemd/system/pi-netconfig.service`
- Executes `systemctl daemon-reload`
- Raises: InstallerError on write or systemctl failure

```python
def enable_and_start_service() -> None
```
- Executes `systemctl enable pi-netconfig`
- Executes `systemctl start pi-netconfig`
- Raises: InstallerError on systemctl command failure

```python
def rollback_installation() -> None
```
- Removes created directories and files
- Best-effort cleanup (does not raise exceptions)
- Logs cleanup actions

**Processing Logic:**

1. Verify root privileges → exit with error message if not root
2. Check if service already installed → skip installation if exists
3. Create required directories
4. Copy application script to installation location
5. Generate systemd unit file content
6. Install unit file and reload systemd
7. Enable and start service
8. On any failure: rollback partial installation
9. Exit with status code 0 (success) or 1 (failure)

[Return to Table of Contents](<#table of contents>)

---

## Data Design

### Systemd Unit File Template

**Location:** Generated in-memory, installed to `/etc/systemd/system/pi-netconfig.service`

**Content Structure:**
```ini
[Unit]
Description=Pi Network Configuration Service
After=network.target
Wants=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/local/bin/pi-netconfig/main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
User=root

[Install]
WantedBy=multi-user.target
```

### Installation Paths

**Application:**
- Source: Current script location (detected at runtime)
- Destination: `/usr/local/bin/pi-netconfig/main.py`

**Configuration:**
- Directory: `/etc/pi-netconfig/`
- Initial state: Empty (config.json created by ConnectionManager)

**Logs:**
- Directory: `/var/log/`
- File: `pi-netconfig.log` (created by ServiceController logging)

[Return to Table of Contents](<#table of contents>)

---

## Interfaces

### Public Functions

```python
async def install() -> bool
```
**Purpose:** Main installation entry point  
**Parameters:** None  
**Returns:** True if installation successful, False otherwise  
**Raises:** InstallerError on critical failures  

**Processing:**
1. Verify root privileges
2. Check existing installation
3. Execute installation steps
4. Rollback on failure
5. Return success/failure status

### Internal Interfaces

**To ServiceController:**
- Invoked by ServiceController.main() when service not detected
- Returns control after installation completion
- Exit signal: process exit (systemd restarts application)

**From ServiceController:**
- Receives execution context (bootstrap mode indicator)

[Return to Table of Contents](<#table of contents>)

---

## Error Handling

### Exception Hierarchy

```python
class InstallerError(PiNetConfigError):
    """Base exception for installer operations"""
    pass

class PrivilegeError(InstallerError):
    """Insufficient privileges for installation"""
    pass

class FileSystemError(InstallerError):
    """Directory or file operation failure"""
    pass

class SystemdError(InstallerError):
    """Systemd command execution failure"""
    pass
```

### Error Conditions and Handling

**Insufficient Privileges:**
- Condition: `os.geteuid() != 0`
- Handling: Print error message, exit with code 1
- Message: "Installation requires root privileges. Run with sudo."

**Directory Creation Fails:**
- Condition: `os.makedirs()` raises exception
- Handling: Raise FileSystemError, trigger rollback
- Log: Full traceback with path details

**Script Copy Fails:**
- Condition: `shutil.copy2()` raises exception
- Handling: Raise FileSystemError, trigger rollback
- Log: Source and destination paths, error details

**Systemd Commands Fail:**
- Condition: `subprocess.run()` returns non-zero exit code
- Handling: Raise SystemdError, trigger rollback
- Log: Command executed, stderr output, exit code

**Rollback Failures:**
- Condition: Cleanup operations fail during rollback
- Handling: Log errors but continue (best-effort cleanup)
- No exceptions raised during rollback

### Logging

**Level: DEBUG**
- Each installation step start/completion
- Directory paths created
- File operations performed
- Systemctl commands executed

**Level: INFO**
- Installation start
- Service detection result
- Installation success

**Level: WARNING**
- Rollback initiated
- Cleanup operation failures

**Level: ERROR**
- Installation step failures
- Exception details with traceback

**Level: CRITICAL**
- Installation failed after rollback
- Systemd integration failure

[Return to Table of Contents](<#table of contents>)

---

## Cross References

**Master Design:** [design-0000-master.md](<design-0000-master.md>)

**Related Modules:**
- [ServiceController](<design-0006-servicecontroller.md>) - Invokes installer on first run
- All modules - Depend on successful installation

**Dependencies:**
- Python standard library only (subprocess, shutil, os, pathlib)
- Systemd (system service)

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-11 | William Watson | Initial module design extracted from master |

[Return to Table of Contents](<#table of contents>)

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
