# T04 Prompt Template v1.0 - YAML Format
# Optimized for Claude Desktop → Claude Code filesystem communication
# Designed for minimal token usage while maintaining completeness

prompt_info:
  id: "prompt-0026"
  task_type: "debug"
  source_ref: "change-0026-fix-webserver-import-paths.md"
  date: "2026-01-07"
  priority: "high"
  iteration: 1
  coupled_docs:
    change_ref: "change-0026"
    change_iteration: 1

context:
  purpose: "Correct module import paths in webserver.py API handlers to resolve ModuleNotFoundError exceptions"
  integration: "WebServer component provides HTTP configuration interface in AP mode; depends on ConnectionManager and StateMonitor modules"
  knowledge_references: []
  constraints:
    - "Must use package-qualified imports: pi_netconfig.<module>"
    - "Cannot modify API handler logic or web server functionality"
    - "Must maintain consistency with existing codebase import patterns"

specification:
  description: "Fix two incorrect import statements in webserver.py that use flat module paths instead of package-qualified paths"
  requirements:
    functional:
      - "Update line 303: Change 'from connection_manager import ConnectionManager' to 'from pi_netconfig.connectionmanager import ConnectionManager'"
      - "Update line 317: Change 'from state_monitor import StateMonitor' to 'from pi_netconfig.statemonitor import StateMonitor'"
      - "Verify all other imports in webserver.py use correct package-qualified paths"
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Use package-qualified imports: from pi_netconfig.module import Class"
        - "Preserve exact indentation and code formatting"
        - "Do not modify any other code except import statements"
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
            description: "Two incorrect flat import paths requiring correction"
        outputs:
          type: "corrected source file"
          description: "webserver.py with package-qualified imports"
        raises: []
      logic:
        - "Line 303: Replace 'from connection_manager import ConnectionManager' with 'from pi_netconfig.connectionmanager import ConnectionManager'"
        - "Line 317: Replace 'from state_monitor import StateMonitor' with 'from pi_netconfig.statemonitor import StateMonitor'"
        - "Audit all imports in file to verify package qualification"
  dependencies:
    internal:
      - "pi_netconfig.connectionmanager"
      - "pi_netconfig.statemonitor"
    external: []

data_schema:
  entities: []

error_handling:
  strategy: "Verify exact line matches before replacement to prevent incorrect modifications"
  exceptions: []
  logging:
    level: "Not applicable - simple file edit"
    format: "Not applicable"

testing:
  unit_tests: []
  edge_cases:
    - "Verify only targeted import statements modified"
    - "Ensure no unintended whitespace changes"
  validation:
    - "Confirm file saved to correct path: src/pi_netconfig/webserver.py"
    - "Verify import statements syntactically correct"

deliverable:
  format_requirements:
    - "Use str_replace tool to modify existing file"
    - "Match old_str exactly including whitespace"
    - "Preserve all surrounding code and formatting"
  files:
    - path: "src/pi_netconfig/webserver.py"
      content: "Modified import statements at lines 303 and 317"

success_criteria:
  - "Line 303 contains: from pi_netconfig.connectionmanager import ConnectionManager"
  - "Line 317 contains: from pi_netconfig.statemonitor import StateMonitor"
  - "No other code modified"
  - "File syntax valid Python"

notes: "Critical fix for web configuration interface. Current flat imports cause ModuleNotFoundError in production deployment."

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
