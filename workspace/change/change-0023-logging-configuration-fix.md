Created: 2025 December 05

```yaml
change_info:
  id: "change-0023"
  title: "Fix logging configuration bugs"
  date: "2025-12-05"
  author: "Claude Desktop"
  status: "proposed"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0023"
    issue_iteration: 1

source:
  type: "issue"
  reference: "workspace/issue/issue-0023-logging-configuration-bugs.md"
  description: "Hardware validation revealed logging configuration prevents debug output due to environment variable mismatch and inverted debug mode logic"

scope:
  summary: "Correct logging configuration to enable DEBUG level output and fix environment variable name"
  affected_components:
    - name: "ServiceController"
      file_path: "src/pi_netconfig/main.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-0006-servicecontroller.md"
      sections:
        - "Logging Configuration"
  out_of_scope:
    - "StateMonitor logging implementation (already correct)"
    - "Installer logging configuration"

rational:
  problem_statement: |
    Two bugs prevent debug logging:
    1. Code checks PI_NETCONFIG_DEBUG but systemd sets DEBUG_MODE
    2. Both debug_mode branches result in INFO level only
    
    Impact: StateMonitor monitoring_loop() silent, blocks hardware validation
  proposed_solution: |
    1. Standardize on DEBUG_MODE environment variable
    2. Set root logger to DEBUG when debug_mode=True
    3. Remove unnecessary filter logic
  alternatives_considered:
    - option: "Change systemd to use PI_NETCONFIG_DEBUG"
      reason_rejected: "DEBUG_MODE more conventional, matches design spec variable naming"
    - option: "Add separate handler for debug messages"
      reason_rejected: "Unnecessary complexity, level setting sufficient"
  benefits:
    - "Enables hardware validation visibility"
    - "Matches design specification requirements"
    - "Simplifies logging configuration code"
  risks:
    - risk: "Increased log volume in debug mode"
      mitigation: "Expected behavior per design, rotation prevents disk issues"

technical_details:
  current_behavior: |
    Line 148: Checks PI_NETCONFIG_DEBUG (mismatched with systemd)
    Line 156: Sets root logger to INFO always
    Lines 165-167: Both branches result in INFO level
    
    Result: No debug messages regardless of DEBUG_MODE value
  proposed_behavior: |
    Line 148: Check DEBUG_MODE environment variable
    Line 156: Set root logger level based on debug_mode flag
    Lines 165-167: Set file handler level based on debug_mode flag
    
    Result: DEBUG messages appear when DEBUG_MODE=true
  implementation_approach: |
    Modify configure_logging() function:
    1. Change environment variable check
    2. Set root logger level conditionally
    3. Set file handler level conditionally
    4. Remove filter logic
  code_changes:
    - component: "ServiceController"
      file: "src/pi_netconfig/main.py"
      change_summary: "Fix logging configuration bugs"
      functions_affected:
        - "configure_logging"
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Progressive validation: minimal fix verification, then hardware validation"
  test_cases:
    - scenario: "Debug mode enabled"
      expected_result: "Root logger level DEBUG, debug messages appear in log"
    - scenario: "Debug mode disabled"
      expected_result: "Root logger level INFO, only INFO+ messages in log"
    - scenario: "StateMonitor monitoring_loop"
      expected_result: "Debug messages visible: 'Monitoring loop started', connection checks"
  regression_scope:
    - "Service startup in all modes (bootstrap/service/manual)"
    - "Log rotation functionality"
    - "Signal handler operation"
  validation_criteria:
    - "Log shows correct level in configuration message"
    - "StateMonitor debug output appears"
    - "CLIENT mode validation can proceed"

implementation:
  effort_estimate: "30 minutes"
  implementation_steps:
    - step: "Modify line 148: Change PI_NETCONFIG_DEBUG to DEBUG_MODE, default 'false'"
      owner: "Claude Code"
    - step: "Modify line 156: Set root logger level conditionally"
      owner: "Claude Code"
    - step: "Modify lines 165-167: Set file handler level conditionally, remove filter"
      owner: "Claude Code"
    - step: "Update line 174 log message to show actual level"
      owner: "Claude Code"
  rollback_procedure: "Reinstall version 0.2.4 wheel"
  deployment_notes: "Version 0.2.5, requires service restart after deployment"

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
        - "Environment Variables (standardize on DEBUG_MODE)"
      update_date: ""
  related_changes: []
  related_issues:
    - issue_ref: "issue-0023"
      relationship: "resolves"

notes: |
  Change required for hardware validation to proceed. Without debug output,
  cannot verify CLIENT mode operation or state transitions.
  
  Environment variable standardization important for consistency with installer
  and design documentation.

version_history:
  - version: "1.0"
    date: "2025-12-05"
    author: "Claude Desktop"
    changes:
      - "Initial change specification from issue-0023"
      - "Defined two-part fix: environment variable and logic correction"
      - "Specified progressive validation approach"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
