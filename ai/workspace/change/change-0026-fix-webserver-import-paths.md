# T02 Change Template v1.0 - YAML Format
# Optimized for LM code generation context efficiency

change_info:
  id: "change-0026"
  title: "Fix WebServer module import paths"
  date: "2026-01-07"
  author: "Claude Desktop"
  status: "proposed"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0026"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-0026-webserver-module-import-errors.md"
  description: "Correct module import paths in webserver.py API handlers"

scope:
  summary: "Update import statements in webserver.py to use package-qualified module paths"
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
  problem_statement: "WebServer API handlers use incorrect flat module import paths causing ModuleNotFoundError exceptions in production"
  proposed_solution: "Replace flat module imports with package-qualified imports matching actual module structure"
  alternatives_considered:
    - option: "Restructure package to support flat imports"
      reason_rejected: "Would require renaming modules and breaking existing imports throughout codebase"
    - option: "Use relative imports"
      reason_rejected: "Package-qualified imports are more explicit and maintainable"
  benefits:
    - "Restores web configuration interface functionality"
    - "Aligns imports with established package structure"
    - "Prevents similar import errors in future"
  risks:
    - risk: "Potential for similar issues in other files"
      mitigation: "Audit all imports in webserver.py during fix"

technical_details:
  current_behavior: "API handlers fail with ModuleNotFoundError when attempting dynamic imports"
  proposed_behavior: "API handlers successfully import required modules and return valid responses"
  implementation_approach: "Direct string replacement of import statements in webserver.py"
  code_changes:
    - component: "WebServer"
      file: "src/pi_netconfig/webserver.py"
      change_summary: "Update two import statements to use package-qualified paths"
      functions_affected:
        - "handle_scan_request"
        - "handle_status_request"
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Integration test on Raspberry Pi hardware in AP mode"
  test_cases:
    - scenario: "Network scan via /api/scan endpoint"
      expected_result: "Returns JSON list of available networks without errors"
    - scenario: "Status query via /api/status endpoint"
      expected_result: "Returns JSON system status without errors"
  regression_scope:
    - "Verify web server starts successfully"
    - "Verify HTML page loads"
    - "Verify all API endpoints functional"
  validation_criteria:
    - "No ModuleNotFoundError exceptions in logs"
    - "API endpoints return HTTP 200 responses"
    - "Network scan returns valid network list"

implementation:
  effort_estimate: "15 minutes"
  implementation_steps:
    - step: "Line 303: Change 'from connection_manager import ConnectionManager' to 'from pi_netconfig.connectionmanager import ConnectionManager'"
      owner: "Claude Code"
    - step: "Line 317: Change 'from state_monitor import StateMonitor' to 'from pi_netconfig.statemonitor import StateMonitor'"
      owner: "Claude Code"
    - step: "Audit remaining imports in webserver.py for consistency"
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
  related_changes: []
  related_issues:
    - issue_ref: "issue-0026"
      relationship: "resolves"

notes: "Simple fix with high impact - restores critical web configuration functionality"

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
