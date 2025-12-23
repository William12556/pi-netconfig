Created: 2025 December 04

# issue-0021-main-incorrect-class-names.md

```yaml
issue_info:
  id: "issue-0021"
  title: "Main.py uses incorrect class names causing import failures"
  date: "2025-12-04"
  reporter: "William Watson"
  status: "open"
  severity: "critical"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-0021"
    change_iteration: 1

source:
  origin: "user_report"
  test_ref: ""
  description: "Hardware deployment revealed main.py imports and instantiates non-existent class names"

affected_scope:
  components:
    - name: "Main"
      file_path: "src/pi_netconfig/main.py"
  designs:
    - design_ref: "design-0007-service-controller.md"
  version: "0.2.2"

reproduction:
  prerequisites: "Package 0.2.2 installed on Raspberry Pi"
  steps:
    - "Start service: sudo systemctl start pi-netconfig"
    - "Observe import error"
  frequency: "always"
  reproducibility_conditions: "Any service startup attempt"
  preconditions: "Service installed"
  test_data: "N/A"
  error_output: "ImportError: cannot import name 'ConnectionManager' from 'pi_netconfig.connectionmanager'. Did you mean: 'connectionmanager'?"

behavior:
  expected: "Service imports correct classes: ConfigManager, AccessPoint, WebServerManager"
  actual: "Service attempts to import non-existent classes: ConnectionManager, APManager, WebServer"
  impact: "Service cannot start. Complete deployment failure"
  workaround: "None"

environment:
  python_version: "3.13"
  os: "Debian 12 (Raspberry Pi)"
  dependencies:
    - library: "pi-netconfig"
      version: "0.2.2"
  domain: "domain_2"

analysis:
  root_cause: |
    main.py line 28-29: Incorrect imports
    from pi_netconfig.connectionmanager import ConnectionManager
    from pi_netconfig.apmanager import APManager
    
    main.py line 290-292: Incorrect instantiation
    connection_manager = ConnectionManager()
    ap_manager = APManager()
    web_server = WebServer(connection_manager)
    
    Actual class names in source:
    - ConfigManager (connectionmanager.py)
    - AccessPoint (apmanager.py)
    - WebServerManager (webserver.py)
  technical_notes: "Code generation used incorrect class names. Design specs may specify wrong names or code generator misread specs"
  related_issues:
    - issue_ref: "issue-0020"
      relationship: "related - same root cause (code generation bugs)"

resolution:
  assigned_to: "Claude Code"
  target_date: "2025-12-04"
  approach: |
    Fix imports:
    from pi_netconfig.connectionmanager import ConfigManager
    from pi_netconfig.apmanager import AccessPoint
    from pi_netconfig.webserver import WebServerManager
    
    Fix instantiation:
    config_manager = ConfigManager()
    access_point = AccessPoint()
    web_server_manager = WebServerManager(config_manager)
    state_monitor = StateMonitor(config_manager, access_point, web_server_manager)
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
  preventive_measures: "Verify all imports against actual source files before code generation"
  process_improvements: "Add import validation step to code generation workflow"

verification_enhanced:
  verification_steps:
    - "Build 0.2.3 with corrected class names"
    - "Deploy to Raspberry Pi"
    - "Verify service starts without import errors"
    - "Monitor logs for operational state"
  verification_results: ""

traceability:
  design_refs:
    - "design-0007-service-controller.md"
  change_refs: []
  test_refs: []

notes: "Critical blocker. Service cannot start with current class names"

version_history:
  - version: "1.0"
    date: "2025-12-04"
    author: "Claude Desktop"
    changes:
      - "Initial issue creation from import error analysis"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-04 | Claude Desktop | Initial issue creation from import error analysis |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
