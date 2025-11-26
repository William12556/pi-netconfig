Created: 2025 November 26

# T04 Prompt: ServiceController Test Alignment

```yaml
prompt_info:
  id: "prompt-0013"
  task_type: "test_analysis_and_fix"
  source_ref: "change-0010-servicecontroller-test-alignment"
  date: "2025-11-26"
  priority: "high"

mcp_config:
  model: "claude-sonnet-4-20250514"
  temperature: 0.2
  max_tokens: 8192
  system_prompt: "Expert Python developer. First analyze main.py, then output corrected tests."

context:
  purpose: "Align tests with actual main.py implementation"
  integration: "Replace 8 test methods in src/tests/servicecontroller/test_servicecontroller.py"
  prerequisite: "Analyze src/main.py to determine actual implementation"

tasks:
  step_1:
    action: "Analyze main.py"
    outputs:
      - "Document actual constant names (e.g., LOG_FILE_PATH equivalent)"
      - "Document actual function signatures"
      - "Document actual import names (StateMonitor vs StateMachine)"
      - "Identify any other test mismatches"
  
  step_2:
    action: "Generate corrected tests"
    targets:
      - "test_configure_logging_creates_file_handler"
      - "test_configure_logging_adds_console_handler_in_manual_mode"
      - "test_signal_handler_sets_shutdown_event"
      - "test_register_signal_handlers_registers_sigterm_and_sigint"
      - "test_graceful_shutdown_calls_state_monitor_shutdown"
      - "test_graceful_shutdown_handles_timeout_gracefully"
      - "test_run_service_creates_state_monitor_and_waits_for_shutdown"
      - "test_main_runs_service_in_service_mode"

specification:
  analysis_focus:
    - "Logging configuration constants and implementation"
    - "Signal handling function signatures"
    - "State monitor class name and instantiation"
    - "Async function signatures"
    - "Event loop management"

  known_issues:
    - issue: "LOG_FILE_PATH not found"
      investigation: "Find actual log path constant or hardcoded value"
    - issue: "StateMachine vs StateMonitor"
      investigation: "Verify class name in main.py imports"
    - issue: "signal_handler(signum, frame, shutdown_event)"
      investigation: "Verify actual signature"
    - issue: "register_signal_handlers(shutdown_event)"
      investigation: "Verify actual signature"
    - issue: "graceful_shutdown(state_monitor)"
      investigation: "Verify actual signature"

output_format:
  part_1: "Analysis Report"
  structure: |
    ## main.py Analysis
    
    ### Constants
    - Log file path: [actual constant or value]
    
    ### Function Signatures
    - signal_handler: [actual signature]
    - register_signal_handlers: [actual signature]
    - graceful_shutdown: [actual signature]
    - run_service: [actual signature]
    
    ### Imports
    - State monitor class: [actual name]
    
    ### Discrepancies
    - [List any design vs implementation differences]
  
  part_2: "Corrected Test Methods"
  format: "Python code only"

deliverable:
  outputs:
    - "Analysis report documenting actual implementation"
    - "8 corrected test methods"
  integration: "Replace methods in test_servicecontroller.py"
  documentation: "Document any design compliance issues discovered"

success_criteria:
  - "All 17 ServiceController tests pass"
  - "Tests verify actual implementation behavior"
  - "Design discrepancies documented for future review"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
