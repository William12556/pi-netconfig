Created: 2025 December 05

```yaml
issue_info:
  id: "issue-0023"
  title: "Logging configuration bugs prevent debug output"
  date: "2025-12-05"
  reporter: "Claude Desktop"
  status: "open"
  severity: "high"
  type: "bug"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

source:
  origin: "hardware validation"
  test_ref: "audit-0003-code-integration-verification.md"
  description: "Hardware validation revealed StateMonitor.monitoring_loop() produces no log output. Investigation identified two bugs in main.py configure_logging(): (1) environment variable name mismatch, (2) inverted debug mode logic."

affected_scope:
  components:
    - name: "ServiceController"
      file_path: "src/pi_netconfig/main.py"
  designs:
    - design_ref: "design-0006-servicecontroller.md"
  version: "0.2.4"

reproduction:
  prerequisites: "Service running on Raspberry Pi with systemd"
  steps:
    - "Set Environment='DEBUG_MODE=true' in systemd service file"
    - "Start service: sudo systemctl start pi-netconfig"
    - "Monitor logs: sudo tail -f /var/log/pi-netconfig.log"
    - "Observe: Log level remains INFO, no DEBUG messages appear"
    - "Observe: StateMonitor.monitoring_loop() produces no output"
  frequency: "always"
  reproducibility_conditions: "All service executions"
  preconditions: "None"
  test_data: "N/A"
  error_output: |
    Log output shows:
    2025-12-05 10:56:28,984 INFO ServiceController Logging configured: debug_mode=True, level=INFO
    2025-12-05 10:56:29,165 INFO ServiceController Service running, waiting for shutdown signal
    
    No StateMonitor output appears despite monitoring_loop() executing.

behavior:
  expected: |
    When DEBUG_MODE=true:
    - Root logger should set level to DEBUG
    - StateMonitor debug messages should appear in logs
    - Monitoring loop activity visible
  actual: |
    - Log level remains INFO regardless of DEBUG_MODE value
    - StateMonitor.monitoring_loop() silent (uses logger.debug())
    - No visibility into monitoring activity
  impact: |
    - Cannot validate CLIENT mode operation
    - Cannot observe state transitions
    - Cannot debug connection checking
    - Hardware validation blocked
  workaround: "None - StateMonitor uses debug level exclusively for monitoring activity"

environment:
  python_version: "3.13.5"
  os: "Debian 12 (Raspberry Pi)"
  dependencies: []
  domain: "domain_2"

analysis:
  root_cause: |
    Two bugs in main.py configure_logging():
    
    Bug 1 - Environment variable name mismatch (line 148):
    ```python
    debug_mode = os.environ.get('PI_NETCONFIG_DEBUG', 'true').lower() == 'true'
    ```
    Code checks PI_NETCONFIG_DEBUG but systemd service sets DEBUG_MODE.
    
    Bug 2 - Inverted debug mode logic (lines 165-167):
    ```python
    if debug_mode:
        file_handler.setLevel(logging.INFO)
    else:
        file_handler.addFilter(lambda record: record.levelno == logging.INFO)
    ```
    Both branches result in INFO level only:
    - debug_mode=True: Sets level to INFO (should be DEBUG)
    - debug_mode=False: Filters to INFO only (correct)
    
    Root logger always set to INFO (line 156), never DEBUG.
    
  technical_notes: |
    StateMonitor implementation uses logger.debug() for all monitoring activity:
    - Line 105: "Monitoring loop started"
    - Line 111: Connection check details
    - Line 124: Failure count tracking
    
    With log level stuck at INFO, these messages never appear.
    
    Design specification (design-0006) requires:
    - Debug mode: DEBUG, INFO, WARNING, ERROR, CRITICAL
    - Normal mode: INFO, WARNING, ERROR, CRITICAL
    
    Current implementation violates this requirement.
    
  related_issues:
    - issue_ref: "issue-0017"
      relationship: "related"

resolution:
  assigned_to: "Claude Code"
  target_date: "2025-12-05"
  approach: |
    Fix 1 - Standardize environment variable:
    Change line 148 to check DEBUG_MODE:
    ```python
    debug_mode = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
    ```
    
    Fix 2 - Correct debug mode logic:
    Change lines 156 and 165-167:
    ```python
    # Configure root logger with correct level
    root_logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    
    # File handler inherits root level, no additional filter needed
    file_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    ```
    
    Remove filter logic - unnecessary with correct level setting.
    
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
    - Add unit tests for configure_logging() with both debug modes
    - Test environment variable variations
    - Verify actual log level matches expected level
    - Test that debug messages appear when debug_mode=True
  process_improvements: |
    - Document environment variable conventions in design specs
    - Review all environment variable usage for consistency
    - Add logging level verification to integration tests

verification_enhanced:
  verification_steps:
    - "Deploy fix to Pi: sudo /opt/pi-netconfig/venv/bin/pip install --force-reinstall /tmp/pi_netconfig-*.whl"
    - "Set DEBUG_MODE=true in service file"
    - "Restart service: sudo systemctl restart pi-netconfig"
    - "Monitor logs: sudo tail -f /var/log/pi-netconfig.log"
    - "Verify: debug_mode=True, level=DEBUG in configuration message"
    - "Verify: StateMonitor debug messages appear"
    - "Verify: 'Monitoring loop started' message present"
    - "Verify: Connection check details visible"
    - "Test normal mode: Set DEBUG_MODE=false, verify INFO level only"
  verification_results: ""

traceability:
  design_refs:
    - "design-0006-servicecontroller.md"
  change_refs: []
  test_refs: []

notes: |
  Issue discovered during hardware validation per audit-0003 CLIENT mode testing.
  
  Service appears functional (no crashes) but completely silent regarding monitoring
  activity, preventing validation of state detection and connection checking.
  
  Bug severity HIGH due to blocking hardware validation and preventing operational
  visibility in production deployments.

version_history:
  - version: "1.0"
    date: "2025-12-05"
    author: "Claude Desktop"
    changes:
      - "Initial issue creation from hardware validation findings"
      - "Identified two bugs: environment variable mismatch and inverted logic"
      - "Documented impact on validation and operational visibility"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
