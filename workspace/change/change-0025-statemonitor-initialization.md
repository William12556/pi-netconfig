Created: 2025 December 23

```yaml
change_info:
  id: "change-0025"
  title: "Call StateMonitor.initialize() before starting monitoring"
  date: "2025-12-23"
  author: "Claude Desktop"
  status: "proposed"
  priority: "critical"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0025"
    issue_iteration: 1

source:
  type: "issue"
  reference: "workspace/issue/issue-0025-statemonitor-initialization.md"
  description: "StateMonitor.initialize() never called, causing monitoring loop to fail silently"

scope:
  summary: "Add StateMonitor.initialize() call in main.py run_service() function"
  affected_components:
    - name: "ServiceController"
      file_path: "src/pi_netconfig/main.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-0006-servicecontroller.md"
      sections:
        - "Component initialization"
  out_of_scope:
    - "StateMonitor internal implementation"
    - "Monitoring loop logic"

rational:
  problem_statement: |
    main.py creates StateMonitor then directly calls monitoring_loop(),
    skipping initialize(). This leaves shutdown_event as None, causing
    monitoring loop to fail immediately with AttributeError.
  proposed_solution: |
    Call StateMonitor.initialize() after construction and before any
    monitoring operations. Remove explicit monitoring_loop() call since
    initialize() starts monitoring internally.
  alternatives_considered:
    - option: "Move initialization into __init__"
      reason_rejected: "__init__ cannot be async, would require major refactor"
    - option: "Make shutdown_event optional"
      reason_rejected: "Masks design flaw, doesn't fix root cause"
  benefits:
    - "Fixes critical monitoring failure"
    - "Follows designed initialization pattern"
    - "Minimal code change"
  risks:
    - risk: "None - restores intended behavior"
      mitigation: "N/A"

technical_details:
  current_behavior: |
    Lines 288-294 in main.py:
    ```python
    # Initialize StateMonitor
    logger.debug("Initializing StateMonitor")
    state_monitor = StateMonitor(config_manager, access_point, web_server_manager)
    
    # Start StateMonitor
    logger.debug("Starting StateMonitor")
    monitor_task = asyncio.create_task(state_monitor.monitoring_loop())
    ```
    
    Result: shutdown_event remains None, monitoring fails
  proposed_behavior: |
    Modified lines 288-295:
    ```python
    # Initialize StateMonitor
    logger.debug("Initializing StateMonitor")
    state_monitor = StateMonitor(config_manager, access_point, web_server_manager)
    await state_monitor.initialize()
    
    logger.debug("StateMonitor initialized and monitoring started")
    ```
    
    Result: shutdown_event created, monitoring functions correctly
  implementation_approach: |
    1. Add await state_monitor.initialize() after StateMonitor construction
    2. Remove explicit monitoring_loop() call (initialize handles it)
    3. Update log messages for clarity
    4. Remove monitor_task variable (no longer needed)
    5. Update graceful_shutdown to use state_monitor.monitoring_task
  code_changes:
    - component: "ServiceController"
      file: "src/pi_netconfig/main.py"
      change_summary: "Add initialize() call, remove redundant monitoring_loop() call"
      functions_affected:
        - "run_service"
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Hardware validation with log monitoring"
  test_cases:
    - scenario: "Service startup"
      expected_result: "initialize() completes, monitoring starts"
    - scenario: "30 seconds runtime"
      expected_result: "Connection check logged"
    - scenario: "5 minutes runtime"
      expected_result: "Multiple connection checks logged"
  regression_scope:
    - "Service startup"
    - "Signal handling"
    - "Graceful shutdown"
  validation_criteria:
    - "Connection checks appear every 30 seconds"
    - "State transitions occur based on connectivity"
    - "No AttributeError in logs"

implementation:
  effort_estimate: "15 minutes"
  implementation_steps:
    - step: "Modify main.py lines 288-294: add initialize() call"
      owner: "Claude Code"
    - step: "Remove explicit monitoring_loop() call"
      owner: "Claude Code"
    - step: "Update log messages"
      owner: "Claude Code"
    - step: "Verify graceful_shutdown references correct task"
      owner: "Claude Code"
  rollback_procedure: "Reinstall version 0.2.6"
  deployment_notes: "Version 0.2.7, critical fix"

verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []

traceability:
  design_updates:
    - design_ref: "design-0006-servicecontroller.md"
      sections_updated:
        - "Component initialization sequence"
      update_date: ""
  related_changes: []
  related_issues:
    - issue_ref: "issue-0025"
      relationship: "resolves"

notes: |
  Critical fix blocking all monitoring functionality. Simple change with
  high impact - restores entire StateMonitor operation.
  
  StateMonitor.initialize() already creates monitoring_task internally,
  so explicit monitoring_loop() call was redundant and incorrect.

version_history:
  - version: "1.0"
    date: "2025-12-23"
    author: "Claude Desktop"
    changes:
      - "Initial change specification for initialize() fix"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
