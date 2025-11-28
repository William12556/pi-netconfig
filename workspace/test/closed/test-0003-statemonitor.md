Created: 2025 November 14

# StateMonitor Module Test Specification

```yaml
test_info:
  id: "test-0003"
  title: "StateMonitor Module Unit Tests"
  date: "2025-11-14"
  author: "Domain 1"
  status: "planned"
  type: "unit"
  priority: "critical"

source:
  test_target: "statemonitor.py - State machine and operational mode transitions"
  design_refs:
    - "design-0002-statemonitor.md"
  change_refs: []
  requirement_refs:
    - "FR-010: Check WiFi connection every 30 seconds"
    - "FR-011: Detect connection loss within 10 seconds of boot"
    - "FR-013: Transition to AP mode after 3 failed checks"
    - "FR-020: Implement three operational states"
    - "FR-021: Coordinate state transitions"
    - "FR-022: Initialize components on transitions"
    - "FR-045: Activate AP within 15 seconds of failed connection"

scope:
  description: "Unit tests for state machine covering state transitions, connection monitoring, component coordination, and graceful shutdown"
  test_objectives:
    - "Verify correct state transitions based on connection status"
    - "Validate 30-second monitoring interval"
    - "Test failure count accumulation and reset logic"
    - "Verify component initialization on state changes"
    - "Test graceful shutdown sequence"
    - "Validate error recovery mechanisms"
  in_scope:
    - "StateMachine class and all methods"
    - "SystemState enum"
    - "State transition logic"
    - "Component coordination"
    - "Exception handling"
  out_scope:
    - "Actual connection manager/AP manager/webserver implementations"
    - "Real network operations (all mocked)"
  dependencies:
    - "pytest-asyncio for async test support"
    - "unittest.mock for component mocking"

test_environment:
  python_version: "3.11+"
  os: "Linux"
  libraries:
    - name: "pytest"
      version: ">=7.0.0"
    - name: "pytest-asyncio"
      version: ">=0.21.0"
  test_framework: "pytest with asyncio support"
  test_data_location: "N/A - behavior testing"

test_cases:
  - case_id: "TC-001"
    description: "Verify state machine initializes in CHECKING state"
    category: "positive"
    preconditions:
      - "Mock component instances created"
    test_steps:
      - step: "1"
        action: "Create StateMachine instance"
    inputs: []
    expected_outputs:
      - field: "current_state"
        expected_value: "SystemState.CHECKING"
        validation: "Enum equality"
      - field: "failure_count"
        expected_value: "0"
        validation: "Integer equality"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-002"
    description: "Verify successful connection check transitions to CLIENT mode"
    category: "positive"
    preconditions:
      - "State machine in CHECKING state"
      - "Mock connection_manager.test_connection() returns True"
    test_steps:
      - step: "1"
        action: "Call check_connection()"
      - step: "2"
        action: "Verify transition_to_client() called"
    inputs: []
    expected_outputs:
      - field: "current_state"
        expected_value: "SystemState.CLIENT"
        validation: "State equality"
      - field: "failure_count"
        expected_value: "0"
        validation: "Counter reset"
    postconditions:
      - "AP manager deactivated if was in AP mode"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-003"
    description: "Verify 3 consecutive failures trigger AP_MODE transition"
    category: "positive"
    preconditions:
      - "Mock connection_manager.test_connection() returns False"
    test_steps:
      - step: "1"
        action: "Run monitoring loop 3 iterations"
      - step: "2"
        action: "Verify failure_count increments to 3"
      - step: "3"
        action: "Verify transition_to_ap_mode() called"
    inputs: []
    expected_outputs:
      - field: "failure_count"
        expected_value: "3"
        validation: "Integer equality"
      - field: "current_state"
        expected_value: "SystemState.AP_MODE"
        validation: "State equality"
    postconditions:
      - "AP manager activated"
      - "Web server started"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-004"
    description: "Verify failure count resets on successful connection in CLIENT state"
    category: "positive"
    preconditions:
      - "State machine in CLIENT state"
      - "failure_count > 0"
    test_steps:
      - step: "1"
        action: "Mock test_connection() returns True"
      - step: "2"
        action: "Run monitoring iteration"
    inputs: []
    expected_outputs:
      - field: "failure_count"
        expected_value: "0"
        validation: "Counter reset"
      - field: "current_state"
        expected_value: "SystemState.CLIENT"
        validation: "State unchanged"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-005"
    description: "Verify monitoring loop runs every 30 seconds"
    category: "positive"
    preconditions:
      - "Mock asyncio.wait_for with timeout parameter capture"
    test_steps:
      - step: "1"
        action: "Start monitoring loop"
      - step: "2"
        action: "Verify wait_for called with timeout=30.0"
    inputs: []
    expected_outputs:
      - field: "timeout_value"
        expected_value: "30.0"
        validation: "Float equality"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-006"
    description: "Verify transition_to_client deactivates AP when transitioning from AP_MODE"
    category: "positive"
    preconditions:
      - "State machine in AP_MODE"
    test_steps:
      - step: "1"
        action: "Call transition_to_client()"
      - step: "2"
        action: "Verify ap_manager.deactivate_ap() called"
      - step: "3"
        action: "Verify web_server.stop_server() called"
    inputs: []
    expected_outputs:
      - field: "ap_deactivated"
        expected_value: "True"
        validation: "Mock call verification"
      - field: "server_stopped"
        expected_value: "True"
        validation: "Mock call verification"
      - field: "current_state"
        expected_value: "SystemState.CLIENT"
        validation: "State transition"
    postconditions:
      - "failure_count reset to 0"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-007"
    description: "Verify transition_to_ap_mode activates AP and starts web server"
    category: "positive"
    preconditions:
      - "State machine in CHECKING or CLIENT state"
    test_steps:
      - step: "1"
        action: "Call transition_to_ap_mode()"
      - step: "2"
        action: "Verify ap_manager.activate_ap() called"
      - step: "3"
        action: "Verify web_server.start_server() called"
    inputs: []
    expected_outputs:
      - field: "ap_activated"
        expected_value: "True"
        validation: "Mock call verification"
      - field: "server_started"
        expected_value: "True"
        validation: "Mock call verification"
      - field: "current_state"
        expected_value: "SystemState.AP_MODE"
        validation: "State transition"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-008"
    description: "Verify transition failure triggers recovery attempt"
    category: "negative"
    preconditions:
      - "Mock transition_to_ap_mode() to raise exception"
    test_steps:
      - step: "1"
        action: "Attempt transition that fails"
      - step: "2"
        action: "Verify handle_state_transition_failure() called"
    inputs: []
    expected_outputs:
      - field: "recovery_attempted"
        expected_value: "True"
        validation: "Error handler invoked"
      - field: "error_logged"
        expected_value: "True"
        validation: "Log verification"
    postconditions:
      - "State remains consistent"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-009"
    description: "Verify shutdown cancels monitoring task and deactivates components"
    category: "positive"
    preconditions:
      - "State machine running in AP_MODE"
      - "monitoring_task active"
    test_steps:
      - step: "1"
        action: "Call shutdown()"
      - step: "2"
        action: "Verify shutdown_event set"
      - step: "3"
        action: "Verify monitoring_task cancelled"
      - step: "4"
        action: "Verify components deactivated"
    inputs: []
    expected_outputs:
      - field: "shutdown_event_set"
        expected_value: "True"
        validation: "Event status"
      - field: "task_cancelled"
        expected_value: "True"
        validation: "Task state"
      - field: "ap_deactivated"
        expected_value: "True"
        validation: "Mock call verification"
    postconditions:
      - "Clean shutdown with no hanging resources"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-010"
    description: "Verify monitoring loop handles CancelledError gracefully"
    category: "positive"
    preconditions:
      - "monitoring_task running"
    test_steps:
      - step: "1"
        action: "Cancel monitoring_task"
      - step: "2"
        action: "Verify CancelledError caught and logged"
    inputs: []
    expected_outputs:
      - field: "exception_caught"
        expected_value: "True"
        validation: "No unhandled exception"
      - field: "clean_exit"
        expected_value: "True"
        validation: "Loop terminates cleanly"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-011"
    description: "Verify connection check exception returns False without crashing"
    category: "negative"
    preconditions:
      - "Mock connection_manager.test_connection() to raise exception"
    test_steps:
      - step: "1"
        action: "Call check_connection()"
    inputs: []
    expected_outputs:
      - field: "return_value"
        expected_value: "False"
        validation: "Boolean return"
      - field: "exception_logged"
        expected_value: "True"
        validation: "Warning logged"
    postconditions:
      - "State machine continues operating"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-012"
    description: "Verify transition_to_client raises StateTransitionError on component failure"
    category: "negative"
    preconditions:
      - "Mock ap_manager.deactivate_ap() to raise exception"
    test_steps:
      - step: "1"
        action: "Call transition_to_client() from AP_MODE"
    inputs: []
    expected_outputs:
      - field: "exception_type"
        expected_value: "StateTransitionError"
        validation: "Exception raised"
      - field: "error_logged"
        expected_value: "True"
        validation: "Error logged with traceback"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

coverage:
  requirements_covered:
    - requirement_ref: "FR-010"
      test_cases: ["TC-005"]
    - requirement_ref: "FR-011"
      test_cases: ["TC-003"]
    - requirement_ref: "FR-013"
      test_cases: ["TC-003"]
    - requirement_ref: "FR-020"
      test_cases: ["TC-001"]
    - requirement_ref: "FR-021"
      test_cases: ["TC-002", "TC-006", "TC-007"]
    - requirement_ref: "FR-022"
      test_cases: ["TC-006", "TC-007"]
    - requirement_ref: "FR-045"
      test_cases: ["TC-007"]
  code_coverage:
    target: "80%"
    achieved: ""
  untested_areas: []

test_execution_summary:
  total_cases: 12
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
    - requirement_ref: "FR-010"
      test_cases: ["TC-005"]
    - requirement_ref: "FR-011"
      test_cases: ["TC-003"]
    - requirement_ref: "FR-013"
      test_cases: ["TC-003"]
    - requirement_ref: "FR-020"
      test_cases: ["TC-001"]
    - requirement_ref: "FR-021"
      test_cases: ["TC-002", "TC-006", "TC-007"]
    - requirement_ref: "FR-022"
      test_cases: ["TC-006", "TC-007"]
    - requirement_ref: "FR-045"
      test_cases: ["TC-007"]
  designs:
    - design_ref: "design-0002-statemonitor.md"
      test_cases: ["TC-001" through "TC-012"]
  changes: []

notes: |
  Tests use pytest-asyncio for async function testing.
  All component dependencies mocked using unittest.mock.AsyncMock.
  Focus on state machine logic, not actual network operations.

version_history:
  - version: "1.0"
    date: "2025-11-14"
    author: "Domain 1"
    changes:
      - "Initial test specification covering state machine requirements"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t05_test"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
