# T02 Change Template v1.0 - YAML Format
# Optimized for LM code generation context efficiency

change_info:
  id: "change-0027"
  title: "Correct WebServer module import paths with accurate module names"
  date: "2026-01-07"
  author: "Claude Desktop"
  status: "proposed"
  priority: "critical"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0027"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-0027-webserver-imports-incorrect-module-names.md"
  description: "Fix incomplete change-0026 implementation - correct both package paths and module name format"

scope:
  summary: "Replace incorrect flat imports with package-qualified imports using correct single-word module names"
  affected_components:
    - name: "WebServer"
      file_path: "src/pi_netconfig/webserver.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-0003-component_webserver_webserver.md"
      sections:
        - "Implementation Details"
  out_of_scope:
    - "No changes to API handler logic"
    - "No changes to web server configuration"
    - "No changes to HTML/JavaScript frontend"

rational:
  problem_statement: "WebServer imports use incorrect flat paths AND incorrect snake_case module names (connection_manager, state_monitor) when actual modules are single-word (connectionmanager, statemonitor)"
  proposed_solution: "Replace imports with package-qualified paths using correct module names matching filesystem"
  alternatives_considered:
    - option: "Rename module files to match snake_case import expectations"
      reason_rejected: "Would break all existing imports throughout codebase"
  benefits:
    - "Restores web configuration interface functionality"
    - "Aligns imports with actual module filesystem structure"
    - "Corrects previous incomplete fix"
  risks:
    - risk: "None - straightforward correction"
      mitigation: "N/A"

technical_details:
  current_behavior: "Line 303 has 'from connection_manager import ConnectionManager' - Line 317 has 'from state_monitor import StateMonitor'"
  proposed_behavior: "Line 303 has 'from pi_netconfig.connectionmanager import ConnectionManager' - Line 317 has 'from pi_netconfig.statemonitor import StateMonitor'"
  implementation_approach: "Use str_replace tool with exact string matching of current incorrect imports"
  code_changes:
    - component: "WebServer"
      file: "src/pi_netconfig/webserver.py"
      change_summary: "Correct two import statements with proper package path and module name"
      functions_affected:
        - "handle_scan_request"
        - "handle_status_request"
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal:
    - component: "connectionmanager"
      impact: "None - module already exists with correct name"
    - component: "statemonitor"
      impact: "None - module already exists with correct name"
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Integration test on Raspberry Pi hardware in AP mode"
  test_cases:
    - scenario: "Network scan via /api/scan endpoint"
      expected_result: "HTTP 200 response with JSON network list"
    - scenario: "Status query via /api/status endpoint"
      expected_result: "HTTP 200 response with JSON system status"
  regression_scope:
    - "Verify web server starts successfully"
    - "Verify HTML page loads"
    - "Verify all API endpoints return valid responses"
  validation_criteria:
    - "No ModuleNotFoundError exceptions in logs"
    - "API endpoints return HTTP 200 responses"
    - "Network scan returns valid network list"
    - "Status query returns valid system state"

implementation:
  effort_estimate: "10 minutes"
  implementation_steps:
    - step: "Line 303: Replace 'from connection_manager import ConnectionManager' with 'from pi_netconfig.connectionmanager import ConnectionManager'"
      owner: "Claude Code"
    - step: "Line 317: Replace 'from state_monitor import StateMonitor' with 'from pi_netconfig.statemonitor import StateMonitor'"
      owner: "Claude Code"
    - step: "Verify no other incorrect imports exist in webserver.py"
      owner: "Claude Code"
  rollback_procedure: "Revert to previous version via git"
  deployment_notes: "Requires rebuild and reinstall of pi-netconfig package on Raspberry Pi"

verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-0026"
      relationship: "corrects"
  related_issues:
    - issue_ref: "issue-0027"
      relationship: "resolves"
    - issue_ref: "issue-0026"
      relationship: "related"

notes: "Critical fix - previous change-0026 was not implemented correctly by Claude Code"

version_history:
  - version: "1.0"
    date: "2026-01-07"
    author: "Claude Desktop"
    changes:
      - "Initial change document creation"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
