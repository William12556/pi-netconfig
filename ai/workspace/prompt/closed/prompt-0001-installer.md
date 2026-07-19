Created: 2025 November 12

# T04 Prompt: Installer Module

```yaml
prompt_info:
  id: "prompt-0001"
  task_type: "code_generation"
  source_ref: "design-0001-installer"
  date: "2025-11-12"
  priority: "high"

mcp_config:
  model: "claude-sonnet-4-20250514"
  temperature: 0.2
  max_tokens: 4096
  system_prompt: |
    Expert Python developer. Generate production-quality code following specifications.
    
    OUTPUT FORMAT REQUIREMENTS:
    - Return code only, no explanations or commentary
    - Include brief integration instructions after code
    - No markdown code blocks unless explicitly requested
    - No conversational text or preamble
    - Domain 1 handles all integration logic

context:
  purpose: "Self-installation mechanism that detects existing systemd service installation and configures the system on first run"
  integration: "Invoked by ServiceController on first application run when systemd service not detected"
  constraints:
    - "Requires root privileges for all operations"
    - "Must work with systemd (standard on Raspbian Bookworm)"
    - "Must handle partial installation failures with rollback"
    - "Single execution model (run once, then exit)"

specification:
  description: "Create installer module that detects systemd service, creates directories, copies application, generates and installs systemd unit file, enables and starts service"
  requirements:
    functional:
      - "Detect if systemd service file exists at /etc/systemd/system/pi-netconfig.service"
      - "Verify root privileges (UID 0)"
      - "Create directories: /usr/local/bin/pi-netconfig/, /etc/pi-netconfig/, /var/log/"
      - "Copy current script to /usr/local/bin/pi-netconfig/main.py"
      - "Generate systemd unit file with proper configuration"
      - "Install unit file and reload systemd daemon"
      - "Enable and start pi-netconfig service"
      - "Rollback partial installation on failure"
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Thread-safe if concurrent access"
        - "Comprehensive error handling with specific exception types"
        - "Debug logging with traceback"
        - "Professional docstrings (Google style)"
        - "Type hints for all functions and methods"
  performance:
    - target: "Installation completion under 30 seconds"
      metric: "time"
    - target: "Clean failure and rollback under 5 seconds"
      metric: "time"

design:
  architecture: "Class-based with separation of detection and installation logic"
  components:
    - name: "InstallationDetector"
      type: "class"
      purpose: "Check for existing systemd service installation"
      interface:
        inputs:
          - name: "None"
            type: "N/A"
            description: "No constructor parameters"
        outputs:
          type: "bool or Path"
          description: "Service installation status or script path"
        raises:
          - "InstallerError - filesystem access failures"
      logic:
        - "Check existence of /etc/systemd/system/pi-netconfig.service"
        - "Determine absolute path of currently executing script"
        - "Return boolean for installation status"
    
    - name: "SystemdInstaller"
      type: "class"
      purpose: "Perform installation steps and systemd configuration"
      interface:
        inputs:
          - name: "None"
            type: "N/A"
            description: "No constructor parameters"
        outputs:
          type: "bool"
          description: "Installation success status"
        raises:
          - "InstallerError - critical failures"
          - "PrivilegeError - insufficient privileges"
          - "FileSystemError - directory/file operation failure"
          - "SystemdError - systemd command execution failure"
      logic:
        - "Verify root privileges (os.geteuid() == 0)"
        - "Create required directories with proper permissions (755)"
        - "Copy application script to installation location"
        - "Generate systemd unit file content in-memory"
        - "Write unit file and execute systemctl daemon-reload"
        - "Enable and start service via systemctl"
        - "On failure: execute rollback to remove created files/directories"
    
    - name: "install"
      type: "function"
      purpose: "Main installation entry point"
      interface:
        inputs:
          - name: "None"
            type: "N/A"
            description: "No parameters"
        outputs:
          type: "bool"
          description: "True if installation successful, False otherwise"
        raises:
          - "InstallerError - on critical failures"
      logic:
        - "Verify root privileges - exit with error if not root"
        - "Check existing installation - skip if service already exists"
        - "Execute installation steps via SystemdInstaller"
        - "Rollback on any failure"
        - "Return success/failure status"
  
  dependencies:
    internal: []
    external:
      - "subprocess - for systemctl commands"
      - "shutil - for file copy operations"
      - "os - for privilege checking and directory creation"
      - "pathlib - for path operations"

data_schema:
  entities:
    - name: "SystemdUnitFile"
      attributes:
        - name: "content"
          type: "str"
          constraints: "Valid systemd unit file format"
      validation:
        - "Must include [Unit], [Service], [Install] sections"
        - "ExecStart must point to /usr/local/bin/pi-netconfig/main.py"
        - "Restart policy must be on-failure"
        - "User must be root"

error_handling:
  strategy: "Raise specific exception types for different failure categories, with rollback on any failure"
  exceptions:
    - exception: "InstallerError"
      condition: "Base exception for installer operations"
      handling: "Log with traceback and trigger rollback"
    - exception: "PrivilegeError"
      condition: "os.geteuid() != 0"
      handling: "Print error message 'Installation requires root privileges. Run with sudo.' and exit with code 1"
    - exception: "FileSystemError"
      condition: "Directory creation or file copy fails"
      handling: "Log full traceback, trigger rollback"
    - exception: "SystemdError"
      condition: "systemctl command returns non-zero exit code"
      handling: "Log command, stderr, exit code, trigger rollback"
  logging:
    level: "DEBUG, INFO, WARNING, ERROR, CRITICAL as appropriate"
    format: "Use logging module with logger name 'Installer'"

testing:
  unit_tests:
    - scenario: "Detect existing service file"
      expected: "is_service_installed() returns True"
    - scenario: "No existing service file"
      expected: "is_service_installed() returns False"
    - scenario: "Root privilege check succeeds"
      expected: "verify_root_privileges() returns True"
    - scenario: "Non-root privilege check"
      expected: "verify_root_privileges() returns False"
    - scenario: "Directory creation succeeds"
      expected: "Directories exist with 755 permissions"
    - scenario: "Systemd unit generation"
      expected: "Valid unit file content returned"
  edge_cases:
    - "Partial installation (some directories exist)"
    - "Service file exists but service not enabled"
    - "Insufficient disk space"
    - "systemctl command not available"
  validation:
    - "All created paths exist after successful installation"
    - "Rollback removes all created artifacts on failure"
    - "Service is enabled and active after successful installation"

output_format:
  structure: "code_only"
  integration_notes: "brief"
  constraints:
    - "No explanatory prose"
    - "No conversational preamble"
    - "Integration instructions: 2-3 lines maximum"
    - "Domain 1 performs integration; Domain 2 provides code only"

deliverable:
  format_requirements:
    - "Return raw Python code without markdown blocks"
    - "Add integration notes after code (max 3 lines)"
    - "No additional commentary or explanations"
    - "Format: <code>\\n\\nINTEGRATION: <brief instructions>"
  files:
    - path: "src/installer.py"
      content: "Complete installer module implementation"
  documentation:
    - "Integration: Import install() function from installer module. Call from ServiceController when service not detected. Expects root privileges."

success_criteria:
  - "Service file detected correctly when exists"
  - "Root privilege verification accurate"
  - "All directories created with correct permissions"
  - "Application copied to correct location"
  - "Systemd unit file generated and installed correctly"
  - "Service enabled and started successfully"
  - "Rollback removes all created artifacts on failure"
  - "No unhandled exceptions"

notes: "This is the first module to be generated. It has no internal dependencies on other project modules. Uses only Python stdlib."

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

## Design Specification

### Module: Installer

**Purpose:** Self-installation mechanism that detects existing systemd service installation and configures the system on first run.

**Key Components:**

1. **InstallationDetector Class**
   - `is_service_installed() -> bool`: Checks /etc/systemd/system/pi-netconfig.service
   - `get_current_script_path() -> Path`: Returns absolute path of executing script

2. **SystemdInstaller Class**
   - `verify_root_privileges() -> bool`: Checks os.geteuid() == 0
   - `create_directories() -> None`: Creates /usr/local/bin/pi-netconfig/, /etc/pi-netconfig/, /var/log/
   - `copy_application() -> None`: Copies script to /usr/local/bin/pi-netconfig/main.py
   - `generate_systemd_unit() -> str`: Returns systemd unit file content
   - `install_systemd_unit(unit_content: str) -> None`: Writes unit file, executes systemctl daemon-reload
   - `enable_and_start_service() -> None`: Executes systemctl enable and start
   - `rollback_installation() -> None`: Best-effort cleanup of created files/directories

3. **install() Function**
   - Main entry point
   - Returns bool (success/failure)
   - Coordinates InstallationDetector and SystemdInstaller

**Systemd Unit Template:**
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

**Exception Hierarchy:**
- InstallerError (base)
  - PrivilegeError
  - FileSystemError
  - SystemdError

**Error Handling:**
- Insufficient privileges: Print message, exit code 1
- Directory creation failure: Log traceback, trigger rollback, raise FileSystemError
- Copy failure: Log details, trigger rollback, raise FileSystemError
- systemctl failure: Log command/stderr/exit code, trigger rollback, raise SystemdError
- Rollback failures: Log errors but continue (best-effort)

**Logging Levels:**
- DEBUG: Each installation step, directory paths, file operations, systemctl commands
- INFO: Installation start, service detection result, installation success
- WARNING: Rollback initiated, cleanup failures
- ERROR: Installation step failures, exception details with traceback
- CRITICAL: Installation failed after rollback, systemd integration failure

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
