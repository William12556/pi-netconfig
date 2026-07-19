# T03 Issue Template v1.0 - YAML Format
# Optimized for LM code generation context efficiency

issue_info:
  id: "issue-0027"
  title: "WebServer imports not corrected - incorrect module names used"
  date: "2026-01-07"
  reporter: "Human"
  status: "open"
  severity: "critical"
  type: "bug"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

source:
  origin: "test_result"
  test_ref: "AP mode test execution"
  description: "Claude Code did not implement change-0026 correctly - imports still use flat paths with incorrect module names"

affected_scope:
  components:
    - name: "WebServer"
      file_path: "src/pi_netconfig/webserver.py"
  designs:
    - design_ref: "design-0003-component_webserver_webserver.md"
  version: "Latest deployment"

reproduction:
  prerequisites: "System in AP mode with web server active"
  steps:
    - "Access /api/scan endpoint"
    - "Access /api/status endpoint"
  frequency: "always"
  reproducibility_conditions: "Any API request requiring ConnectionManager or StateMonitor"
  preconditions: "Web server running in AP mode"
  test_data: "HTTP GET requests to API endpoints"
  error_output: |
    Line 303 error:
    ModuleNotFoundError: No module named 'connection_manager'
    from connection_manager import ConnectionManager
    
    Line 317 error:
    ModuleNotFoundError: No module named 'state_monitor'
    from state_monitor import StateMonitor

behavior:
  expected: "API handlers successfully import modules and return valid responses"
  actual: "ModuleNotFoundError exceptions - imports fail"
  impact: "Complete failure of web configuration interface - all API endpoints non-functional"
  workaround: "None - requires code correction"

environment:
  python_version: "3.13.5"
  os: "Debian GNU/Linux 13 (trixie)"
  dependencies:
    - library: "pi_netconfig"
      version: "Latest build"
  domain: "domain_2"

analysis:
  root_cause: "Claude Code fix was incomplete - two errors persist: (1) imports still use flat paths without package qualification, (2) imports use snake_case module names (connection_manager, state_monitor) but actual modules are single-word (connectionmanager, statemonitor)"
  technical_notes: |
    Actual module structure:
    - src/pi_netconfig/connectionmanager.py (not connection_manager.py)
    - src/pi_netconfig/statemonitor.py (not state_monitor.py)
    
    Line 303 currently has: from connection_manager import ConnectionManager
    Line 303 requires: from pi_netconfig.connectionmanager import ConnectionManager
    
    Line 317 currently has: from state_monitor import StateMonitor
    Line 317 requires: from pi_netconfig.statemonitor import StateMonitor
  related_issues:
    - issue_ref: "issue-0026"
      relationship: "related"

resolution:
  assigned_to: "Claude Code"
  target_date: "2026-01-07"
  approach: "Correct both package path and module name format in imports"
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
  preventive_measures: "Verify actual module filenames before constructing import statements"
  process_improvements: "Include verification step in fix validation - confirm imports match actual filesystem structure"

verification_enhanced:
  verification_steps:
    - "Deploy corrected build to Raspberry Pi"
    - "Trigger AP mode activation"
    - "Execute curl requests to /api/scan and /api/status"
    - "Verify HTTP 200 responses with valid JSON"
    - "Check logs for absence of ModuleNotFoundError"
  verification_results: ""

traceability:
  design_refs:
    - "design-0003-component_webserver_webserver.md"
  change_refs:
    - "change-0026"
  test_refs:
    - "AP mode integration test"

notes: "Original prompt-0026 was ambiguous - specified line numbers and changes but did not emphasize verification against actual filesystem structure"

version_history:
  - version: "1.0"
    date: "2026-01-07"
    author: "Claude Desktop"
    changes:
      - "Initial issue document creation"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
