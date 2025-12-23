Created: 2025 December 04

# change-0020-main-integration-errors.md

```yaml
change_info:
  id: "change-0020"
  title: "Fix main.py integration errors"
  date: "2025-12-04"
  author: "Claude Desktop"
  status: "proposed"
  priority: "critical"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0020"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-0020-main-integration-errors.md"
  description: "Two critical bugs prevent service startup: wrong module name in installer, missing StateMonitor dependencies in main"

scope:
  summary: "Fix installer module name generation and add proper component initialization in main.py"
  affected_components:
    - name: "Installer"
      file_path: "src/pi_netconfig/installer.py"
      change_type: "modify"
    - name: "Main"
      file_path: "src/pi_netconfig/main.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-0001-installer.md"
      sections:
        - "§3.5 Systemd Unit Generation"
    - design_ref: "design-0007-service-controller.md"
      sections:
        - "§3.3 Component Initialization"
  out_of_scope:
    - "Configuration file handling"
    - "Logging enhancements"

rational:
  problem_statement: "Service fails to start: (1) systemd tries to run non-existent service_controller module, (2) StateMonitor instantiated without required ConnectionManager, APManager, WebServer dependencies"
  proposed_solution: "Change installer to generate 'pi_netconfig.main' module name. Add component initialization sequence in main.py before StateMonitor creation"
  alternatives_considered:
    - option: "Rename main.py to service_controller.py"
      reason_rejected: "Breaking change, requires package structure updates, no benefit"
  benefits:
    - "Service starts successfully on hardware"
    - "Proper dependency injection"
    - "Matches actual package structure"
  risks:
    - risk: "Component initialization order dependencies"
      mitigation: "Follow design specifications for initialization sequence"

technical_details:
  current_behavior: "Installer generates ExecStart with service_controller module. Main.py creates StateMonitor() with no arguments"
  proposed_behavior: "Installer generates ExecStart with main module. Main.py creates all components in correct order, passes to StateMonitor"
  implementation_approach: |
    Fix 1 - installer.py line ~100:
    Change: ExecStart={venv_python} -m pi_netconfig.service_controller
    To: ExecStart={venv_python} -m pi_netconfig.main
    
    Fix 2 - main.py:
    Before StateMonitor instantiation, add:
    1. connection_manager = ConnectionManager()
    2. ap_manager = APManager()
    3. web_server = WebServer(connection_manager)
    4. state_monitor = StateMonitor(connection_manager, ap_manager, web_server)
  code_changes:
    - component: "Installer"
      file: "src/pi_netconfig/installer.py"
      change_summary: "Change module name in systemd unit generation"
      functions_affected:
        - "SystemdInstaller.generate_venv_systemd_unit()"
      classes_affected: []
    - component: "Main"
      file: "src/pi_netconfig/main.py"
      change_summary: "Add component initialization before StateMonitor"
      functions_affected:
        - "run_service()"
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal:
    - component: "ConnectionManager"
      impact: "Must instantiate before StateMonitor"
    - component: "APManager"
      impact: "Must instantiate before StateMonitor"
    - component: "WebServer"
      impact: "Must instantiate before StateMonitor, requires ConnectionManager"
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Hardware validation on Raspberry Pi"
  test_cases:
    - scenario: "Fresh installation"
      expected_result: "Service starts, no module errors, no instantiation errors"
    - scenario: "Service restart"
      expected_result: "Clean shutdown, successful restart"
    - scenario: "Boot persistence"
      expected_result: "Service starts on boot"
  regression_scope:
    - "All existing unit tests"
  validation_criteria:
    - "Service file contains correct module name"
    - "Service status shows active (running)"
    - "No errors in journalctl logs"
    - "State detection works (CLIENT or AP_MODE)"

implementation:
  effort_estimate: "2 hours"
  implementation_steps:
    - step: "Fix installer.py module name"
      owner: "Claude Code"
    - step: "Add component initialization to main.py"
      owner: "Claude Code"
    - step: "Build and deploy to Pi"
      owner: "Human"
    - step: "Hardware validation"
      owner: "Human"
  rollback_procedure: "Revert to 0.2.1, manual service file fix"
  deployment_notes: "Version 0.2.2. Clean installation recommended (remove old service file first)"

verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []

traceability:
  design_updates:
    - design_ref: "design-0001-installer.md"
      sections_updated:
        - "§3.5 Systemd Unit Generation - correct module name"
      update_date: ""
    - design_ref: "design-0007-service-controller.md"
      sections_updated:
        - "§3.3 Component Initialization - dependency order"
      update_date: ""
  related_changes: []
  related_issues:
    - issue_ref: "issue-0020"
      relationship: "resolves"

notes: |
  Critical fixes for deployment blocker.
  
  Component initialization order matters: ConnectionManager first (no deps), APManager second (no deps), WebServer third (needs ConnectionManager), StateMonitor last (needs all three).

version_history:
  - version: "1.0"
    date: "2025-12-04"
    author: "Claude Desktop"
    changes:
      - "Initial change document from issue-0020"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-04 | Claude Desktop | Initial change document from issue-0020 |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
