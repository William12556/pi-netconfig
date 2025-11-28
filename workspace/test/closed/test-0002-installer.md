Created: 2025 November 14

# Installer Module Test Specification

```yaml
test_info:
  id: "test-0002"
  title: "Installer Module Unit Tests"
  date: "2025-11-14"
  author: "Domain 1"
  status: "planned"
  type: "unit"
  priority: "high"

source:
  test_target: "installer.py - Self-installation and systemd service setup"
  design_refs:
    - "design-0001-installer.md"
  change_refs: []
  requirement_refs:
    - "FR-001: Detect if systemd service installed"
    - "FR-002: Self-install as systemd service when not installed"
    - "FR-003: Create required directories during installation"
    - "FR-004: Copy to /usr/local/bin/pi-netconfig/"
    - "FR-005: Generate and install systemd unit file"
    - "FR-006: Enable and start systemd service"
    - "FR-007: Verify installation success"

scope:
  description: "Unit tests for installer module covering installation detection, directory creation, file operations, systemd integration, privilege verification, and rollback procedures"
  test_objectives:
    - "Verify service installation detection logic"
    - "Validate privilege checking"
    - "Test directory creation with proper permissions"
    - "Verify application file copying"
    - "Test systemd unit file generation"
    - "Validate systemd command execution"
    - "Test rollback cleanup on failure"
  in_scope:
    - "InstallationDetector class methods"
    - "SystemdInstaller class methods"
    - "install() entry point function"
    - "Exception handling and logging"
  out_scope:
    - "Actual systemd daemon interaction (mocked)"
    - "Filesystem persistence (use tempfile)"
    - "Root privilege escalation testing"
  dependencies:
    - "unittest.mock for subprocess and filesystem mocking"
    - "tempfile for isolated test environments"

test_environment:
  python_version: "3.11+"
  os: "Linux (Debian/Ubuntu)"
  libraries:
    - name: "pytest"
      version: ">=7.0.0"
    - name: "pytest-asyncio"
      version: ">=0.21.0"
  test_framework: "pytest"
  test_data_location: "Generated in test methods"

test_cases:
  - case_id: "TC-001"
    description: "Verify service detection returns True when service file exists"
    category: "positive"
    preconditions:
      - "Mock Path.exists() to return True"
    test_steps:
      - step: "1"
        action: "Call InstallationDetector.is_service_installed()"
    inputs:
      - parameter: "service_path"
        value: "/etc/systemd/system/pi-netconfig.service"
        type: "Path"
    expected_outputs:
      - field: "return_value"
        expected_value: "True"
        validation: "Boolean equality"
    postconditions:
      - "Path.exists() called with correct service path"
    execution:
      status: "not_run"
      executed_date: ""
      executed_by: ""
      actual_result: ""
      pass_fail_criteria: "Returns True"
    defects: []

  - case_id: "TC-002"
    description: "Verify service detection returns False when service file missing"
    category: "positive"
    preconditions:
      - "Mock Path.exists() to return False"
    test_steps:
      - step: "1"
        action: "Call InstallationDetector.is_service_installed()"
    inputs:
      - parameter: "service_path"
        value: "/etc/systemd/system/pi-netconfig.service"
        type: "Path"
    expected_outputs:
      - field: "return_value"
        expected_value: "False"
        validation: "Boolean equality"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-003"
    description: "Verify root privilege check raises PrivilegeError when UID != 0"
    category: "negative"
    preconditions:
      - "Mock os.geteuid() to return 1000 (non-root)"
    test_steps:
      - step: "1"
        action: "Call SystemdInstaller.verify_root_privileges()"
    inputs:
      - parameter: "euid"
        value: "1000"
        type: "int"
    expected_outputs:
      - field: "exception"
        expected_value: "PrivilegeError"
        validation: "Exception type match"
    postconditions:
      - "Error message printed to stderr"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-004"
    description: "Verify root privilege check returns True when UID = 0"
    category: "positive"
    preconditions:
      - "Mock os.geteuid() to return 0 (root)"
    test_steps:
      - step: "1"
        action: "Call SystemdInstaller.verify_root_privileges()"
    inputs:
      - parameter: "euid"
        value: "0"
        type: "int"
    expected_outputs:
      - field: "return_value"
        expected_value: "True"
        validation: "Boolean equality"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-005"
    description: "Verify directory creation creates all required directories"
    category: "positive"
    preconditions:
      - "Use tempfile.TemporaryDirectory for isolated environment"
    test_steps:
      - step: "1"
        action: "Mock directory paths to temp locations"
      - step: "2"
        action: "Call SystemdInstaller.create_directories()"
      - step: "3"
        action: "Verify all directories exist"
    inputs:
      - parameter: "directories"
        value: "['/usr/local/bin/pi-netconfig', '/etc/pi-netconfig', '/var/log']"
        type: "List[str]"
    expected_outputs:
      - field: "directories_exist"
        expected_value: "True for all paths"
        validation: "Path.exists() for each"
      - field: "permissions"
        expected_value: "0o755"
        validation: "os.stat().st_mode check"
    postconditions:
      - "All directories created with 755 permissions"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-006"
    description: "Verify directory creation raises FileSystemError on permission denied"
    category: "negative"
    preconditions:
      - "Mock Path.mkdir() to raise PermissionError"
    test_steps:
      - step: "1"
        action: "Call SystemdInstaller.create_directories()"
    inputs: []
    expected_outputs:
      - field: "exception"
        expected_value: "FileSystemError"
        validation: "Exception type and message"
    postconditions:
      - "Error logged"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-007"
    description: "Verify application copy creates file at destination with 755 permissions"
    category: "positive"
    preconditions:
      - "Source file exists in temp location"
      - "Mock destination path"
    test_steps:
      - step: "1"
        action: "Create source file"
      - step: "2"
        action: "Call SystemdInstaller.copy_application(source_path)"
      - step: "3"
        action: "Verify destination file exists with correct permissions"
    inputs:
      - parameter: "source_path"
        value: "Path to test script"
        type: "Path"
    expected_outputs:
      - field: "destination_exists"
        expected_value: "True"
        validation: "Path.exists()"
      - field: "permissions"
        expected_value: "0o755"
        validation: "os.stat().st_mode"
    postconditions:
      - "File copied successfully"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-008"
    description: "Verify systemd unit generation produces valid unit file content"
    category: "positive"
    preconditions: []
    test_steps:
      - step: "1"
        action: "Call SystemdInstaller.generate_systemd_unit()"
      - step: "2"
        action: "Validate unit file sections present"
    inputs: []
    expected_outputs:
      - field: "unit_content"
        expected_value: "Contains [Unit], [Service], [Install] sections"
        validation: "String content verification"
      - field: "exec_start"
        expected_value: "Contains correct python3 path"
        validation: "String search"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-009"
    description: "Verify systemd unit installation writes file and reloads daemon"
    category: "positive"
    preconditions:
      - "Mock subprocess.run for systemctl daemon-reload"
      - "Use tempfile for unit file path"
    test_steps:
      - step: "1"
        action: "Call SystemdInstaller.install_systemd_unit(unit_content)"
      - step: "2"
        action: "Verify file written"
      - step: "3"
        action: "Verify daemon-reload called"
    inputs:
      - parameter: "unit_content"
        value: "Valid systemd unit file content"
        type: "str"
    expected_outputs:
      - field: "file_exists"
        expected_value: "True"
        validation: "Path.exists()"
      - field: "daemon_reload_called"
        expected_value: "True"
        validation: "subprocess.run call verification"
    postconditions:
      - "systemctl daemon-reload executed"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-010"
    description: "Verify enable and start commands execute successfully"
    category: "positive"
    preconditions:
      - "Mock subprocess.run for systemctl enable/start"
    test_steps:
      - step: "1"
        action: "Call SystemdInstaller.enable_and_start_service()"
      - step: "2"
        action: "Verify systemctl enable called"
      - step: "3"
        action: "Verify systemctl start called"
    inputs: []
    expected_outputs:
      - field: "enable_called"
        expected_value: "True with correct args"
        validation: "subprocess.run call verification"
      - field: "start_called"
        expected_value: "True with correct args"
        validation: "subprocess.run call verification"
    postconditions:
      - "Both commands executed in sequence"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-011"
    description: "Verify systemctl enable failure raises SystemdError"
    category: "negative"
    preconditions:
      - "Mock subprocess.run to raise CalledProcessError on enable"
    test_steps:
      - step: "1"
        action: "Call SystemdInstaller.enable_and_start_service()"
    inputs: []
    expected_outputs:
      - field: "exception"
        expected_value: "SystemdError"
        validation: "Exception type and message"
    postconditions:
      - "Error logged"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-012"
    description: "Verify rollback removes created files and directories"
    category: "positive"
    preconditions:
      - "Create temporary files/directories to represent installation"
    test_steps:
      - step: "1"
        action: "Create test installation artifacts"
      - step: "2"
        action: "Call SystemdInstaller.rollback_installation()"
      - step: "3"
        action: "Verify artifacts removed"
    inputs: []
    expected_outputs:
      - field: "service_file_removed"
        expected_value: "True"
        validation: "not Path.exists()"
      - field: "install_dir_removed"
        expected_value: "True"
        validation: "not Path.exists()"
    postconditions:
      - "All installation artifacts cleaned up"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-013"
    description: "Verify install() returns True when service already installed"
    category: "positive"
    preconditions:
      - "Mock InstallationDetector.is_service_installed() to return True"
    test_steps:
      - step: "1"
        action: "Call install()"
    inputs: []
    expected_outputs:
      - field: "return_value"
        expected_value: "True"
        validation: "Boolean equality"
      - field: "installation_steps_skipped"
        expected_value: "True"
        validation: "Verify create_directories not called"
    postconditions:
      - "Early return, no installation steps executed"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-014"
    description: "Verify install() completes full installation when not installed"
    category: "positive"
    preconditions:
      - "Mock all filesystem and subprocess operations"
      - "Mock is_service_installed() to return False"
      - "Mock verify_root_privileges() to return True"
    test_steps:
      - step: "1"
        action: "Call install()"
      - step: "2"
        action: "Verify all installation steps called in sequence"
    inputs: []
    expected_outputs:
      - field: "return_value"
        expected_value: "True"
        validation: "Boolean equality"
      - field: "installation_sequence"
        expected_value: "All steps executed in order"
        validation: "Mock call verification"
    postconditions:
      - "Service installed and started"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-015"
    description: "Verify install() returns False and triggers rollback on FileSystemError"
    category: "negative"
    preconditions:
      - "Mock create_directories() to raise FileSystemError"
    test_steps:
      - step: "1"
        action: "Call install()"
      - step: "2"
        action: "Verify rollback called"
    inputs: []
    expected_outputs:
      - field: "return_value"
        expected_value: "False"
        validation: "Boolean equality"
      - field: "rollback_called"
        expected_value: "True"
        validation: "Mock call verification"
    postconditions:
      - "Error logged"
    execution:
      status: "not_run"
    defects: []

coverage:
  requirements_covered:
    - requirement_ref: "FR-001"
      test_cases: ["TC-001", "TC-002"]
    - requirement_ref: "FR-002"
      test_cases: ["TC-013", "TC-014"]
    - requirement_ref: "FR-003"
      test_cases: ["TC-005", "TC-006"]
    - requirement_ref: "FR-004"
      test_cases: ["TC-007"]
    - requirement_ref: "FR-005"
      test_cases: ["TC-008", "TC-009"]
    - requirement_ref: "FR-006"
      test_cases: ["TC-010", "TC-011"]
    - requirement_ref: "FR-007"
      test_cases: ["TC-014", "TC-015"]
  code_coverage:
    target: "80%"
    achieved: ""
  untested_areas: []

test_execution_summary:
  total_cases: 15
  passed: 0
  failed: 0
  blocked: 0
  skipped: 0
  pass_rate: ""
  execution_time: ""
  test_cycle: "Initial"

defect_summary:
  total_defects: 0
  critical: 0
  high: 0
  medium: 0
  low: 0
  issues: []

verification:
  verified_date: ""
  verified_by: ""
  verification_notes: ""
  sign_off: ""

traceability:
  requirements:
    - requirement_ref: "FR-001"
      test_cases: ["TC-001", "TC-002"]
    - requirement_ref: "FR-002"
      test_cases: ["TC-013", "TC-014"]
    - requirement_ref: "FR-003"
      test_cases: ["TC-005", "TC-006"]
    - requirement_ref: "FR-004"
      test_cases: ["TC-007"]
    - requirement_ref: "FR-005"
      test_cases: ["TC-008", "TC-009"]
    - requirement_ref: "FR-006"
      test_cases: ["TC-010", "TC-011"]
    - requirement_ref: "FR-007"
      test_cases: ["TC-014", "TC-015"]
  designs:
    - design_ref: "design-0001-installer.md"
      test_cases: ["TC-001" through "TC-015"]
  changes: []

notes: |
  Test implementation uses unittest.mock for subprocess and filesystem operations.
  Temporary directories used to isolate tests from actual filesystem.
  Root privilege tests verify error handling without requiring actual root access.

version_history:
  - version: "1.0"
    date: "2025-11-14"
    author: "Domain 1"
    changes:
      - "Initial test specification covering all installer requirements"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t05_test"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
