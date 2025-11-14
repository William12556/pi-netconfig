Created: 2025 November 14

# ServiceController Module Test Specification

```yaml
test_info:
  id: "test-0006"
  title: "ServiceController (main.py) Unit Tests"
  date: "2025-11-14"
  author: "Domain 1"
  status: "planned"
  type: "unit"
  priority: "critical"

source:
  test_target: "main.py - Application entry point and service lifecycle management"
  design_refs:
    - "design-0006-servicecontroller.md"
  change_refs: []
  requirement_refs:
    - "FR-023: Shutdown components gracefully on service stop"
    - "FR-070: Detect execution mode (bootstrap/service/manual)"
    - "FR-071: Configure logging to /var/log/pi-netconfig.log"
    - "FR-072: Register SIGTERM and SIGINT signal handlers"
    - "FR-073: Perform graceful shutdown on signal receipt"
    - "FR-074: Verify root privileges before service operations"

scope:
  description: "Unit tests for service controller covering execution mode detection, logging configuration, signal handling, graceful shutdown, and main entry point"
  test_objectives:
    - "Verify execution mode detection logic"
    - "Test logging configuration"
    - "Validate signal handler registration"
    - "Test graceful shutdown sequence"
    - "Verify privilege checking"
    - "Test main() entry point flow"
  in_scope:
    - "detect_execution_mode()"
    - "verify_root_privileges()"
    - "configure_logging()"
    - "signal_handler()"
    - "register_signal_handlers()"
    - "graceful_shutdown()"
    - "run_service()"
    - "main()"
  out_scope:
    - "Actual StateMonitor implementation (mocked)"
    - "Real signal delivery (mocked)"
  dependencies:
    - "pytest-asyncio for async tests"
    - "unittest.mock for comprehensive mocking"

test_environment:
  python_version: "3.11+"
  os: "Linux"
  libraries:
    - name: "pytest"
      version: ">=7.0.0"
    - name: "pytest-asyncio"
      version: ">=0.21.0"
  test_framework: "pytest with asyncio support"

test_cases:
  - case_id: "TC-001"
    description: "Verify detect_execution_mode returns 'bootstrap' when service not installed"
    category: "positive"
    preconditions:
      - "Mock InstallationDetector.is_service_installed() returns False"
    test_steps:
      - step: "1"
        action: "Call detect_execution_mode()"
    expected_outputs:
      - field: "return_value"
        expected_value: "bootstrap"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-002"
    description: "Verify detect_execution_mode returns 'service' when under systemd"
    category: "positive"
    preconditions:
      - "Mock is_service_installed() returns True"
      - "Mock INVOCATION_ID environment variable exists"
    test_steps:
      - step: "1"
        action: "Call detect_execution_mode()"
    expected_outputs:
      - field: "return_value"
        expected_value: "service"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-003"
    description: "Verify detect_execution_mode returns 'manual' when installed but not systemd"
    category: "positive"
    preconditions:
      - "Mock is_service_installed() returns True"
      - "Mock INVOCATION_ID not present"
    test_steps:
      - step: "1"
        action: "Call detect_execution_mode()"
    expected_outputs:
      - field: "return_value"
        expected_value: "manual"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-004"
    description: "Verify verify_root_privileges returns True for UID 0"
    category: "positive"
    preconditions:
      - "Mock os.geteuid() returns 0"
    test_steps:
      - step: "1"
        action: "Call verify_root_privileges()"
    expected_outputs:
      - field: "return_value"
        expected_value: "True"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-005"
    description: "Verify verify_root_privileges returns False for non-root UID"
    category: "positive"
    preconditions:
      - "Mock os.geteuid() returns 1000"
    test_steps:
      - step: "1"
        action: "Call verify_root_privileges()"
    expected_outputs:
      - field: "return_value"
        expected_value: "False"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-006"
    description: "Verify configure_logging creates file handler"
    category: "positive"
    preconditions:
      - "Use tempfile for log path"
    test_steps:
      - step: "1"
        action: "Call configure_logging('service')"
      - step: "2"
        action: "Verify file handler added"
    expected_outputs:
      - field: "file_handler_present"
        expected_value: "True"
      - field: "console_handler_present"
        expected_value: "False for service mode"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-007"
    description: "Verify configure_logging adds console handler in manual mode"
    category: "positive"
    preconditions:
      - "Use tempfile for log path"
    test_steps:
      - step: "1"
        action: "Call configure_logging('manual')"
    expected_outputs:
      - field: "file_handler_present"
        expected_value: "True"
      - field: "console_handler_present"
        expected_value: "True"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-008"
    description: "Verify configure_logging raises LoggingConfigurationError on permission denied"
    category: "negative"
    preconditions:
      - "Mock file handler creation to raise PermissionError"
    test_steps:
      - step: "1"
        action: "Call configure_logging('service')"
    expected_outputs:
      - field: "exception_type"
        expected_value: "LoggingConfigurationError"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-009"
    description: "Verify signal_handler sets shutdown_event"
    category: "positive"
    preconditions:
      - "Create shutdown_event"
      - "Mock signal"
    test_steps:
      - step: "1"
        action: "Call signal_handler(SIGTERM, frame)"
      - step: "2"
        action: "Verify shutdown_event.is_set()"
    expected_outputs:
      - field: "event_set"
        expected_value: "True"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-010"
    description: "Verify register_signal_handlers registers SIGTERM and SIGINT"
    category: "positive"
    preconditions:
      - "Mock signal.signal()"
    test_steps:
      - step: "1"
        action: "Call register_signal_handlers()"
    expected_outputs:
      - field: "sigterm_registered"
        expected_value: "True"
      - field: "sigint_registered"
        expected_value: "True"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-011"
    description: "Verify graceful_shutdown calls StateMonitor.shutdown()"
    category: "positive"
    preconditions:
      - "Mock StateMonitor instance"
    test_steps:
      - step: "1"
        action: "Call graceful_shutdown()"
    expected_outputs:
      - field: "shutdown_called"
        expected_value: "True"
      - field: "completion_logged"
        expected_value: "True"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-012"
    description: "Verify graceful_shutdown handles timeout gracefully"
    category: "positive"
    preconditions:
      - "Mock StateMonitor.shutdown() to timeout"
    test_steps:
      - step: "1"
        action: "Call graceful_shutdown()"
    expected_outputs:
      - field: "timeout_logged"
        expected_value: "True"
      - field: "no_exception_raised"
        expected_value: "True"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-013"
    description: "Verify run_service creates StateMonitor and waits for shutdown"
    category: "positive"
    preconditions:
      - "Mock StateMonitor"
      - "Mock asyncio.Event"
    test_steps:
      - step: "1"
        action: "Call run_service()"
      - step: "2"
        action: "Set shutdown_event"
    expected_outputs:
      - field: "state_monitor_created"
        expected_value: "True"
      - field: "monitor_task_started"
        expected_value: "True"
      - field: "graceful_shutdown_called"
        expected_value: "True"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-014"
    description: "Verify main() calls install() in bootstrap mode"
    category: "positive"
    preconditions:
      - "Mock detect_execution_mode() returns 'bootstrap'"
      - "Mock verify_root_privileges() returns True"
      - "Mock install() returns True"
    test_steps:
      - step: "1"
        action: "Call main()"
    expected_outputs:
      - field: "return_code"
        expected_value: "0"
      - field: "install_called"
        expected_value: "True"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-015"
    description: "Verify main() returns 1 when install() fails"
    category: "negative"
    preconditions:
      - "Mock detect_execution_mode() returns 'bootstrap'"
      - "Mock install() returns False"
    test_steps:
      - step: "1"
        action: "Call main()"
    expected_outputs:
      - field: "return_code"
        expected_value: "1"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-016"
    description: "Verify main() runs service in service mode"
    category: "positive"
    preconditions:
      - "Mock detect_execution_mode() returns 'service'"
      - "Mock all service components"
    test_steps:
      - step: "1"
        action: "Call main()"
    expected_outputs:
      - field: "logging_configured"
        expected_value: "True"
      - field: "signal_handlers_registered"
        expected_value: "True"
      - field: "run_service_called"
        expected_value: "True"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-017"
    description: "Verify main() returns 1 without root privileges"
    category: "negative"
    preconditions:
      - "Mock verify_root_privileges() returns False"
    test_steps:
      - step: "1"
        action: "Call main()"
    expected_outputs:
      - field: "return_code"
        expected_value: "1"
      - field: "error_logged"
        expected_value: "True"
    execution:
      status: "not_run"
    defects: []

coverage:
  requirements_covered:
    - requirement_ref: "FR-023"
      test_cases: ["TC-011", "TC-012"]
    - requirement_ref: "FR-070"
      test_cases: ["TC-001", "TC-002", "TC-003"]
    - requirement_ref: "FR-071"
      test_cases: ["TC-006", "TC-007", "TC-008"]
    - requirement_ref: "FR-072"
      test_cases: ["TC-010"]
    - requirement_ref: "FR-073"
      test_cases: ["TC-009", "TC-011"]
    - requirement_ref: "FR-074"
      test_cases: ["TC-004", "TC-005", "TC-017"]
  code_coverage:
    target: "80%"
    achieved: ""

test_execution_summary:
  total_cases: 17
  passed: 0
  failed: 0

notes: |
  Tests use comprehensive mocking for all dependencies.
  Async tests require pytest-asyncio.
  Signal handling tested via mock, not actual signals.

version_history:
  - version: "1.0"
    date: "2025-11-14"
    author: "Domain 1"
    changes:
      - "Initial test specification"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t05_test"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
