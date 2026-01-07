# T03 Issue Template v1.0 - YAML Format
# Optimized for LM code generation context efficiency

issue_info:
  id: "issue-0026"
  title: "WebServer module import errors in API handlers"
  date: "2026-01-07"
  reporter: "William Watson"
  status: "open"
  severity: "high"
  type: "bug"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

source:
  origin: "user_report"
  test_ref: "AP mode integration test - 2026-01-07"
  description: "Network scan functionality returns HTTP 500 error due to incorrect module import paths in webserver.py"

affected_scope:
  components:
    - name: "WebServer"
      file_path: "src/pi_netconfig/webserver.py"
  designs:
    - design_ref: "design-0003-component_webserver_webserver.md"
  version: "Deployed production version on deb1.local"

reproduction:
  prerequisites: "System in AP_MODE with web server running on port 8080"
  steps:
    - "Connect to AP (SSID: pi-netconfig-ap)"
    - "Navigate to http://192.168.50.1:8080/"
    - "Click 'Scan Networks' button"
    - "Observe HTTP 500 error"
  frequency: "always"
  reproducibility_conditions: "Any attempt to use /api/scan or /api/status endpoints"
  preconditions: "AP mode active, web server listening on port 8080"
  test_data: "N/A - API endpoint invocation only"
  error_output: |
    2026-01-07 10:26:03,765 ERROR WebServer Scan failed: No module named 'connection_manager'
    Traceback (most recent call last):
      File "/opt/pi-netconfig/venv/lib/python3.13/site-packages/pi_netconfig/webserver.py", line 303, in handle_scan_request
        from connection_manager import ConnectionManager
    ModuleNotFoundError: No module named 'connection_manager'
    
    2026-01-07 10:25:21,173 ERROR WebServer Status query failed: No module named 'state_monitor'
    Traceback (most recent call last):
      File "/opt/pi-netconfig/venv/lib/python3.13/site-packages/pi_netconfig/webserver.py", line 317, in handle_status_request
        from state_monitor import StateMonitor
    ModuleNotFoundError: No module named 'state_monitor'

behavior:
  expected: "API endpoints /api/scan and /api/status return valid JSON responses with network data"
  actual: "API endpoints return HTTP 500 errors with ModuleNotFoundError exceptions"
  impact: "Web configuration interface non-functional - users cannot scan for available networks or configure WiFi via web interface"
  workaround: "None available - web-based configuration is completely broken"

environment:
  python_version: "3.13.5"
  os: "Debian GNU/Linux 13 (trixie) on Raspberry Pi"
  dependencies:
    - library: "pi-netconfig"
      version: "Installed from /opt/pi-netconfig/venv"
  domain: "domain_1"

analysis:
  root_cause: "Incorrect module import paths in webserver.py - using flat module names instead of package-qualified imports"
  technical_notes: |
    Lines 303 and 317 in webserver.py use incorrect import statements:
    
    Current (incorrect):
      from connection_manager import ConnectionManager
      from state_monitor import StateMonitor
    
    Required (correct):
      from pi_netconfig.connectionmanager import ConnectionManager
      from pi_netconfig.statemonitor import StateMonitor
    
    The module structure is src/pi_netconfig/ with:
      - connectionmanager.py (not connection_manager.py)
      - statemonitor.py (not state_monitor.py)
    
    Package-qualified imports are required for proper module resolution.
  related_issues: []

resolution:
  assigned_to: "Claude Code"
  target_date: ""
  approach: "Update import statements in webserver.py to use correct package-qualified module paths"
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
  preventive_measures: "Ensure all imports use package-qualified paths (pi_netconfig.module_name) rather than flat module names"
  process_improvements: "Add import path validation to code review checklist"

verification_enhanced:
  verification_steps:
    - "Deploy fixed code to Raspberry Pi"
    - "Restart pi-netconfig service"
    - "Trigger AP mode"
    - "Connect to AP web interface"
    - "Execute network scan via /api/scan"
    - "Verify scan returns network list without errors"
    - "Execute status query via /api/status"
    - "Verify status returns system state without errors"
  verification_results: ""

traceability:
  design_refs:
    - "design-0003-component_webserver_webserver.md"
  change_refs: []
  test_refs:
    - "AP mode integration test - 2026-01-07"

notes: |
  Web page HTML loads successfully (HTTP 200), indicating basic web server functionality is intact.
  Only API handlers that perform dynamic imports are affected.
  Error manifests immediately on first API call - no transient issues.

version_history:
  - version: "1.0"
    date: "2026-01-07"
    author: "Claude Desktop"
    changes:
      - "Initial issue creation from AP mode test failure"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
