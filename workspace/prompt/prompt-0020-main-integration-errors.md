Created: 2025 December 04

# prompt-0020-main-integration-errors.md

```yaml
prompt_info:
  id: "prompt-0020"
  task_type: "code_generation"
  source_ref: "change-0020-main-integration-errors.md"
  date: "2025-12-04"
  priority: "critical"
  iteration: 1
  coupled_docs:
    change_ref: "change-0020"
    change_iteration: 1

context:
  purpose: "Fix two critical bugs preventing service startup on hardware"
  integration: "Installer generates systemd service file. Main.py is service entry point"
  knowledge_references: []
  constraints:
    - "Preserve all existing functionality"
    - "No breaking changes"
    - "Minimal modifications"

specification:
  description: "Fix installer module name and add component initialization in main.py"
  requirements:
    functional:
      - "Fix 1: Change installer systemd ExecStart to use pi_netconfig.main"
      - "Fix 2: Initialize ConnectionManager, APManager, WebServer before StateMonitor"
      - "Fix 2: Pass all three components to StateMonitor constructor"
    technical:
      language: "Python"
      version: "3.9+"
      standards:
        - "Thread-safe component initialization"
        - "Comprehensive error handling"
        - "Proper dependency injection order"
  performance: []

design:
  architecture: "Two independent fixes in separate files"
  components:
    - name: "installer.py fix"
      type: "function"
      purpose: "Generate correct module name in systemd unit"
      interface:
        inputs:
          - name: "venv_python"
            type: "Path"
            description: "Venv Python executable path"
        outputs:
          type: "str"
          description: "Systemd unit file content"
        raises: []
      logic:
        - "Locate line 172 in generate_venv_systemd_unit()"
        - "Change: ExecStart={venv_python} -m pi_netconfig.service_controller"
        - "To: ExecStart={venv_python} -m pi_netconfig.main"
    - name: "main.py fix"
      type: "function"
      purpose: "Initialize components before StateMonitor"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Async function"
        raises:
          - "ServiceControllerError"
      logic:
        - "Locate line 287: state_monitor = StateMonitor()"
        - "Add before that line:"
        - "connection_manager = ConnectionManager()"
        - "ap_manager = APManager()"  
        - "web_server = WebServer(connection_manager)"
        - "Change line 287 to: state_monitor = StateMonitor(connection_manager, ap_manager, web_server)"
  dependencies:
    internal:
      - "ConnectionManager class"
      - "APManager class"
      - "WebServer class"
      - "StateMonitor class"
    external: []

data_schema:
  entities: []

error_handling:
  strategy: "Preserve existing error handling, no changes needed"
  exceptions: []
  logging:
    level: "DEBUG/INFO"
    format: "Existing logging unchanged"

testing:
  unit_tests:
    - scenario: "Hardware validation only"
      expected: "Service starts, runs correctly"
  edge_cases: []
  validation:
    - "Build, deploy, test on Raspberry Pi"

deliverable:
  format_requirements:
    - "Modify src/pi_netconfig/installer.py line 172"
    - "Modify src/pi_netconfig/main.py around line 287"
  files:
    - path: "src/pi_netconfig/installer.py"
      content: "Change service_controller to main"
    - path: "src/pi_netconfig/main.py"
      content: "Add component initialization before StateMonitor"

success_criteria:
  - "Installer generates correct module name"
  - "Main.py creates all components before StateMonitor"
  - "Service starts without errors on hardware"

notes: |
  Fix 1 - installer.py line 172:
  CURRENT:
  ExecStart={venv_python} -m pi_netconfig.service_controller
  
  FIXED:
  ExecStart={venv_python} -m pi_netconfig.main
  
  Fix 2 - main.py around line 287:
  CURRENT:
  state_monitor = StateMonitor()
  
  FIXED:
  connection_manager = ConnectionManager()
  ap_manager = APManager()
  web_server = WebServer(connection_manager)
  state_monitor = StateMonitor(connection_manager, ap_manager, web_server)

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-04 | Claude Desktop | Initial prompt from change-0020 |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
