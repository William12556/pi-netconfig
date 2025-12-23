Created: 2025 December 23

```yaml
issue_info:
  id: "issue-0025"
  title: "StateMonitor.initialize() not called, monitoring loop fails silently"
  date: "2025-12-23"
  reporter: "Claude Desktop"
  status: "open"
  severity: "critical"
  type: "bug"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

source:
  origin: "hardware validation"
  test_ref: "CLIENT mode validation"
  description: "Monitoring loop started but no connection checks occur. StateMonitor.initialize() never called, shutdown_event remains None, causing loop to exit immediately with silent AttributeError."

affected_scope:
  components:
    - name: "ServiceController"
      file_path: "src/pi_netconfig/main.py"
    - name: "StateMonitor"
      file_path: "src/pi_netconfig/statemonitor.py"
  designs:
    - design_ref: "design-0002-statemonitor.md"
    - design_ref: "design-0006-servicecontroller.md"
  version: "0.2.6"

reproduction:
  prerequisites: "Service running on Pi"
  steps:
    - "Start service: sudo systemctl start pi-netconfig"
    - "Monitor logs: sudo tail -f /var/log/pi-netconfig.log"
    - "Observe: 'Monitoring loop started' appears"
    - "Wait 30+ seconds"
    - "Observe: No connection check activity logged"
  frequency: "always"
  reproducibility_conditions: "All service executions since version 0.2.4"
  preconditions: "None"
  test_data: "N/A"
  error_output: |
    Log shows:
    2025-12-23 06:47:37,073 DEBUG StateMonitor Monitoring loop started
    
    Then silence - no connection checks despite 90+ minute runtime

behavior:
  expected: |
    - StateMonitor.initialize() called before monitoring_loop()
    - shutdown_event created
    - Connection checks every 30 seconds
    - State transitions based on connection status
  actual: |
    - initialize() never called
    - shutdown_event remains None
    - monitoring_loop() line 105: while not self.shutdown_event.is_set() throws AttributeError
    - Loop exits immediately, silently
    - No connection checks occur
  impact: |
    - StateMonitor completely non-functional
    - No connection monitoring
    - No state transitions
    - CLIENT/AP mode validation impossible
    - System appears running but does nothing
  workaround: "None"

environment:
  python_version: "3.13.5"
  os: "Debian 12 (Raspberry Pi)"
  dependencies: []
  domain: "domain_2"

analysis:
  root_cause: |
    main.py run_service() function (line 290-294):
    
    ```python
    state_monitor = StateMonitor(config_manager, access_point, web_server_manager)
    
    # Start StateMonitor
    logger.debug("Starting StateMonitor")
    monitor_task = asyncio.create_task(state_monitor.monitoring_loop())
    ```
    
    Directly calls monitoring_loop() without calling initialize() first.
    
    StateMonitor.__init__ sets self.shutdown_event = None (line 73).
    
    StateMonitor.initialize() (line 77-95) creates shutdown_event:
    ```python
    self.shutdown_event = asyncio.Event()
    ```
    
    But initialize() never called, so shutdown_event stays None.
    
    monitoring_loop() line 105:
    ```python
    while not self.shutdown_event.is_set():
    ```
    
    Attempts to call .is_set() on None, raises AttributeError.
    
    Exception caught by asyncio task, loop exits immediately.
    No error logged because exception happens in background task.
    
  technical_notes: |
    Design flaw: StateMonitor has separate __init__ and initialize() methods,
    but caller doesn't know to call both.
    
    Better pattern: __init__ should be complete initialization, or initialize()
    should be called automatically.
    
    Current logs show "Monitoring loop started" (line 105) but nothing after,
    confirming loop exits immediately after that log message.
    
  related_issues: []

resolution:
  assigned_to: "Claude Code"
  target_date: "2025-12-23"
  approach: |
    Option 1 (Recommended): Call initialize() in main.py before monitoring_loop()
    
    main.py line 290-294:
    ```python
    state_monitor = StateMonitor(config_manager, access_point, web_server_manager)
    
    # Initialize StateMonitor
    logger.debug("Initializing StateMonitor")
    await state_monitor.initialize()
    
    # Start monitoring (already started by initialize())
    logger.debug("StateMonitor initialized and monitoring")
    ```
    
    Note: initialize() already creates and starts monitoring_task internally,
    so remove the explicit monitoring_loop() call.
    
    Option 2 (Alternative): Move initialization into __init__
    - Would require making __init__ async
    - More invasive change
    - Not recommended
    
  change_ref: ""
  resolved_date: ""
  resolved_by: ""
  fix_description: ""

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

prevention:
  preventive_measures: |
    - Review all async component initialization patterns
    - Document initialization requirements clearly
    - Add logging for initialization completion
    - Consider removing two-phase initialization pattern
  process_improvements: |
    - Integration tests should verify monitoring activity
    - Hardware validation should check for expected log patterns
    - Silent failures should be detected and logged

verification_enhanced:
  verification_steps:
    - "Deploy fix to Pi"
    - "Restart service"
    - "Monitor logs for 5 minutes"
    - "Verify connection checks appear every 30 seconds"
    - "Verify state detection occurs"
    - "Check failure count increments if disconnected"
  verification_results: ""

traceability:
  design_refs:
    - "design-0002-statemonitor.md"
    - "design-0006-servicecontroller.md"
  change_refs: []
  test_refs: []

notes: |
  Critical bug blocking all hardware validation. System appears operational
  but monitoring completely non-functional.
  
  Bug existed since StateMonitor implementation but masked by previous issues.
  Only visible now with DEBUG logging enabled.
  
  Fix is straightforward: call initialize() before using monitoring_loop().

version_history:
  - version: "1.0"
    date: "2025-12-23"
    author: "Claude Desktop"
    changes:
      - "Initial issue creation from hardware validation findings"
      - "Identified missing initialize() call in main.py"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
