change_info:
  id: change-0013
  title: Redesign installer for venv-based package deployment
  date: 2025-12-03
  author: William Watson
  status: proposed
  priority: critical
  iteration: 1
  coupled_docs:
    issue_ref: issue-0013
    issue_iteration: 1

source:
  type: issue
  reference: issue-0013-installer-venv-incompatibility.md
  description: Installer fails silently when package installed via pip in virtual environment, incompatible with Python packaging deployment workflow

scope:
  summary: Redesign Installer module to support venv-based package deployment with proper systemd service generation
  affected_components:
    - name: Installer
      file_path: src/pi_netconfig/installer.py
      change_type: refactor
  affected_designs:
    - design_ref: design-0000-master_pi-netconfig.md
      sections:
        - "6.1 Installer (FR-001 through FR-007)"
    - design_ref: design-0001-component_installer.md
      sections:
        - "5.1 InstallationDetector class"
        - "5.2 SystemdInstaller class"
        - "6.1 install() function"
  out_of_scope:
    - "Changes to other modules (StateMonitor, ConnectionManager, APManager, WebServer, ServiceController)"
    - "Changes to packaging configuration (pyproject.toml)"
    - "Changes to deployment guide documentation"

rational:
  problem_statement: |
    Current installer designed for script-based deployment, predates Python packaging:
    - Expects script file to copy to /usr/local/bin/pi-netconfig/main.py
    - Generates systemd unit with hardcoded script path
    - Incompatible with pip-installed packages in venv
    - Fails silently (exit code 5) with no error messages
    - Blocks all hardware deployment
  proposed_solution: |
    Redesign installer to detect and support venv-based deployment:
    1. Detect venv execution context using sys.prefix != sys.base_prefix
    2. Extract venv Python path from sys.executable
    3. Remove script copy operation (package in site-packages)
    4. Generate systemd unit executing venv Python with module: {venv_python} -m pi_netconfig.service_controller
    5. Update rollback to remove only service file (no script directory)
    6. Add comprehensive logging for venv detection and paths
  alternatives_considered:
    - option: "Support both script and package modes"
      reason_rejected: "Increases complexity, script mode no longer needed with Python packaging"
    - option: "Install as system-wide package"
      reason_rejected: "Violates Debian PEP 668 externally-managed-environment policy"
    - option: "Use console_scripts entry point"
      reason_rejected: "Adds complexity, module execution simpler for service context"
  benefits:
    - "Aligns with Python packaging standards (pyproject.toml, pip install)"
    - "Compatible with Debian PEP 668 policy requiring venv"
    - "Eliminates script file management complexity"
    - "Enables proper hardware deployment testing"
    - "Simplifies rollback (only service file removal needed)"
  risks:
    - risk: "Venv detection logic failure on edge cases"
      mitigation: "Explicit venv validation, clear error messages if not in venv"
    - risk: "Service startup failure if venv path changes"
      mitigation: "Use absolute paths from sys.executable at install time"

technical_details:
  current_behavior: |
    InstallationDetector.get_current_script_path():
    - Returns Path(__file__).resolve()
    - Returns None when module executed via python -m
    
    SystemdInstaller.copy_application(script_path):
    - Copies script_path to /usr/local/bin/pi-netconfig/main.py
    - Fails when script_path is None
    
    SystemdInstaller.generate_systemd_unit():
    - ExecStart=/usr/bin/python3 /usr/local/bin/pi-netconfig/main.py
    - Hardcoded paths, no venv support
    
    SystemdInstaller.rollback_installation():
    - Removes /usr/local/bin/pi-netconfig directory
    - Removes /etc/systemd/system/pi-netconfig.service
  proposed_behavior: |
    VenvDetector.is_venv() -> bool:
    - Returns sys.prefix != sys.base_prefix
    - True when running in virtual environment
    
    VenvDetector.get_venv_python() -> Path:
    - Returns Path(sys.executable)
    - Absolute path to venv Python interpreter
    
    VenvDetector.validate_package_installed() -> bool:
    - Attempts: import pi_netconfig
    - Returns True if importable, False otherwise
    
    SystemdInstaller.generate_venv_systemd_unit(venv_python: Path) -> str:
    - ExecStart={venv_python} -m pi_netconfig.service_controller
    - Uses absolute venv Python path from detection
    
    SystemdInstaller.rollback_installation():
    - Only removes /etc/systemd/system/pi-netconfig.service
    - No script directory removal (doesn't exist)
    
    install() function:
    - Validates running in venv (VenvDetector.is_venv())
    - Validates package installed (VenvDetector.validate_package_installed())
    - Gets venv Python path
    - Creates directories (/etc/pi-netconfig, /var/log - not /usr/local/bin/pi-netconfig)
    - Generates venv-aware systemd unit
    - Installs unit, enables and starts service
  implementation_approach: |
    1. Add VenvDetector class:
       - is_venv() method using sys.prefix check
       - get_venv_python() method returning sys.executable
       - validate_package_installed() method importing pi_netconfig
    
    2. Refactor SystemdInstaller:
       - Remove copy_application() method
       - Add generate_venv_systemd_unit(venv_python: Path) method
       - Update create_directories() to remove /usr/local/bin/pi-netconfig
       - Update rollback_installation() to remove only service file
    
    3. Update install() function:
       - Add venv validation checks
       - Remove script path detection
       - Call generate_venv_systemd_unit() instead of generate_systemd_unit()
       - Enhanced logging for venv paths and detection
    
    4. Add error handling:
       - Raise clear error if not in venv
       - Raise clear error if package not installed
       - Provide actionable error messages for deployment issues
  code_changes:
    - component: "Installer"
      file: "src/pi_netconfig/installer.py"
      change_summary: "Add VenvDetector class, refactor SystemdInstaller for venv deployment, update install() orchestration"
      functions_affected:
        - "install()"
      classes_affected:
        - "InstallationDetector (remove get_current_script_path)"
        - "SystemdInstaller (remove copy_application, add generate_venv_systemd_unit)"
        - "VenvDetector (new class)"
  data_changes: []
  interface_changes:
    - interface: "install() function"
      change_type: "contract"
      details: "New precondition: Must execute in venv context (sys.prefix != sys.base_prefix)"
      backward_compatible: "no"

dependencies:
  internal: []
  external:
    - library: "sys"
      version_change: "n/a"
      impact: "Use sys.prefix, sys.base_prefix, sys.executable for venv detection"
  required_changes: []

testing_requirements:
  test_approach: |
    Hardware validation on Raspberry Pi required (venv functionality platform-specific):
    
    1. Development unit tests (Mac):
       - Mock sys.prefix, sys.base_prefix for venv detection
       - Mock sys.executable for path extraction
       - Verify systemd unit generation with venv paths
    
    2. Hardware validation tests (Pi):
       - Full deployment workflow per docs/deploy_test-guide.md
       - Verify service file creation with correct ExecStart
       - Verify service starts and detects state
       - Verify rollback removes only service file
  test_cases:
    - scenario: "Venv detection - in venv"
      expected_result: "VenvDetector.is_venv() returns True"
    - scenario: "Venv detection - not in venv"
      expected_result: "VenvDetector.is_venv() returns False"
    - scenario: "Venv Python path extraction"
      expected_result: "Returns absolute path to venv bin/python"
    - scenario: "Package validation - installed"
      expected_result: "validate_package_installed() returns True"
    - scenario: "Package validation - not installed"
      expected_result: "validate_package_installed() returns False"
    - scenario: "Systemd unit generation with venv"
      expected_result: "ExecStart uses absolute venv Python path with -m flag"
    - scenario: "Installation in venv"
      expected_result: "Service file created, service starts, state detected"
    - scenario: "Installation not in venv"
      expected_result: "Clear error message, installation fails gracefully"
    - scenario: "Rollback after failure"
      expected_result: "Only service file removed, venv untouched"
  regression_scope:
    - "All existing unit tests for Installer module"
  validation_criteria:
    - "Service file created at /etc/systemd/system/pi-netconfig.service"
    - "ExecStart references venv Python: /opt/pi-netconfig/venv/bin/python"
    - "ExecStart uses module execution: -m pi_netconfig.service_controller"
    - "Service starts successfully: sudo systemctl start pi-netconfig"
    - "Service detects state: CLIENT or AP_MODE in logs"
    - "Installation fails with clear error if not in venv"

implementation:
  effort_estimate: "4 hours"
  implementation_steps:
    - step: "Create VenvDetector class with is_venv(), get_venv_python(), validate_package_installed()"
      owner: "Claude Code"
    - step: "Refactor SystemdInstaller: remove copy_application(), add generate_venv_systemd_unit()"
      owner: "Claude Code"
    - step: "Update SystemdInstaller.create_directories() to remove /usr/local/bin/pi-netconfig"
      owner: "Claude Code"
    - step: "Update SystemdInstaller.rollback_installation() to remove only service file"
      owner: "Claude Code"
    - step: "Refactor install() function: add venv validation, remove script operations"
      owner: "Claude Code"
    - step: "Add comprehensive logging for venv detection and paths"
      owner: "Claude Code"
    - step: "Update unit tests with mocked sys.prefix/sys.executable"
      owner: "Claude Code"
  rollback_procedure: |
    Git revert to commit before change implementation.
    Installer already non-functional for venv deployment, no regression risk.
  deployment_notes: |
    After implementation:
    1. Build new distribution: python3 -m build
    2. Transfer to Pi: scp dist/*.whl admin@deb1:/tmp/
    3. Install in venv: sudo /opt/pi-netconfig/venv/bin/pip install --upgrade /tmp/pi_netconfig-*.whl
    4. Run installer: sudo /opt/pi-netconfig/venv/bin/python -m pi_netconfig.installer --install --systemd-mode
    5. Verify service: sudo systemctl status pi-netconfig

verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []

traceability:
  design_updates:
    - design_ref: "design-0000-master_pi-netconfig.md"
      sections_updated:
        - "6.1 Installer component description"
      update_date: ""
    - design_ref: "design-0001-installer.md"
      sections_updated:
        - "5.1 InstallationDetector class (remove get_current_script_path)"
        - "5.1.1 VenvDetector class (new)"
        - "5.2 SystemdInstaller class (refactor for venv)"
        - "6.1 install() function (updated orchestration)"
      update_date: ""
  related_changes: []
  related_issues:
    - issue_ref: "issue-0013"
      relationship: "resolves"

notes: |
  Critical deployment blocker. Hardware validation impossible until resolved.
  
  Implementation must maintain thread safety and error logging standards per NFR-007, NFR-008.

version_history:
  - version: "1.0"
    date: "2025-12-03"
    author: "William Watson"
    changes:
      - "Initial change document from issue-0012"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"

