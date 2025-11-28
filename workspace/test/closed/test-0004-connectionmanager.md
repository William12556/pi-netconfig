Created: 2025 November 14

# ConnectionManager Module Test Specification

```yaml
test_info:
  id: "test-0004"
  title: "ConnectionManager Module Unit Tests"
  date: "2025-11-14"
  author: "Domain 1"
  status: "planned"
  type: "unit"
  priority: "high"

source:
  test_target: "connectionmanager.py - WiFi connection management and configuration"
  design_refs:
    - "design-0003-connectionmanager.md"
  change_refs:
    - "change-0001-connectionmanager-defect-corrections.md"
  requirement_refs:
    - "FR-012: Test connectivity by pinging known hosts"
    - "FR-030: Scan for available WiFi networks"
    - "FR-031: Parse network SSID, signal, security, frequency"
    - "FR-032: Configure WiFi connection using nmcli"
    - "FR-033: Activate WiFi connection"
    - "FR-034: Persist last successful SSID to JSON"
    - "FR-060: Store last successful SSID only"
    - "FR-061: Persist to /etc/pi-netconfig/config.json"
    - "FR-062: Store timestamp in ISO 8601 format"

scope:
  description: "Unit tests for connection management covering connectivity testing, network scanning, configuration, persistence, and thread safety"
  test_objectives:
    - "Verify connectivity testing logic"
    - "Validate network scanning and parsing"
    - "Test WiFi configuration workflow"
    - "Verify configuration persistence"
    - "Test thread-safe concurrent operations"
    - "Validate input validation"
  in_scope:
    - "ConnectionTester class"
    - "NetworkScanner class"
    - "ConfigManager class"
    - "Thread safety via Lock"
    - "JSON persistence"
  out_scope:
    - "Actual nmcli command execution (mocked)"
    - "Actual socket connections (mocked)"
    - "Real filesystem operations (use tempfile)"
  dependencies:
    - "unittest.mock for subprocess and socket mocking"
    - "tempfile for isolated file operations"
    - "threading for concurrency testing"

test_environment:
  python_version: "3.11+"
  os: "Linux"
  libraries:
    - name: "pytest"
      version: ">=7.0.0"
  test_framework: "pytest"
  test_data_location: "Generated in test methods"

test_cases:
  - case_id: "TC-001"
    description: "Verify connectivity test returns True when first host reachable"
    category: "positive"
    preconditions:
      - "Mock socket.create_connection succeeds for 8.8.8.8"
    test_steps:
      - step: "1"
        action: "Call ConnectionTester.test_connection()"
    inputs: []
    expected_outputs:
      - field: "return_value"
        expected_value: "True"
        validation: "Boolean equality"
      - field: "second_host_not_tested"
        expected_value: "True"
        validation: "Only first host attempted"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-002"
    description: "Verify connectivity test returns True when second host reachable"
    category: "positive"
    preconditions:
      - "Mock socket.create_connection fails for 8.8.8.8"
      - "Mock socket.create_connection succeeds for 1.1.1.1"
    test_steps:
      - step: "1"
        action: "Call ConnectionTester.test_connection()"
    inputs: []
    expected_outputs:
      - field: "return_value"
        expected_value: "True"
        validation: "Boolean equality"
      - field: "both_hosts_tested"
        expected_value: "True"
        validation: "Fallback logic verified"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-003"
    description: "Verify connectivity test returns False when both hosts unreachable"
    category: "negative"
    preconditions:
      - "Mock socket.create_connection fails for both hosts"
    test_steps:
      - step: "1"
        action: "Call ConnectionTester.test_connection()"
    inputs: []
    expected_outputs:
      - field: "return_value"
        expected_value: "False"
        validation: "Boolean equality"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-004"
    description: "Verify network scan parses nmcli output correctly"
    category: "positive"
    preconditions:
      - "Mock subprocess.check_output returns valid nmcli terse output"
    test_steps:
      - step: "1"
        action: "Call NetworkScanner.scan_networks()"
      - step: "2"
        action: "Verify NetworkInfo objects created"
    inputs:
      - parameter: "nmcli_output"
        value: "TestSSID:75:WPA2:2.4GHz\\nOtherSSID:50:WPA3:5GHz"
        type: "str"
    expected_outputs:
      - field: "networks_count"
        expected_value: "2"
        validation: "List length"
      - field: "sorted_by_signal"
        expected_value: "True"
        validation: "Descending signal strength order"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-005"
    description: "Verify network scan filters duplicate SSIDs keeping strongest signal"
    category: "positive"
    preconditions:
      - "Mock nmcli output with duplicate SSID"
    test_steps:
      - step: "1"
        action: "Call NetworkScanner.scan_networks()"
    inputs:
      - parameter: "nmcli_output"
        value: "TestSSID:75:WPA2:2.4GHz\\nTestSSID:60:WPA2:5GHz"
        type: "str"
    expected_outputs:
      - field: "networks_count"
        expected_value: "1"
        validation: "Duplicate filtered"
      - field: "signal_strength"
        expected_value: "75"
        validation: "Stronger signal kept"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-006"
    description: "Verify network scan raises NetworkScanError on nmcli failure"
    category: "negative"
    preconditions:
      - "Mock subprocess.check_output raises CalledProcessError"
    test_steps:
      - step: "1"
        action: "Call NetworkScanner.scan_networks()"
    inputs: []
    expected_outputs:
      - field: "exception_type"
        expected_value: "NetworkScanError"
        validation: "Exception raised"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-007"
    description: "Verify configure_network validates SSID length"
    category: "negative"
    preconditions: []
    test_steps:
      - step: "1"
        action: "Call ConfigManager.configure_network('', 'password123')"
    inputs:
      - parameter: "ssid"
        value: ""
        type: "str"
    expected_outputs:
      - field: "exception_type"
        expected_value: "ConfigurationError"
        validation: "Invalid SSID rejected"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-008"
    description: "Verify configure_network validates password length"
    category: "negative"
    preconditions: []
    test_steps:
      - step: "1"
        action: "Call ConfigManager.configure_network('TestSSID', '123')"
    inputs:
      - parameter: "password"
        value: "123"
        type: "str"
    expected_outputs:
      - field: "exception_type"
        expected_value: "ConfigurationError"
        validation: "Short password rejected"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-009"
    description: "Verify configure_network validates special characters"
    category: "negative"
    preconditions: []
    test_steps:
      - step: "1"
        action: "Call ConfigManager.configure_network('Test;SSID', 'password123')"
    inputs:
      - parameter: "ssid"
        value: "Test;SSID"
        type: "str"
    expected_outputs:
      - field: "exception_type"
        expected_value: "ConfigurationError"
        validation: "Shell special character rejected"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-010"
    description: "Verify configure_network completes full workflow"
    category: "positive"
    preconditions:
      - "Mock all subprocess.run calls"
      - "Use tempfile for config path"
    test_steps:
      - step: "1"
        action: "Call ConfigManager.configure_network('TestSSID', 'password123')"
      - step: "2"
        action: "Verify nmcli delete called"
      - step: "3"
        action: "Verify nmcli add called"
      - step: "4"
        action: "Verify nmcli up called"
      - step: "5"
        action: "Verify persist_configuration called"
    inputs:
      - parameter: "ssid"
        value: "TestSSID"
        type: "str"
      - parameter: "password"
        value: "password123"
        type: "str"
    expected_outputs:
      - field: "return_value"
        expected_value: "True"
        validation: "Success indicated"
      - field: "config_file_written"
        expected_value: "True"
        validation: "Persistence verified"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-011"
    description: "Verify persist_configuration creates directory if missing"
    category: "positive"
    preconditions:
      - "Use tempfile for config directory"
      - "Directory does not exist initially"
    test_steps:
      - step: "1"
        action: "Call ConfigManager.persist_configuration('TestSSID')"
      - step: "2"
        action: "Verify directory created"
    inputs: []
    expected_outputs:
      - field: "directory_exists"
        expected_value: "True"
        validation: "mkdir(parents=True, exist_ok=True)"
      - field: "config_file_written"
        expected_value: "True"
        validation: "File exists"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-012"
    description: "Verify persist_configuration uses default AP password"
    category: "positive"
    preconditions:
      - "Use tempfile for config path"
    test_steps:
      - step: "1"
        action: "Call ConfigManager.persist_configuration('TestSSID')"
      - step: "2"
        action: "Read config file"
    inputs: []
    expected_outputs:
      - field: "ap_password"
        expected_value: "piconfig123"
        validation: "Field equals default"
      - field: "configured_ssid"
        expected_value: "TestSSID"
        validation: "SSID stored"
      - field: "last_connected"
        expected_value: "ISO 8601 timestamp"
        validation: "Timestamp format valid"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-013"
    description: "Verify load_configuration returns configured SSID"
    category: "positive"
    preconditions:
      - "Config file exists with valid JSON"
    test_steps:
      - step: "1"
        action: "Call ConfigManager.load_configuration()"
    inputs: []
    expected_outputs:
      - field: "return_value"
        expected_value: "TestSSID"
        validation: "SSID returned"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-014"
    description: "Verify load_configuration returns None when file missing"
    category: "positive"
    preconditions:
      - "Config file does not exist"
    test_steps:
      - step: "1"
        action: "Call ConfigManager.load_configuration()"
    inputs: []
    expected_outputs:
      - field: "return_value"
        expected_value: "None"
        validation: "None returned"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-015"
    description: "Verify thread safety under concurrent configure_network calls"
    category: "positive"
    preconditions:
      - "Mock all subprocess calls"
      - "Create multiple threads"
    test_steps:
      - step: "1"
        action: "Launch 10 threads calling configure_network"
      - step: "2"
        action: "Wait for all threads to complete"
      - step: "3"
        action: "Verify no race conditions"
    inputs: []
    expected_outputs:
      - field: "all_succeeded"
        expected_value: "True"
        validation: "All threads complete successfully"
      - field: "lock_acquired"
        expected_value: "True for each call"
        validation: "Lock prevents concurrent access"
    postconditions: []
    execution:
      status: "not_run"
    defects: []

coverage:
  requirements_covered:
    - requirement_ref: "FR-012"
      test_cases: ["TC-001", "TC-002", "TC-003"]
    - requirement_ref: "FR-030"
      test_cases: ["TC-004", "TC-006"]
    - requirement_ref: "FR-031"
      test_cases: ["TC-004", "TC-005"]
    - requirement_ref: "FR-032"
      test_cases: ["TC-010"]
    - requirement_ref: "FR-033"
      test_cases: ["TC-010"]
    - requirement_ref: "FR-034"
      test_cases: ["TC-010", "TC-012"]
    - requirement_ref: "FR-060"
      test_cases: ["TC-012"]
    - requirement_ref: "FR-061"
      test_cases: ["TC-011", "TC-012"]
    - requirement_ref: "FR-062"
      test_cases: ["TC-012"]
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
    - requirement_ref: "FR-012"
      test_cases: ["TC-001", "TC-002", "TC-003"]
    - requirement_ref: "FR-030"
      test_cases: ["TC-004", "TC-006"]
    - requirement_ref: "FR-031"
      test_cases: ["TC-004", "TC-005"]
    - requirement_ref: "FR-032"
      test_cases: ["TC-010"]
    - requirement_ref: "FR-033"
      test_cases: ["TC-010"]
    - requirement_ref: "FR-034"
      test_cases: ["TC-010", "TC-012"]
    - requirement_ref: "FR-060"
      test_cases: ["TC-012"]
    - requirement_ref: "FR-061"
      test_cases: ["TC-011", "TC-012"]
    - requirement_ref: "FR-062"
      test_cases: ["TC-012"]
  designs:
    - design_ref: "design-0003-connectionmanager.md"
      test_cases: ["TC-001" through "TC-015"]
  changes:
    - change_ref: "change-0001"
      test_cases: ["TC-011", "TC-012", "TC-015"]

notes: |
  Tests verify thread safety corrections from change-0001.
  All subprocess and socket operations mocked for isolation.
  Tempfile used for configuration file operations.

version_history:
  - version: "1.0"
    date: "2025-11-14"
    author: "Domain 1"
    changes:
      - "Initial test specification covering connection management requirements"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t05_test"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
