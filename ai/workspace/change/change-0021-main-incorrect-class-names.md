Created: 2025 December 04

# change-0021-main-incorrect-class-names.md

```yaml
change_info:
  id: "change-0021"
  title: "Fix main.py class name imports and instantiation"
  date: "2025-12-04"
  author: "Claude Desktop"
  status: "proposed"
  priority: "critical"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0021"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-0021-main-incorrect-class-names.md"
  description: "Main.py imports non-existent class names causing import failure"

scope:
  summary: "Correct class names in imports and instantiation to match actual source files"
  affected_components:
    - name: "Main"
      file_path: "src/pi_netconfig/main.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-0007-service-controller.md"
      sections:
        - "§3.3 Component Initialization"
  out_of_scope: []

rational:
  problem_statement: "main.py imports ConnectionManager, APManager, WebServer - none exist. Actual classes: ConfigManager, AccessPoint, WebServerManager"
  proposed_solution: "Change imports and variable names to match actual class names"
  alternatives_considered: []
  benefits:
    - "Service can start"
    - "Imports succeed"
  risks: []

technical_details:
  current_behavior: "ImportError on startup"
  proposed_behavior: "Successful import and instantiation"
  implementation_approach: |
    Line 28-29: Fix imports
    Line 290-292: Fix instantiation
    Line 293: Fix StateMonitor arguments
  code_changes:
    - component: "Main"
      file: "src/pi_netconfig/main.py"
      change_summary: "Correct class names"
      functions_affected:
        - "run_service()"
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal:
    - component: "ConfigManager"
      impact: "Correct class imported"
    - component: "AccessPoint"
      impact: "Correct class imported"
    - component: "WebServerManager"
      impact: "Correct class imported"
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Hardware validation on Raspberry Pi"
  test_cases:
    - scenario: "Service startup"
      expected_result: "No import errors, service runs"
  regression_scope:
    - "All unit tests"
  validation_criteria:
    - "Service starts successfully"
    - "No import errors"

implementation:
  effort_estimate: "30 minutes"
  implementation_steps:
    - step: "Fix imports and instantiation in main.py"
      owner: "Claude Code"
  rollback_procedure: "Revert to 0.2.2"
  deployment_notes: "Version 0.2.3"

verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []

traceability:
  design_updates:
    - design_ref: "design-0007-service-controller.md"
      sections_updated:
        - "§3.3 Component Initialization"
      update_date: ""
  related_changes: []
  related_issues:
    - issue_ref: "issue-0021"
      relationship: "resolves"

notes: |
  Correct mappings:
  ConnectionManager → ConfigManager
  APManager → AccessPoint
  WebServer → WebServerManager
  
  Also update variable names for consistency:
  connection_manager → config_manager
  ap_manager → access_point
  web_server → web_server_manager

version_history:
  - version: "1.0"
    date: "2025-12-04"
    author: "Claude Desktop"
    changes:
      - "Initial change document from issue-0021"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-04 | Claude Desktop | Initial change document from issue-0021 |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
