Created: 2025 November 14

# WebServer Module Test Specification

```yaml
test_info:
  id: "test-0005"
  title: "WebServer Module Unit Tests"
  date: "2025-11-14"
  author: "Domain 1"
  status: "planned"
  type: "unit"
  priority: "high"

source:
  test_target: "webserver.py - HTTP configuration interface on port 8080"
  design_refs:
    - "design-0005-webserver.md"
  change_refs: []
  requirement_refs:
    - "FR-050: Serve web interface on port 8080"
    - "FR-051: GET / endpoint serving main page"
    - "FR-052: GET /api/scan returning JSON network list"
    - "FR-053: POST /api/configure accepting SSID/password"
    - "FR-054: GET /api/status returning current state"
    - "FR-055: Respond within 500ms"

scope:
  description: "Unit tests for HTTP server covering endpoint routing, JSON APIs, HTML serving, thread safety, and lifecycle management"
  test_objectives:
    - "Verify HTTP endpoint routing"
    - "Test JSON API request/response"
    - "Validate HTML page serving"
    - "Test server lifecycle (start/stop)"
    - "Verify thread safety"
    - "Test error handling"
  in_scope:
    - "ConfigHTTPHandler methods"
    - "WebServerManager lifecycle"
    - "ThreadedHTTPServer threading"
    - "Module-level functions"
  out_scope:
    - "Actual connection_manager/state_monitor integration (mocked)"
    - "Browser JavaScript execution"
  dependencies:
    - "unittest.mock for component mocking"
    - "http.client for test requests"

test_environment:
  python_version: "3.11+"
  os: "Linux"
  libraries:
    - name: "pytest"
      version: ">=7.0.0"
  test_framework: "pytest"
  test_data_location: "N/A"

test_cases:
  - case_id: "TC-001"
    description: "Verify GET / returns HTML page"
    category: "positive"
    test_steps:
      - step: "1"
        action: "Start server, send GET /"
    expected_outputs:
      - field: "status_code"
        expected_value: "200"
      - field: "content_type"
        expected_value: "text/html"
      - field: "contains_html"
        expected_value: "<!DOCTYPE html>"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-002"
    description: "Verify GET /api/scan returns JSON network list"
    category: "positive"
    preconditions:
      - "Mock ConnectionManager.scan_networks()"
    test_steps:
      - step: "1"
        action: "Send GET /api/scan"
    expected_outputs:
      - field: "status_code"
        expected_value: "200"
      - field: "content_type"
        expected_value: "application/json"
      - field: "json_structure"
        expected_value: "{networks: []}"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-003"
    description: "Verify POST /api/configure with valid data returns success"
    category: "positive"
    preconditions:
      - "Mock ConnectionManager.configure_network()"
    test_steps:
      - step: "1"
        action: "Send POST /api/configure with JSON body"
    inputs:
      - parameter: "body"
        value: "{ssid: TestSSID, password: password123}"
        type: "JSON"
    expected_outputs:
      - field: "status_code"
        expected_value: "200"
      - field: "json_success"
        expected_value: "true"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-004"
    description: "Verify POST /api/configure rejects empty SSID"
    category: "negative"
    test_steps:
      - step: "1"
        action: "Send POST with empty SSID"
    inputs:
      - parameter: "body"
        value: "{ssid: '', password: password123}"
        type: "JSON"
    expected_outputs:
      - field: "status_code"
        expected_value: "400"
      - field: "json_success"
        expected_value: "false"
      - field: "error_message"
        expected_value: "SSID is required"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-005"
    description: "Verify POST /api/configure rejects empty password"
    category: "negative"
    test_steps:
      - step: "1"
        action: "Send POST with empty password"
    inputs:
      - parameter: "body"
        value: "{ssid: TestSSID, password: ''}"
        type: "JSON"
    expected_outputs:
      - field: "status_code"
        expected_value: "400"
      - field: "error_message"
        expected_value: "Password is required"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-006"
    description: "Verify GET /api/status returns state information"
    category: "positive"
    preconditions:
      - "Mock StateMonitor, ConnectionManager, APManager"
    test_steps:
      - step: "1"
        action: "Send GET /api/status"
    expected_outputs:
      - field: "status_code"
        expected_value: "200"
      - field: "json_fields"
        expected_value: "state, ssid, ap_active present"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-007"
    description: "Verify 404 response for unknown endpoints"
    category: "negative"
    test_steps:
      - step: "1"
        action: "Send GET /unknown/path"
    expected_outputs:
      - field: "status_code"
        expected_value: "404"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-008"
    description: "Verify start_server binds to port 8080"
    category: "positive"
    test_steps:
      - step: "1"
        action: "Call start_server()"
      - step: "2"
        action: "Verify server thread running"
    expected_outputs:
      - field: "server_running"
        expected_value: "True"
      - field: "port"
        expected_value: "8080"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-009"
    description: "Verify start_server raises PortInUseError if already running"
    category: "negative"
    preconditions:
      - "Server already started"
    test_steps:
      - step: "1"
        action: "Call start_server() again"
    expected_outputs:
      - field: "exception_type"
        expected_value: "PortInUseError"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-010"
    description: "Verify stop_server shuts down gracefully"
    category: "positive"
    preconditions:
      - "Server running"
    test_steps:
      - step: "1"
        action: "Call stop_server()"
      - step: "2"
        action: "Verify is_running() returns False"
    expected_outputs:
      - field: "server_stopped"
        expected_value: "True"
      - field: "thread_terminated"
        expected_value: "True"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-011"
    description: "Verify CORS headers present in JSON responses"
    category: "positive"
    test_steps:
      - step: "1"
        action: "Send GET /api/scan"
      - step: "2"
        action: "Check response headers"
    expected_outputs:
      - field: "cors_origin"
        expected_value: "Access-Control-Allow-Origin: *"
      - field: "cors_methods"
        expected_value: "Present"
    execution:
      status: "not_run"
    defects: []

  - case_id: "TC-012"
    description: "Verify malformed JSON returns 400"
    category: "negative"
    test_steps:
      - step: "1"
        action: "Send POST /api/configure with invalid JSON"
    inputs:
      - parameter: "body"
        value: "{invalid json"
        type: "str"
    expected_outputs:
      - field: "status_code"
        expected_value: "400"
      - field: "error_message"
        expected_value: "Invalid JSON format"
    execution:
      status: "not_run"
    defects: []

coverage:
  requirements_covered:
    - requirement_ref: "FR-050"
      test_cases: ["TC-008"]
    - requirement_ref: "FR-051"
      test_cases: ["TC-001"]
    - requirement_ref: "FR-052"
      test_cases: ["TC-002"]
    - requirement_ref: "FR-053"
      test_cases: ["TC-003", "TC-004", "TC-005"]
    - requirement_ref: "FR-054"
      test_cases: ["TC-006"]
  code_coverage:
    target: "80%"
    achieved: ""

test_execution_summary:
  total_cases: 12
  passed: 0
  failed: 0
  blocked: 0
  skipped: 0

notes: |
  Tests use http.client to send actual HTTP requests to local server.
  Component dependencies mocked for isolation.
  Server lifecycle tests verify threading behavior.

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
