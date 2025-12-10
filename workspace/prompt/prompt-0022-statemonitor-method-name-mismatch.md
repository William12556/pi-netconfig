Created: 2025 December 05

# prompt-0022-statemonitor-method-name-mismatch.md

```yaml
prompt_info:
  id: "prompt-0022"
  task_type: "code_generation"
  source_ref: "change-0022-statemonitor-method-name-mismatch.md"
  date: "2025-12-05"
  priority: "critical"
  iteration: 1
  coupled_docs:
    change_ref: "change-0022"
    change_iteration: 1

context:
  purpose: "Fix method call to match actual StateMonitor method name"
  integration: "Main.py starts StateMonitor monitoring loop"
  knowledge_references: []
  constraints:
    - "Single line change only"

specification:
  description: "Change run() to monitoring_loop() in main.py line 300"
  requirements:
    functional:
      - "Call correct StateMonitor method"
    technical:
      language: "Python"
      version: "3.9+"
      standards: []
  performance: []

design:
  architecture: "Single method call correction"
  components:
    - name: "Method call fix"
      type: "function call"
      purpose: "Invoke StateMonitor monitoring loop"
      interface:
        inputs: []
        outputs: []
        raises: []
      logic:
        - "Line 300: Change state_monitor.run() to state_monitor.monitoring_loop()"
  dependencies:
    internal:
      - "StateMonitor.monitoring_loop()"
    external: []

data_schema:
  entities: []

error_handling:
  strategy: "No changes"
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
    - "Deploy and verify startup"

deliverable:
  format_requirements:
    - "Modify src/pi_netconfig/main.py line 300"
  files:
    - path: "src/pi_netconfig/main.py"
      content: "Line 300 only"

success_criteria:
  - "No AttributeError"
  - "Service runs"

notes: |
  Line 300 change:
  
  CURRENT:
  monitor_task = asyncio.create_task(state_monitor.run())
  
  FIXED:
  monitor_task = asyncio.create_task(state_monitor.monitoring_loop())

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-05 | Claude Desktop | Initial prompt from change-0022 |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
