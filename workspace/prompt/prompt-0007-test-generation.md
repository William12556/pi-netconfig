# T04 Prompt: Comprehensive Unit Test Suite Generation

```yaml
prompt_info:
  id: "prompt-0007"
  task_type: "code_generation"
  source_ref: "test-0002 through test-0006, audit-0001 CI-1"
  date: "2025-11-14"
  priority: "critical"

context:
  purpose: "Generate comprehensive unit test suite achieving 80% code coverage per governance P06 requirements"
  integration: "Tests execute via pytest in src/tests/ with component-based organization"
  constraints:
    - "Must use pytest and pytest-asyncio frameworks"
    - "All external dependencies mocked using unittest.mock"
    - "Isolated test environments via tempfile/TemporaryDirectory"
    - "Thread-safe test execution"
    - "No actual system operations (all mocked)"

specification:
  description: |
    Generate executable pytest test files for all pi-netconfig modules covering 71 test
    cases documented in test-0002 through test-0006. Tests must achieve minimum 80% code
    coverage and verify all functional requirements FR-001 through FR-074.
  
  requirements:
    functional:
      - "Implement all test cases from test specifications"
      - "Cover all 37 functional requirements"
      - "Verify thread safety where applicable"
      - "Test error handling and recovery"
      - "Validate input validation logic"
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "pytest test discovery conventions"
        - "unittest.mock for all external dependencies"
        - "pytest-asyncio for async function testing"
        - "tempfile for filesystem isolation"
        - "Comprehensive assertions"
        - "Clear test naming: test_<module>_<scenario>"

  performance:
    - target: "Complete test suite execution < 60 seconds"
      metric: "time"
    - target: "80% code coverage minimum"
      metric: "coverage"

design:
  architecture: "Component-based test organization in src/tests/<component>/"
  
  components:
    - name: "test_installer.py"
      type: "module"
      purpose: "Unit tests for installer.py - 15 test cases"
      interface:
        inputs:
          - name: "Mocked filesystem, subprocess, os.geteuid"
            type: "unittest.mock"
            description: "Isolated test environment"
        outputs:
          type: "pytest test results"
          description: "Pass/fail for each test case"
      logic:
        - "TC-001/002: Service detection (is_service_installed)"
        - "TC-003/004: Root privilege verification"
        - "TC-005/006: Directory creation with permissions"
        - "TC-007: Application file copy"
        - "TC-008: Systemd unit generation"
        - "TC-009: Unit installation and daemon-reload"
        - "TC-010/011: Service enable/start with error handling"
        - "TC-012: Rollback cleanup"
        - "TC-013/014/015: install() entry point workflow"

    - name: "test_statemonitor.py"
      type: "module"
      purpose: "Unit tests for statemonitor.py - 12 test cases"
      interface:
        inputs:
          - name: "Mocked connection_manager, ap_manager, web_server"
            type: "unittest.mock.AsyncMock"
            description: "Component dependencies"
        outputs:
          type: "pytest test results"
          description: "Async test execution results"
      logic:
        - "TC-001: Initial state verification"
        - "TC-002: CLIENT mode transition on successful connection"
        - "TC-003: AP_MODE transition after 3 failures"
        - "TC-004: Failure count reset logic"
        - "TC-005: 30-second monitoring interval"
        - "TC-006: Component deactivation on CLIENT transition"
        - "TC-007: Component activation on AP_MODE transition"
        - "TC-008: Transition failure recovery"
        - "TC-009: Graceful shutdown"
        - "TC-010/011: Exception handling"
        - "TC-012: StateTransitionError on component failure"

    - name: "test_connectionmanager.py"
      type: "module"
      purpose: "Unit tests for connectionmanager.py - 15 test cases"
      interface:
        inputs:
          - name: "Mocked socket, subprocess, filesystem"
            type: "unittest.mock"
            description: "Network and filesystem operations"
        outputs:
          type: "pytest test results"
          description: "Connectivity, scanning, configuration tests"
      logic:
        - "TC-001/002/003: Connectivity testing (8.8.8.8, 1.1.1.1 fallback)"
        - "TC-004/005: Network scanning and duplicate filtering"
        - "TC-006: nmcli failure handling"
        - "TC-007/008/009: Input validation (SSID, password, special chars)"
        - "TC-010: Full configuration workflow"
        - "TC-011: Directory creation"
        - "TC-012: Default AP password persistence"
        - "TC-013/014: Configuration loading"
        - "TC-015: Thread safety verification"

    - name: "test_webserver.py"
      type: "module"
      purpose: "Unit tests for webserver.py - 12 test cases"
      interface:
        inputs:
          - name: "HTTP test client, mocked components"
            type: "http.client + unittest.mock"
            description: "HTTP endpoint testing"
        outputs:
          type: "pytest test results"
          description: "HTTP request/response verification"
      logic:
        - "TC-001: GET / HTML page serving"
        - "TC-002: GET /api/scan JSON response"
        - "TC-003/004/005: POST /api/configure validation"
        - "TC-006: GET /api/status state query"
        - "TC-007: 404 for unknown endpoints"
        - "TC-008/009: Server lifecycle (start/stop, port conflict)"
        - "TC-010: Graceful shutdown"
        - "TC-011: CORS headers"
        - "TC-012: Malformed JSON handling"

    - name: "test_servicecontroller.py"
      type: "module"
      purpose: "Unit tests for main.py - 17 test cases"
      interface:
        inputs:
          - name: "Mocked execution environment"
            type: "unittest.mock"
            description: "OS, signals, logging, asyncio"
        outputs:
          type: "pytest test results"
          description: "Entry point and lifecycle tests"
      logic:
        - "TC-001/002/003: Execution mode detection"
        - "TC-004/005: Privilege verification"
        - "TC-006/007/008: Logging configuration (service/manual/errors)"
        - "TC-009/010: Signal handling (SIGTERM/SIGINT)"
        - "TC-011/012: Graceful shutdown with timeout"
        - "TC-013: Service loop execution"
        - "TC-014/015: Bootstrap mode install"
        - "TC-016: Service mode execution"
        - "TC-017: Privilege failure handling"

  dependencies:
    internal:
      - "All src/*.py modules under test"
    external:
      - "pytest>=7.0.0"
      - "pytest-asyncio>=0.21.0"
      - "pytest-cov>=4.0.0"
      - "unittest.mock (stdlib)"
      - "tempfile (stdlib)"
      - "http.client (stdlib)"
      - "threading (stdlib)"

error_handling:
  strategy: "Tests verify error conditions explicitly via negative test cases"
  exceptions:
    - exception: "AssertionError"
      condition: "Test assertion fails"
      handling: "pytest reports failure with diff"
    - exception: "Mock exceptions"
      condition: "Verify exception propagation"
      handling: "pytest.raises() context manager"
  logging:
    level: "DEBUG"
    format: "pytest captures all logs for failure analysis"

testing:
  unit_tests:
    - scenario: "Run complete test suite: pytest src/tests/"
      expected: "71 tests pass, 0 failures"
    - scenario: "Run with coverage: pytest --cov=src --cov-report=term-missing"
      expected: "80%+ coverage across all modules"
  edge_cases:
    - "Concurrent operations (threading tests)"
    - "Async function cancellation"
    - "Resource cleanup on exception"
    - "Mock call verification"
  validation:
    - "All test cases from specifications implemented"
    - "Each test can run independently"
    - "No test pollution between runs"
    - "Clear assertion failure messages"

deliverable:
  format_requirements:
    - "Save test files to src/tests/<component>/test_<module>.py"
    - "Use pytest conventions: test_ prefix, Test classes optional"
    - "Include module docstrings referencing test specs"
    - "Import mocking at top of each file"
    - "Group related tests logically"
    - "Use descriptive test names matching TC-NNN from specs"
  
  files:
    - path: "src/tests/installer/test_installer.py"
      content: |
        """
        Unit tests for installer.py module
        
        Test Specification: workspace/test/test-0002-installer.md
        Requirements: FR-001 through FR-007
        Coverage Target: 80%
        """
        # Implementation: 15 test functions covering all test cases
    
    - path: "src/tests/statemonitor/test_statemonitor.py"
      content: |
        """
        Unit tests for statemonitor.py module
        
        Test Specification: workspace/test/test-0003-statemonitor.md
        Requirements: FR-010, FR-011, FR-013, FR-020, FR-021, FR-022, FR-045
        Coverage Target: 80%
        """
        # Implementation: 12 async test functions
    
    - path: "src/tests/connectionmanager/test_connectionmanager.py"
      content: |
        """
        Unit tests for connectionmanager.py module
        
        Test Specification: workspace/test/test-0004-connectionmanager.md
        Requirements: FR-012, FR-030-034, FR-060-062
        Coverage Target: 80%
        """
        # Implementation: 15 test functions including thread safety
    
    - path: "src/tests/webserver/test_webserver.py"
      content: |
        """
        Unit tests for webserver.py module
        
        Test Specification: workspace/test/test-0005-webserver.md
        Requirements: FR-050 through FR-055
        Coverage Target: 80%
        """
        # Implementation: 12 test functions covering HTTP endpoints
    
    - path: "src/tests/servicecontroller/test_servicecontroller.py"
      content: |
        """
        Unit tests for main.py module
        
        Test Specification: workspace/test/test-0006-servicecontroller.md
        Requirements: FR-023, FR-070-074
        Coverage Target: 80%
        """
        # Implementation: 17 test functions including async

  completion_document:
    path: "workspace/prompt/prompt-0007-completion.md"
    required_fields:
      - "timestamp: <ISO 8601 datetime>"
      - "files_created: [list of 5 test file paths]"
      - "test_cases_implemented: 71"
      - "status: SUCCESS or FAILURE"
      - "notes: Coverage achieved, any warnings"

success_criteria:
  - "All 5 test files created in correct locations"
  - "71 test cases implemented matching specifications"
  - "pytest discovers and runs all tests successfully"
  - "Minimum 80% code coverage achieved"
  - "All tests pass on first execution"
  - "No test interdependencies (can run in any order)"
  - "Clear failure messages for debugging"

notes: |
  This prompt addresses audit finding CI-1: No Unit Tests (P06 violation).
  Tests implement comprehensive coverage for all modules per governance requirements.
  Upon completion, updates required to trace-0001-traceability-matrix.md to reflect test coverage.

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

## Test Implementation Guidelines

### Mocking Best Practices

**Filesystem Operations:**
```python
from unittest.mock import patch, MagicMock
from tempfile import TemporaryDirectory

def test_with_temp_filesystem():
    with TemporaryDirectory() as tmpdir:
        # Use tmpdir for all file operations
        config_path = Path(tmpdir) / "config.json"
        ...
```

**Subprocess Mocking:**
```python
@patch('subprocess.run')
def test_nmcli_operation(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout=b'output')
    # Test code that calls subprocess.run
    ...
    mock_run.assert_called_once_with(['nmcli', ...])
```

**Async Function Testing:**
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

**Thread Safety Testing:**
```python
import threading

def test_concurrent_operations():
    threads = []
    results = []
    
    def worker():
        results.append(ConfigManager.configure_network('SSID', 'pass'))
    
    for _ in range(10):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    assert all(results)  # All succeeded without race conditions
```

### Test Organization

Each test file structure:
```python
"""Module docstring with references"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
from tempfile import TemporaryDirectory

# Import module under test
from module_name import ClassName, function_name

# Test functions follow naming: test_<component>_<scenario>
# Group related tests together
# Use descriptive assertions with messages
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
