---
document_info:
  id: "design-0001"
  type: "component_design"
  iteration: 2
  tier: 3
  domain: "installer"
  status: "active"
  coupled_docs:
    change_refs:
      - "change-0012"
    prompt_refs: []
---

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
**Version:** 2.0.0  
**Date:** 2025-12-03  
**Author:** William Watson  
**Master Design:** [design-0000-master.md](<design-0000-master.md>)  
**Change:** [change-0012-installer-venv-deployment.md](<../change/change-0012-installer-venv-deployment.md>)

[Return to Table of Contents](<#table of contents>)

---

## Module Overview

**Purpose:** Self-installation mechanism that detects existing systemd service installation and configures the system for venv-based package deployment.

**Responsibilities:**
- Detect if systemd service already installed
- Validate venv execution context
- Validate package installation
- Create required directories
- Generate venv-aware systemd unit file
- Enable and start systemd service
- Verify installation success

**Context:** Invoked by ServiceController when systemd service not detected. Must execute within virtual environment where pi_netconfig package is installed.

[Return to Table of Contents](<#table of contents>)

---

## Scope

**In Scope:**
- Service file detection at `/etc/systemd/system/pi-netconfig.service`
- Virtual environment validation (sys.prefix != sys.base_prefix)
- Package installation validation (import pi_netconfig)
- Venv Python path extraction (sys.executable)
- Directory creation: `/etc/pi-netconfig/`, `/var/log/`
- Venv-aware systemd unit file generation
- Systemd service enablement and activation
- Root privilege verification
- Installation rollback on failure

**Out of Scope:**
- Application updates or upgrades
- Service removal/uninstallation
- Configuration file management (handled by ConnectionManager)
- Runtime operation (handled by other modules)
- Script file copying (package installed via pip in site-packages)

[Return to Table of Contents](<#table of contents>)

---

## Design Constraints

**Technical:**
- Requires root privileges for all operations
- Must execute within virtual environment
- Must work with systemd (standard on Raspbian/Debian)
- Must handle partial installation failures
- Single execution model (run once, then exit)
- Must support Python package deployment (pip install)

**Implementation:**
- Language: Python 3.9+
- External libraries: subprocess, sys, os, pathlib (stdlib only)
- Standards: PEP 8 compliance, type hints, Debian PEP 668 compliance

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
- No exceptions (returns False on access error)

### VenvDetector Class

**Purpose:** Validate virtual environment execution context and package installation

**Key Methods:**

```python
def is_venv() -> bool
```
- Checks if running in virtual environment
- Returns: sys.prefix != sys.base_prefix
- No exceptions

```python
def get_venv_python() -> Path
```
- Returns absolute path to venv Python interpreter
- Returns: Path(sys.executable)
- No exceptions

```python
def validate_package_installed() -> bool
```
- Validates pi_netconfig package importable
- Attempts: import pi_netconfig
- Returns True if import succeeds, False otherwise
- No exceptions

### SystemdInstaller Class

**Purpose:** Perform installation steps and systemd configuration

**Key Methods:**

```python
def verify_root_privileges() -> bool
```
- Checks effective user ID == 0
- Returns True if running as root
- Raises: PrivilegeError if not root

```python
def create_directories() -> None
```
- Creates: `/etc/pi-netconfig/`, `/var/log/`
- Sets proper permissions (755 for directories)
- Raises: FileSystemError on creation failure

```python
def generate_venv_systemd_unit(venv_python: Path) -> str
```
- Returns systemd unit file content as string
- Template includes:
  - `[Unit]` section with description and network dependency
  - `[Service]` section with ExecStart using venv Python and module execution
  - ExecStart format: {venv_python} -m pi_netconfig.service_controller
  - `[Install]` section with WantedBy=multi-user.target
- Parameters: venv_python - Absolute path to venv Python interpreter
- No exceptions

```python
def install_systemd_unit(unit_content: str) -> None
```
- Writes unit file to `/etc/systemd/system/pi-netconfig.service`
- Executes `systemctl daemon-reload`
- Raises: SystemdError on write or systemctl failure

```python
def enable_and_start_service() -> None
```
- Executes `systemctl enable pi-netconfig`
- Executes `systemctl start pi-netconfig`
- Raises: SystemdError on systemctl command failure

```python
def rollback_installation() -> None
```
- Removes systemd service file only
- Package remains in venv (managed by pip)
- Best-effort cleanup (does not raise exceptions)
- Logs cleanup actions

**Processing Logic:**

1. Verify root privileges → raise PrivilegeError if not root
2. Check if service already installed → return True if exists
3. Validate venv context → raise InstallerError if not in venv
4. Validate package installed → raise InstallerError if not importable
5. Get venv Python path from sys.executable
6. Create required directories
7. Generate venv-aware systemd unit file with extracted Python path
8. Install unit file and reload systemd
9. Enable and start service
10. On any failure: rollback partial installation
11. Return True on success, False on failure

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
ExecStart={venv_python_path} -m pi_netconfig.service_controller
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
User=root

[Install]
WantedBy=multi-user.target
```

**Template Variables:**
- `{venv_python_path}`: Absolute path to venv Python interpreter from sys.executable
- Example: `/opt/pi-netconfig/venv/bin/python`

### Installation Paths

**Application:**
- Location: Venv site-packages (managed by pip)
- Example: `/opt/pi-netconfig/venv/lib/python3.11/site-packages/pi_netconfig/`
- No file copying performed by installer

**Venv Python:**
- Detected at runtime via sys.executable
- Example: `/opt/pi-netconfig/venv/bin/python`
- Used in systemd ExecStart

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
def install() -> bool
```
**Purpose:** Main installation entry point  
**Parameters:** None  
**Returns:** True if installation successful, False otherwise  
**Raises:** 
- PrivilegeError if not running as root
- InstallerError if not in venv or package not installed

**Processing:**
1. Verify root privileges
2. Check existing installation (skip if exists)
3. Validate venv context
4. Validate package installation
5. Extract venv Python path
6. Execute installation steps
7. Rollback on failure
8. Return success/failure status

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
- Handling: Print error message to stderr, raise PrivilegeError
- Message: "Installation requires root privileges. Run with sudo."

**Not in Virtual Environment:**
- Condition: `sys.prefix == sys.base_prefix`
- Handling: Print error message to stderr, raise InstallerError
- Message: "Installer must execute within virtual environment. Install package with pip in venv."

**Package Not Installed:**
- Condition: `import pi_netconfig` raises ImportError
- Handling: Print error message to stderr, raise InstallerError
- Message: "Package pi_netconfig not installed. Run: pip install pi_netconfig"

**Directory Creation Fails:**
- Condition: `os.makedirs()` raises exception
- Handling: Raise FileSystemError, trigger rollback
- Log: Full traceback with path details

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
- Venv detection results
- Python path extraction
- Systemctl commands executed

**Level: INFO**
- Installation start
- Service detection result
- Venv validation success
- Installation success

**Level: WARNING**
- Rollback initiated
- Cleanup operation failures

**Level: ERROR**
- Installation step failures
- Venv validation failures
- Exception details with traceback

**Level: CRITICAL**
- Installation failed after rollback
- Systemd integration failure

[Return to Table of Contents](<#table of contents>)

---

## Cross References

**Master Design:** [design-0000-master.md](<design-0000-master.md>)

**Changes:** [change-0012-installer-venv-deployment.md](<../change/change-0012-installer-venv-deployment.md>)

**Related Modules:**
- [ServiceController](<design-0006-servicecontroller.md>) - Invokes installer on first run
- All modules - Depend on successful installation

**Dependencies:**
- Python standard library only (subprocess, sys, os, pathlib)
- Systemd (system service)

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0.0 | 2025-12-03 | William Watson | Redesigned for venv-based package deployment (change-0012): Added VenvDetector class, removed script copy operations, updated systemd unit for module execution |
| 1.0.0 | 2025-11-11 | William Watson | Initial module design extracted from master |

[Return to Table of Contents](<#table of contents>)

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
