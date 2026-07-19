Created: 2025 December 04

# prompt-0021-main-incorrect-class-names.md

```yaml
prompt_info:
  id: "prompt-0021"
  task_type: "code_generation"
  source_ref: "change-0021-main-incorrect-class-names.md"
  date: "2025-12-04"
  priority: "critical"
  iteration: 1
  coupled_docs:
    change_ref: "change-0021"
    change_iteration: 1

context:
  purpose: "Fix import errors by correcting class names to match actual source files"
  integration: "Main.py is service entry point, imports and initializes all components"
  knowledge_references: []
  constraints:
    - "Use exact class names from source files"
    - "Preserve all functionality"

specification:
  description: "Correct class names in imports and instantiation"
  requirements:
    functional:
      - "Change ConnectionManager → ConfigManager"
      - "Change APManager → AccessPoint"
      - "Change WebServer → WebServerManager"
      - "Update variable names for consistency"
      - "Update StateMonitor arguments"
    technical:
      language: "Python"
      version: "3.9+"
      standards:
        - "No breaking changes"
  performance: []

design:
  architecture: "Simple find-replace operation in main.py"
  components:
    - name: "Import corrections"
      type: "module import"
      purpose: "Import actual classes"
      interface:
        inputs: []
        outputs: []
        raises: []
      logic:
        - "Line 28: from pi_netconfig.connectionmanager import ConfigManager"
        - "Line 29: from pi_netconfig.apmanager import AccessPoint"
        - "Add line 30: from pi_netconfig.webserver import WebServerManager"
    - name: "Instantiation corrections"
      type: "function"
      purpose: "Create component instances"
      interface:
        inputs: []
        outputs: []
        raises: []
      logic:
        - "Line 290: config_manager = ConfigManager()"
        - "Line 291: access_point = AccessPoint()"
        - "Line 292: web_server_manager = WebServerManager(config_manager)"
        - "Line 293: state_monitor = StateMonitor(config_manager, access_point, web_server_manager)"
  dependencies:
    internal:
      - "ConfigManager"
      - "AccessPoint"
      - "WebServerManager"
      - "StateMonitor"
    external: []

data_schema:
  entities: []

error_handling:
  strategy: "No changes to error handling"
  exceptions: []
  logging:
    level: "unchanged"
    format: "unchanged"

testing:
  unit_tests:
    - scenario: "Hardware validation"
      expected: "Service starts"
  edge_cases: []
  validation:
    - "Deploy to Pi and verify startup"

deliverable:
  format_requirements:
    - "Modify src/pi_netconfig/main.py only"
  files:
    - path: "src/pi_netconfig/main.py"
      content: "Correct imports and variable names"

success_criteria:
  - "No import errors"
  - "Service starts successfully"

notes: |
  Changes required in main.py:
  
  Line 28-30 (imports):
  CURRENT:
  from pi_netconfig.connectionmanager import ConnectionManager
  from pi_netconfig.apmanager import APManager
  
  FIXED:
  from pi_netconfig.connectionmanager import ConfigManager
  from pi_netconfig.apmanager import AccessPoint
  from pi_netconfig.webserver import WebServerManager
  
  Line 290-293 (instantiation in run_service function):
  CURRENT:
  connection_manager = ConnectionManager()
  ap_manager = APManager()
  web_server = WebServer(connection_manager)
  state_monitor = StateMonitor(connection_manager, ap_manager, web_server)
  
  FIXED:
  config_manager = ConfigManager()
  access_point = AccessPoint()
  web_server_manager = WebServerManager(config_manager)
  state_monitor = StateMonitor(config_manager, access_point, web_server_manager)

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-04 | Claude Desktop | Initial prompt from change-0021 |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
