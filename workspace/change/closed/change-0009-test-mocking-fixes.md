Created: 2025 November 26

# Change: Test Mocking Infrastructure Fixes

```yaml
change_info:
  id: "change-0009"
  title: "Fix test mocking infrastructure for APManager, StateMonitor, ConnectionManager, WebServer, and ServiceController modules"
  date: "2025-11-26"
  author: "Domain 1"
  type: "test_fix"
  status: "proposed"

issue_refs:
  - id: "issue-0006"
    title: "APManager nmcli output parsing failure"
  - id: "issue-0007"
    title: "StateMonitor async test timing race condition"
  - id: "issue-0008"
    title: "ConnectionManager thread lock testing incompatibility"
  - id: "issue-0009"
    title: "WebServer handler initialization test failures"
  - id: "issue-0010"
    title: "ServiceController test import and signature mismatches"

design_refs:
  - "design-0001-apmanager.md"
  - "design-0002-statemonitor.md"
  - "design-0003-connectionmanager.md"
  - "design-0004-webserver.md"
  - "design-0006-servicecontroller.md"

test_refs:
  - "test-0001-apmanager.md"
  - "test-0002-connectionmanager.md"
  - "test-0003-statemonitor.md"
  - "test-0004-webserver.md"
  - "test-0006-servicecontroller.md"

scope:
  components:
    - "pyproject.toml"
    - "src/tests/apmanager/test_apmanager.py"
    - "src/tests/statemonitor/test_statemonitor.py"
    - "src/tests/connectionmanager/test_connectionmanager.py"
    - "src/tests/webserver/test_webserver.py"
    - "src/tests/servicecontroller/test_main.py"
    - "src/tests/servicecontroller/test_servicecontroller.py"
  
  requirements: []
  version: "0.2.0"

description: |
  Fix 78 test failures across 5 modules caused by incorrect mocking strategies,
  missing pytest-asyncio configuration, and test infrastructure incompatibilities.
  
  Primary failure categories:
  1. APManager (24 failures): subprocess.check_output not properly mocked before AccessPoint instantiation
  2. Async tests (28 failures): pytest-asyncio not configured, timing issues with CHECK_INTERVAL
  3. Lock tests (3 failures): Cannot patch read-only _thread.lock attributes
  4. HTTP handler tests (9 failures): Mock objects incompatible with BaseHTTPRequestHandler
  5. ServiceController tests (8 failures): Missing imports, incorrect function signatures
  6. Logging tests (3 failures): Mock FileHandler causing comparison errors
  7. WebServerManager tests (3 failures): Module singleton pattern issues

changes:
  - file: "pyproject.toml"
    type: "modify"
    description: "Configure pytest-asyncio for async test support"
    rationale: "28 async tests fail with 'async def functions are not natively supported'"
    details: |
      Add pytest-asyncio mode configuration to tool.pytest.ini_options:
      
      ```toml
      [tool.pytest.ini_options]
      asyncio_mode = "auto"
      testpaths = ["src/tests"]  # Fix: was "tests", should be "src/tests"
      python_files = ["test_*.py"]
      python_classes = ["Test*"]
      python_functions = ["test_*"]
      ```

  - file: "src/tests/apmanager/test_apmanager.py"
    type: "modify"
    description: "Fix subprocess mocking - mock BEFORE AccessPoint() instantiation"
    rationale: "All 24 APManager tests fail because nmcli subprocess called before mocks established"
    details: |
      Pattern change for all test methods:
      
      BEFORE (incorrect):
      ```python
      def test_access_point_initializes_with_interface(self):
          nmcli_output = b"DEVICE  TYPE  STATE\nwlan0   wifi  connected\n"
          with patch('subprocess.check_output', return_value=nmcli_output):
              ap = AccessPoint()  # FAILS - tries actual nmcli call
      ```
      
      AFTER (correct):
      ```python
      def test_access_point_initializes_with_interface(self):
          nmcli_device = b"DEVICE  TYPE      STATE\nwlan0   wifi      connected\n"
          nmcli_mac = b"GENERAL.HWADDR:AA:BB:CC:DD:EE:FF\n"
          
          with patch('subprocess.check_output') as mock_check:
              mock_check.side_effect = [nmcli_device, nmcli_mac]
              ap = AccessPoint()
              assert ap.interface == "wlan0"
              assert ap.mac_address == "AA:BB:CC:DD:EE:FF"
              assert ap.ssid == "RPi-EEFF"
      ```
      
      Apply to all 24 test methods in TestAccessPointInitialization, TestInterfaceDetection,
      TestProfileCreation, TestAPActivation, TestFallbackOpenAP, and TestModuleFunctions classes.

  - file: "src/tests/statemonitor/test_statemonitor.py"
    type: "modify"
    description: "Fix async test timing by mocking CHECK_INTERVAL constant"
    rationale: "Test uses 0.3s window but production code has 30s intervals"
    details: |
      Update test_monitoring_loop_transitions_to_ap_after_three_failures:
      
      ```python
      @pytest.mark.asyncio
      async def test_monitoring_loop_transitions_to_ap_after_three_failures(self):
          """Monitoring loop transitions to AP mode after 3 failures."""
          with patch('statemonitor.CHECK_INTERVAL', 0.05):  # 50ms for testing
              connection = Mock()
              connection.test_connection = Mock(return_value=False)
              ap_manager = Mock()
              web_server = Mock()
              
              sm = StateMonitor(connection, ap_manager, web_server)
              sm.initialize()
              
              async def run_and_shutdown():
                  await asyncio.sleep(0.2)  # Allow 4 iterations at 50ms each
                  sm.shutdown_event.set()
              
              await asyncio.gather(
                  sm.monitoring_loop(),
                  run_and_shutdown()
              )
              
              assert sm.failure_count >= 3
              assert sm.current_state == SystemState.AP_MODE
              ap_manager.activate_ap.assert_called_once()
      ```

  - file: "src/tests/connectionmanager/test_connectionmanager.py"
    type: "modify"
    description: "Replace lock mocking with actual concurrency testing"
    rationale: "_thread.lock attributes are read-only, cannot be patched"
    details: |
      Replace 3 failed tests with concurrent execution tests:
      
      ```python
      def test_configure_network_thread_safe(self):
          """Verify configure_network handles concurrent calls."""
          from threading import Thread
          results = []
          errors = []
          
          def worker(suffix):
              try:
                  with patch('subprocess.run'), \
                       patch.object(ConfigManager, 'persist_configuration'):
                      configure_network(f"TestSSID{suffix}", "password123")
                      results.append(suffix)
              except Exception as e:
                  errors.append(e)
          
          threads = [Thread(target=worker, args=(i,)) for i in range(10)]
          for t in threads:
              t.start()
          for t in threads:
              t.join()
          
          assert len(errors) == 0, f"Concurrent calls raised errors: {errors}"
          assert len(results) == 10, "Not all threads completed"
      
      def test_persist_configuration_thread_safe(self):
          """Verify persist_configuration handles concurrent calls."""
          from threading import Thread
          results = []
          errors = []
          
          def worker(suffix):
              try:
                  with patch('pathlib.Path.mkdir'), \
                       patch('builtins.open', mock_open()), \
                       patch('json.dump'):
                      ConfigManager.persist_configuration(f"TestSSID{suffix}")
                      results.append(suffix)
              except Exception as e:
                  errors.append(e)
          
          threads = [Thread(target=worker, args=(i,)) for i in range(10)]
          for t in threads:
              t.start()
          for t in threads:
              t.join()
          
          assert len(errors) == 0
          assert len(results) == 10
      
      def test_load_configuration_thread_safe(self):
          """Verify load_configuration handles concurrent calls."""
          from threading import Thread
          results = []
          errors = []
          
          def worker():
              try:
                  with patch('pathlib.Path.exists', return_value=True), \
                       patch('builtins.open', mock_open(read_data='{"ssid": "TestSSID"}')), \
                       patch('json.load', return_value={"ssid": "TestSSID"}):
                      ssid = ConfigManager.load_configuration()
                      results.append(ssid)
              except Exception as e:
                  errors.append(e)
          
          threads = [Thread(target=worker) for _ in range(10)]
          for t in threads:
              t.start()
          for t in threads:
              t.join()
          
          assert len(errors) == 0
          assert all(r == "TestSSID" for r in results)
      ```

  - file: "src/tests/webserver/test_webserver.py"
    type: "modify"
    description: "Test HTTP handler methods directly without BaseHTTPRequestHandler instantiation"
    rationale: "Mock objects incompatible with socket infrastructure required by parent class"
    details: |
      Replace 9 failed handler tests with method-level testing:
      
      ```python
      def test_do_get_serves_html_for_root(self):
          """GET / returns HTML configuration page."""
          handler = Mock(spec=ConfigHTTPHandler)
          handler.path = '/'
          handler.send_response = Mock()
          handler.send_header = Mock()
          handler.end_headers = Mock()
          handler.wfile = Mock()
          
          ConfigHTTPHandler.do_GET(handler)
          
          handler.send_response.assert_called_once_with(200)
          handler.send_header.assert_any_call('Content-type', 'text/html')
          written_data = handler.wfile.write.call_args[0][0]
          assert b'<!DOCTYPE html>' in written_data
          assert b'<title>WiFi Configuration</title>' in written_data
      
      def test_do_get_handles_scan_request(self):
          """GET /api/scan triggers network scan."""
          handler = Mock(spec=ConfigHTTPHandler)
          handler.path = '/api/scan'
          handler.send_json_response = Mock()
          
          with patch('connectionmanager.scan_networks', return_value=[
              NetworkInfo("TestSSID1", 90),
              NetworkInfo("TestSSID2", 75)
          ]):
              ConfigHTTPHandler.do_GET(handler)
              
              handler.send_json_response.assert_called_once()
              call_args = handler.send_json_response.call_args
              assert call_args[0][0] == 200
              data = call_args[0][1]
              assert 'networks' in data
              assert len(data['networks']) == 2
      
      def test_do_post_handles_configure_request(self):
          """POST /api/configure processes network configuration."""
          handler = Mock(spec=ConfigHTTPHandler)
          handler.path = '/api/configure'
          handler.headers = {'content-length': '42'}
          handler.rfile = Mock()
          handler.rfile.read = Mock(return_value=b'{"ssid": "TestSSID", "password": "testpass"}')
          handler.send_json_response = Mock()
          
          with patch('connectionmanager.configure_network') as mock_config:
              ConfigHTTPHandler.do_POST(handler)
              
              mock_config.assert_called_once_with("TestSSID", "testpass")
              handler.send_json_response.assert_called_once()
              assert handler.send_json_response.call_args[0][0] == 200
      ```
      
      Apply similar patterns to all 9 failed handler tests.
      
      For WebServerManager tests:
      ```python
      def test_stop_server_shuts_down_gracefully(self):
          """stop_server() shuts down and closes server."""
          manager = WebServerManager(port=8080)
          mock_server = Mock()
          mock_thread = Mock()
          manager.server = mock_server
          manager.server_thread = mock_thread
          
          manager.stop_server()
          
          mock_server.shutdown.assert_called_once()
          mock_server.server_close.assert_called_once()
          mock_thread.join.assert_called_once()
          assert manager.server is None
          assert manager.server_thread is None
      ```

  - file: "src/tests/servicecontroller/test_main.py"
    type: "modify"
    description: "Fix logging handler mocking to avoid level comparison errors"
    rationale: "Mock FileHandler lacks numeric level attribute causing TypeError in logging framework"
    details: |
      ```python
      def test_configure_logging_creates_file_handler(self):
          """File handler created for all modes."""
          mock_handler = Mock(spec=logging.FileHandler)
          mock_handler.level = logging.INFO  # Add numeric level
          mock_handler.setLevel = Mock()
          mock_handler.setFormatter = Mock()
          
          with patch('pathlib.Path.mkdir'), \
               patch('logging.FileHandler', return_value=mock_handler), \
               patch('logging.StreamHandler'), \
               patch('os.chmod'):
              
              configure_logging('service')
              
              assert mock_handler.setLevel.called
              assert mock_handler.setFormatter.called
      ```

  - file: "src/tests/servicecontroller/test_servicecontroller.py"
    type: "modify"
    description: "Fix import references and function signatures to match actual implementation"
    rationale: "Tests reference non-existent module attributes and use incorrect signatures"
    details: |
      First, inspect src/main.py to identify actual implementation:
      - Determine actual log file path configuration
      - Verify function signatures for signal_handler, register_signal_handlers, graceful_shutdown
      - Identify class naming (StateMonitor vs StateMachine)
      
      Then update tests accordingly:
      
      ```python
      # If main.py uses hardcoded path instead of constant:
      def test_configure_logging_creates_file_handler(self):
          """TC-006: Verify configure_logging creates file handler."""
          with patch('pathlib.Path.mkdir'), \
               patch('logging.FileHandler') as mock_handler:
              
              mock_handler.return_value.level = logging.INFO
              configure_logging('service')
              
              # Verify handler created for /var/log/pi-netconfig.log
              mock_handler.assert_called_once()
              call_path = str(mock_handler.call_args[0][0])
              assert 'pi-netconfig.log' in call_path
      
      # Update function signatures based on actual implementation:
      def test_signal_handler_sets_shutdown_event(self):
          """TC-009: Verify signal_handler sets shutdown_event."""
          # If implementation is signal_handler(signum, frame):
          shutdown_event = asyncio.Event()
          
          # Store event in module-level or closure scope for signal handler
          with patch('main.shutdown_event', shutdown_event):
              signal_handler(signal.SIGTERM, None)
              # Verify event set through module state
      ```
      
      NOTE: Requires inspection of src/main.py to determine actual signatures.
      May need additional async test fixtures if tests are async.

  - file: "src/tests/servicecontroller/test_main.py"
    type: "modify"
    description: "Fix async test infrastructure - missing await and event loop setup"
    rationale: "Async tests fail with 'no running event loop' and 'coroutine was never awaited'"
    details: |
      ```python
      @pytest.mark.asyncio
      async def test_graceful_shutdown_calls_state_monitor_shutdown(self):
          """Graceful shutdown calls state monitor shutdown."""
          mock_monitor = Mock()
          mock_monitor.shutdown = AsyncMock()
          
          with patch('main.state_monitor', mock_monitor):
              await graceful_shutdown()
              mock_monitor.shutdown.assert_called_once()
      
      @pytest.mark.asyncio
      async def test_run_service_creates_shutdown_event(self):
          """run_service creates shutdown event."""
          with patch('main.StateMonitor') as mock_monitor_class:
              mock_monitor = AsyncMock()
              mock_monitor_class.return_value = mock_monitor
              mock_monitor.initialize = Mock()
              
              # Create task with timeout to avoid hanging
              try:
                  await asyncio.wait_for(run_service(), timeout=0.1)
              except asyncio.TimeoutError:
                  pass  # Expected - service runs until shutdown
              
              mock_monitor.initialize.assert_called_once()
      ```

impact:
  testing: "78 failed tests will pass. Test suite coverage increases from 53% to ~95% pass rate."
  functionality: "No functional changes - pure test infrastructure fixes"
  performance: "No performance impact"
  interfaces: "No interface changes"
  dependencies: "pytest-asyncio already in dev dependencies, no new deps required"

migration:
  breaking_changes: false
  deprecations: []
  compatibility: "All changes are test-only, no production code impact"
  upgrade_path: "None required - test fixes only"

risks:
  - risk: "Async test timing still fragile despite CHECK_INTERVAL mocking"
    severity: "low"
    mitigation: "Added buffer in sleep durations, tests verify behavior not exact timing"
  
  - risk: "Concurrency tests may have platform-specific behavior"
    severity: "low"
    mitigation: "Tests verify absence of race conditions/deadlocks, not specific interleaving"
  
  - risk: "ServiceController tests depend on actual main.py implementation details"
    severity: "medium"
    mitigation: "Requires manual inspection of main.py before implementing fixes"

validation:
  verification_methods:
    - "Run full test suite: pytest src/tests/"
    - "Verify test count: 165 tests, expect ~156 passing (95%)"
    - "Check module-specific pass rates"
    - "Run with coverage: pytest --cov=src --cov-report=html"
  
  acceptance_criteria:
    - "APManager: 24/24 tests pass (100%)"
    - "StateMonitor: 25/25 tests pass (100%)"
    - "ConnectionManager: 22/22 tests pass (100%)"
    - "WebServer: 28/28 tests pass (100%)"
    - "ServiceController: 17/17 tests pass (100%)"
    - "Overall pass rate: ≥95%"
  
  rollback_procedure: "Git revert change commit, restore original test files"

implementation:
  order:
    1: "Update pyproject.toml - pytest configuration"
    2: "Fix APManager tests - highest failure count, clearest fix"
    3: "Fix ConnectionManager lock tests - straightforward replacement"
    4: "Fix StateMonitor async timing - single test fix"
    5: "Fix WebServer handler tests - method-level testing pattern"
    6: "Inspect main.py for ServiceController actual implementation"
    7: "Fix ServiceController tests based on inspection findings"
  
  dependencies:
    - "Step 6 (main.py inspection) must complete before Step 7"
    - "All other steps independent"
  
  testing_strategy: |
    After each module fix:
    1. Run module-specific tests: pytest src/tests/{module}/
    2. Verify pass rate improvement
    3. Document any remaining failures
    4. Commit working changes
    
    Final validation:
    1. Run full suite: pytest src/tests/
    2. Generate coverage report
    3. Document final pass rates per module
    4. Compare against acceptance criteria

notes: |
  Priority order rationale:
  - APManager: 24 failures, clearest fix pattern, critical for system functionality
  - ConnectionManager: 3 failures, straightforward replacement with concurrency tests
  - StateMonitor: 1 failure, simple timing mock
  - WebServer: 9 failures, method-level testing pattern
  - ServiceController: 8 failures, requires investigation first
  
  Test philosophy:
  - Unit tests should not require actual system resources (nmcli, sockets)
  - Async tests need proper timing control for deterministic behavior
  - Thread-safety verified through actual concurrency, not mock inspection
  - HTTP handlers testable at method level, not through protocol stack
  
  Known limitations:
  - Some tests may still be environment-dependent (platform, Python version)
  - Integration testing on actual Pi hardware still required for full validation
  - Mocking external commands (nmcli) doesn't verify actual command compatibility

version_history:
  - version: "1.0"
    date: "2025-11-26"
    author: "Domain 1"
    changes:
      - "Initial change document creation"
      - "Comprehensive test mocking fixes for all 5 affected modules"
      - "78 test failures addressed with specific solutions"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
