Created: 2025 November 26

# Issue: StateMonitor Async Test Timing Race Condition

```yaml
issue_info:
  id: "issue-0007"
  title: "StateMonitor test_monitoring_loop_transitions_to_ap_after_three_failures fails due to insufficient loop iterations"
  date: "2025-11-26"
  reporter: "Domain 1"
  status: "open"
  severity: "high"
  type: "defect"

source:
  origin: "test_execution"
  test_ref: "test-0003-statemonitor.md"
  description: "Test expects failure_count >= 3 after monitoring loop executes, but actual count is 1. Race condition between test control and monitoring loop execution."

affected_scope:
  components:
    - name: "test_statemonitor.py"
      file_path: "src/tests/statemonitor/test_statemonitor.py"
      method: "TestMonitoringLoop.test_monitoring_loop_transitions_to_ap_after_three_failures"
  designs:
    - design_ref: "design-0002-statemonitor.md"
  version: "0.2.0"

reproduction:
  steps:
    - "Execute: pytest src/tests/statemonitor/test_statemonitor.py::TestMonitoringLoop::test_monitoring_loop_transitions_to_ap_after_three_failures"
    - "Observe assertion failure: failure_count=1, expected >= 3"
  frequency: "always"
  preconditions: "Async test environment"
  test_data: |
    Test configuration:
    - connection.test_connection returns False
    - shutdown triggered after 0.3 seconds (3 x 0.1s sleeps)
  error_output: |
    AssertionError: assert 1 >= 3
    where 1 = <statemonitor.StateMonitor object>.failure_count

behavior:
  expected: "Monitoring loop executes at least 3 iterations, incrementing failure_count to 3 or more"
  actual: "Loop executes only once before shutdown, failure_count remains at 1"
  impact: "Test suite reports false failure. Actual runtime behavior may be correct but untestable with current approach."
  workaround: "Manual verification on target hardware"

environment:
  python_version: "3.13.5"
  os: "Linux"
  dependencies:
    - "pytest-asyncio==1.3.0"
  domain: "domain_1"

analysis:
  root_cause: |
    Test uses parallel asyncio.gather() with two coroutines:
    1. sm.monitoring_loop() - checks connection every 30 seconds
    2. run_and_shutdown() - sleeps 0.3s then triggers shutdown
    
    Timing issue:
    - Monitoring loop has 30-second interval (CHECK_INTERVAL constant)
    - Test shutdown occurs after 0.3 seconds
    - Loop cannot complete even one full cycle before shutdown
    - Initial state transition increments failure_count once, then shutdown
    
    Test assumes monitoring loop will execute multiple iterations within 0.3s window,
    but production code uses 30-second intervals.
  
  technical_notes: |
    Current test structure (lines 239-248):
    ```python
    call_count = 0
    async def run_and_shutdown():
        nonlocal call_count
        while call_count < 3:
            await asyncio.sleep(0.1)
            call_count += 1
        sm.shutdown_event.set()
    ```
    
    This attempts to give loop time to execute, but doesn't account for 30s CHECK_INTERVAL
    in actual monitoring_loop() implementation.
  
  related_issues: []

resolution:
  assigned_to: "Domain 1"
  target_date: "TBD"
  approach: |
    Option 1: Mock CHECK_INTERVAL constant for testing
    ```python
    with patch('statemonitor.CHECK_INTERVAL', 0.05):
        # Test logic - loop iterates every 50ms instead of 30s
    ```
    
    Option 2: Add explicit iteration control to StateMonitor for testing
    ```python
    async def monitoring_loop(self, _test_iterations: int = None):
        iteration = 0
        while not self.shutdown_event.is_set():
            if _test_iterations and iteration >= _test_iterations:
                break
            # ... existing logic
            iteration += 1
    ```
    
    Option 3: Test failure accumulation directly without timing
    ```python
    # Call check_connection() directly 3 times
    # Verify failure_count increments
    # Verify transition_to_ap_mode called
    ```
    
    Recommended: Option 1 - cleanest, doesn't modify production code, maintains integration test style.
  
  change_ref: "TBD"
  resolved_date: null
  resolved_by: null
  fix_description: null

verification:
  verified_date: null
  verified_by: null
  test_results: null
  closure_notes: null

traceability:
  design_refs:
    - "design-0002-statemonitor.md"
  change_refs: []
  test_refs:
    - "test-0003-statemonitor.md"

notes: |
  Test pass rate: 24/25 (96%) - only this one test fails
  
  Not a production code defect - StateMonitor logic appears correct
  Test infrastructure issue requiring adjustment
  
  Severity: High (not Critical) because:
  - Production code likely correct
  - Other 24 tests pass
  - Single test failure doesn't block module functionality

version_history:
  - version: "1.0"
    date: "2025-11-26"
    author: "Domain 1"
    changes:
      - "Initial issue creation from test analysis"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
