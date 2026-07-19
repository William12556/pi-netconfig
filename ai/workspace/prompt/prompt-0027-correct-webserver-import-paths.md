# T04 Prompt Template v1.0 - YAML Format
# Optimized for Claude Desktop → Claude Code filesystem communication
# Designed for minimal token usage while maintaining completeness

prompt_info:
  id: "prompt-0027"
  task_type: "debug"
  source_ref: "change-0027-correct-webserver-import-paths.md"
  date: "2026-01-07"
  priority: "critical"
  iteration: 1
  coupled_docs:
    change_ref: "change-0027"
    change_iteration: 1

context:
  purpose: "Correct incomplete fix from prompt-0026 - imports still use flat paths AND incorrect module names"
  integration: "WebServer component provides HTTP configuration interface; depends on connectionmanager and statemonitor modules (single-word names)"
  knowledge_references: []
  constraints:
    - "Actual module filenames: connectionmanager.py and statemonitor.py (NOT connection_manager.py or state_monitor.py)"
    - "Must use package-qualified imports: pi_netconfig.connectionmanager and pi_netconfig.statemonitor"
    - "Cannot modify any other code"

specification:
  description: "Fix two imports that currently use flat paths with incorrect snake_case module names"
  requirements:
    functional:
      - "Line 303: Replace 'from connection_manager import ConnectionManager' with 'from pi_netconfig.connectionmanager import ConnectionManager'"
      - "Line 317: Replace 'from state_monitor import StateMonitor' with 'from pi_netconfig.statemonitor import StateMonitor'"
      - "Verify actual module names in filesystem: connectionmanager.py (not connection_manager.py), statemonitor.py (not state_monitor.py)"
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Use exact module names from filesystem: connectionmanager, statemonitor (single words)"
        - "Use package-qualified imports: from pi_netconfig.modulename import ClassName"
        - "Preserve exact indentation and formatting"
        - "Do not modify any other code"
  performance: []

design:
  architecture: "Direct string replacement in source file"
  components:
    - name: "webserver.py"
      type: "module"
      purpose: "HTTP server providing configuration API endpoints"
      interface:
        inputs:
          - name: "import statements"
            type: "string"
            description: "Two incorrect imports requiring correction"
        outputs:
          type: "corrected source file"
          description: "webserver.py with properly qualified imports using correct module names"
        raises: []
      logic:
        - "Verify actual module filenames in src/pi_netconfig/ directory"
        - "Line 303: Replace entire import statement with correct package-qualified path and module name"
        - "Line 317: Replace entire import statement with correct package-qualified path and module name"
  dependencies:
    internal:
      - "pi_netconfig.connectionmanager (file: connectionmanager.py)"
      - "pi_netconfig.statemonitor (file: statemonitor.py)"
    external: []

data_schema:
  entities: []

error_handling:
  strategy: "Verify exact string match before replacement; confirm module files exist in filesystem"
  exceptions: []
  logging:
    level: "Not applicable"
    format: "Not applicable"

testing:
  unit_tests: []
  edge_cases:
    - "Verify only targeted import statements modified"
    - "Ensure no whitespace changes"
    - "Confirm module names match actual filesystem"
  validation:
    - "Check src/pi_netconfig/connectionmanager.py exists (not connection_manager.py)"
    - "Check src/pi_netconfig/statemonitor.py exists (not state_monitor.py)"
    - "Verify import statements syntactically correct"

deliverable:
  format_requirements:
    - "Use str_replace tool to modify existing file"
    - "Match old_str exactly including whitespace"
    - "Use correct single-word module names from filesystem"
  files:
    - path: "src/pi_netconfig/webserver.py"
      content: "Corrected import statements at lines 303 and 317"

success_criteria:
  - "Line 303 contains: from pi_netconfig.connectionmanager import ConnectionManager"
  - "Line 317 contains: from pi_netconfig.statemonitor import StateMonitor"
  - "Module names match actual filesystem: connectionmanager.py, statemonitor.py"
  - "No other code modified"
  - "File syntax valid Python"

notes: "CRITICAL: Previous prompt-0026 fix was incomplete. Actual modules are connectionmanager.py and statemonitor.py (single words), NOT connection_manager.py or state_monitor.py. Verify filesystem structure before constructing imports."

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
