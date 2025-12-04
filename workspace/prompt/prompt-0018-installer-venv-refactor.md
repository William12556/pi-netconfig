---
prompt_info:
  id: prompt-0018
  task_type: code_generation
  source_ref: change-0013-installer-venv-deployment.md
  date: 2025-12-03
  priority: critical
  iteration: 1
  coupled_docs:
    change_ref: change-0013
    change_iteration: 1

context:
  purpose: Redesign Installer module to support venv-based package deployment instead of script-based deployment
  integration: Installer invoked by ServiceController when systemd service not detected. Must validate venv context and generate systemd unit executing venv Python with module flag.
  constraints:
    - Must execute within virtual environment
    - Package must be pip-installed in venv
    - No script file copying (package in site-packages)
    - Systemd unit must use absolute venv Python path
    - Maintain thread safety and comprehensive error logging per NFR-007, NFR-008

specification:
  description: Refactor src/pi_netconfig/installer.py to detect venv execution, validate package installation, and generate systemd unit for module execution
  requirements:
    functional:
      - Detect virtual environment using sys.prefix != sys.base_prefix
      - Validate pi_netconfig package importable
      - Extract venv Python path from sys.executable
      - Generate systemd unit with ExecStart using venv Python and -m flag
      - Remove script file copy operations
      - Update rollback to remove only service file
    technical:
      language: Python
      version: "3.9+"
      standards:
        - Thread-safe implementation
        - Comprehensive error handling with PrivilegeError, InstallerError, FileSystemError, SystemdError
        - Debug logging with traceback for all operations
        - Professional docstrings with parameter types and exceptions
  performance:
    - target: Installation completion < 30 seconds
      metric: time

design:
  architecture: Three-class structure - InstallationDetector (service detection), VenvDetector (venv validation), SystemdInstaller (installation execution)
  components:
    - name: InstallationDetector
      type: class
      purpose: Check for existing systemd service installation
      interface:
        inputs: []
        outputs:
          type: bool
          description: True if service file exists
        raises: []
      logic:
        - Check existence of /etc/systemd/system/pi-netconfig.service
        - Return True if exists, False otherwise
        - No exceptions raised

    - name: VenvDetector
      type: class
      purpose: Validate virtual environment execution context and package installation
      interface:
        inputs: []
        outputs:
          type: bool/Path
          description: Venv validation result or Python path
        raises: []
      logic:
        - is_venv() method - Return sys.prefix != sys.base_prefix
        - get_venv_python() method - Return Path(sys.executable)
        - validate_package_installed() method - Try import pi_netconfig, return success boolean
        - No exceptions raised (return False on failure)

    - name: SystemdInstaller
      type: class
      purpose: Execute installation steps with venv-aware systemd unit generation
      interface:
        inputs:
          - name: venv_python
            type: Path
            description: Absolute path to venv Python interpreter
        outputs:
          type: None
          description: Side effects - creates directories, service file
        raises:
          - PrivilegeError
          - FileSystemError
          - SystemdError
      logic:
        - verify_root_privileges() - Check os.geteuid() == 0, raise PrivilegeError if not
        - create_directories() - Create /etc/pi-netconfig/, /var/log/ with 755 permissions
        - generate_venv_systemd_unit(venv_python) - Return unit content with ExecStart={venv_python} -m pi_netconfig.service_controller
        - install_systemd_unit(unit_content) - Write to /etc/systemd/system/pi-netconfig.service, execute systemctl daemon-reload
        - enable_and_start_service() - Execute systemctl enable, systemctl start
        - rollback_installation() - Remove /etc/systemd/system/pi-netconfig.service only (best-effort, no exceptions)

    - name: install
      type: function
      purpose: Main installation orchestration with venv validation
      interface:
        inputs: []
        outputs:
          type: bool
          description: Installation success/failure
        raises:
          - PrivilegeError
          - InstallerError
      logic:
        - Check if service already installed (skip if exists)
        - Verify root privileges
        - Validate venv context (raise InstallerError if sys.prefix == sys.base_prefix)
        - Validate package installed (raise InstallerError if import fails)
        - Get venv Python path
        - Create directories
        - Generate venv-aware systemd unit
        - Install unit and reload daemon
        - Enable and start service
        - On failure - rollback and return False
        - Return True on success

  dependencies:
    internal: []
    external:
      - subprocess (systemctl commands)
      - sys (prefix, base_prefix, executable)
      - os (geteuid, makedirs, chmod)
      - pathlib (Path operations)

data_schema:
  entities:
    - name: systemd_unit_template
      attributes:
        - name: ExecStart
          type: string
          constraints: Must use absolute venv Python path with -m flag
        - name: WorkingDirectory
          type: string
          constraints: Optional, can be omitted
      validation:
        - venv_python must be absolute path
        - Must include -m pi_netconfig.service_controller

error_handling:
  strategy: Hierarchical exceptions with rollback on failure
  exceptions:
    - exception: PrivilegeError
      condition: os.geteuid() != 0
      handling: Print error to stderr, raise exception, no rollback needed
    - exception: InstallerError (venv)
      condition: sys.prefix == sys.base_prefix
      handling: Print error message about venv requirement, raise exception
    - exception: InstallerError (package)
      condition: import pi_netconfig fails
      handling: Print error message about package installation, raise exception
    - exception: FileSystemError
      condition: Directory creation fails
      handling: Log with traceback, trigger rollback, raise exception
    - exception: SystemdError
      condition: systemctl commands fail
      handling: Log stderr output, trigger rollback, raise exception
  logging:
    level: DEBUG
    format: "timestamp level logger message with traceback on errors"

testing:
  unit_tests:
    - scenario: VenvDetector.is_venv() in venv
      expected: Returns True
    - scenario: VenvDetector.is_venv() not in venv
      expected: Returns False
    - scenario: VenvDetector.get_venv_python()
      expected: Returns absolute path to Python interpreter
    - scenario: VenvDetector.validate_package_installed() when installed
      expected: Returns True
    - scenario: VenvDetector.validate_package_installed() when not installed
      expected: Returns False
    - scenario: SystemdInstaller.generate_venv_systemd_unit()
      expected: Returns unit content with venv Python path and -m flag
    - scenario: install() in venv with package installed
      expected: Creates service file, returns True
    - scenario: install() not in venv
      expected: Raises InstallerError with venv message
    - scenario: install() package not installed
      expected: Raises InstallerError with package message
  edge_cases:
    - Service file already exists (skip installation)
    - Not running as root (PrivilegeError before venv checks)
    - systemctl daemon-reload fails (SystemdError, rollback)
  validation:
    - Service file created at /etc/systemd/system/pi-netconfig.service
    - ExecStart line contains absolute venv Python path
    - ExecStart includes -m pi_netconfig.service_controller
    - Rollback removes only service file

deliverable:
  format_requirements:
    - Save generated code directly to src/pi_netconfig/installer.py (overwrite existing)
    - Maintain existing exception class definitions
    - Update all class and function implementations
    - Create completion document in workspace/prompt/
  files:
    - path: src/pi_netconfig/installer.py
      content: "Complete refactored installer module"
  completion_document:
    path: workspace/prompt/prompt-0013-completion.md
    required_fields:
      - "timestamp: ISO format"
      - "files_created: [src/pi_netconfig/installer.py]"
      - "status: SUCCESS or FAILURE"
      - "notes: Any warnings or implementation notes"

success_criteria:
  - VenvDetector class implemented with is_venv(), get_venv_python(), validate_package_installed()
  - SystemdInstaller.generate_venv_systemd_unit() generates correct ExecStart
  - SystemdInstaller.create_directories() creates only /etc/pi-netconfig/ and /var/log/
  - SystemdInstaller.rollback_installation() removes only service file
  - install() function validates venv and package before proceeding
  - All methods include comprehensive logging
  - Thread safety maintained
  - Code passes existing unit tests (or tests updated accordingly)

notes: |
  CRITICAL: This is a deployment blocker. Hardware validation cannot proceed until installer works with venv-based package deployment.
  
  The current implementation tries to copy script files which don't exist when package is pip-installed in venv. The systemd unit must execute the venv Python with module flag instead of a script path.
  
  Remove all references to:
  - InstallationDetector.get_current_script_path()
  - SystemdInstaller.copy_application()
  - /usr/local/bin/pi-netconfig/ directory creation
  
  Add venv validation before any installation steps to fail fast with clear error messages.

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
