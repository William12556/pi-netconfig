Created: 2025 December 05

```yaml
prompt_info:
  id: "prompt-0023"
  task_type: "debug"
  source_ref: "change-0023-logging-configuration-fix.md"
  date: "2025-12-05"
  priority: "high"
  iteration: 1
  coupled_docs:
    change_ref: "change-0023"
    change_iteration: 1

context:
  purpose: "Fix logging configuration bugs preventing debug output"
  integration: "ServiceController logging infrastructure used by all components"
  knowledge_references: []
  constraints:
    - "Minimal changes - only fix identified bugs"
    - "No functional changes beyond logging"
    - "Maintain log rotation and file handling"

specification:
  description: |
    Fix two bugs in main.py configure_logging():
    1. Environment variable mismatch (PI_NETCONFIG_DEBUG vs DEBUG_MODE)
    2. Inverted debug mode logic (both branches set INFO level)
  requirements:
    functional:
      - "Check DEBUG_MODE environment variable (not PI_NETCONFIG_DEBUG)"
      - "Set root logger to DEBUG when DEBUG_MODE=true"
      - "Set root logger to INFO when DEBUG_MODE=false"
      - "Remove unnecessary filter logic"
    technical:
      language: "Python"
      version: "3.9+"
      standards:
        - "Maintain existing error handling"
        - "Preserve log rotation configuration"
        - "Keep log format unchanged"
  performance: []

design:
  architecture: "Direct fix to configure_logging() function"
  components:
    - name: "configure_logging"
      type: "function"
      purpose: "Configure logging with correct debug mode support"
      interface:
        inputs:
          - name: "mode"
            type: "str"
            description: "Execution mode (bootstrap/service/manual)"
        outputs:
          type: "None"
          description: "Configures global logging infrastructure"
        raises:
          - "LoggingConfigurationError"
      logic:
        - "Line 148: Change to os.environ.get('DEBUG_MODE', 'false')"
        - "Line 156: Set root_logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)"
        - "Line 165: Set file_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)"
        - "Line 166-167: Remove filter logic (unnecessary)"
        - "Line 174: Update log message to show actual level name"
  dependencies:
    internal: []
    external:
      - "logging module"

data_schema:
  entities: []

error_handling:
  strategy: "Maintain existing exception handling unchanged"
  exceptions: []
  logging:
    level: "INFO"
    format: "Unchanged"

testing:
  unit_tests:
    - scenario: "Debug mode enabled"
      expected: "Root logger DEBUG, debug messages visible"
    - scenario: "Debug mode disabled"  
      expected: "Root logger INFO, no debug messages"
  edge_cases:
    - "DEBUG_MODE not set (defaults to false)"
    - "DEBUG_MODE case variations (TRUE, True, true)"
  validation:
    - "Service starts without errors"
    - "Log level matches debug_mode setting"
    - "StateMonitor debug output appears when enabled"

deliverable:
  format_requirements:
    - "Modify src/pi_netconfig/main.py only"
    - "Preserve all other functionality"
  files:
    - path: "src/pi_netconfig/main.py"
      content: |
        Modify configure_logging() function:
        
        Line 148 (current):
        debug_mode = os.environ.get('PI_NETCONFIG_DEBUG', 'true').lower() == 'true'
        
        Line 148 (fixed):
        debug_mode = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
        
        
        Line 156 (current):
        root_logger.setLevel(logging.INFO)
        
        Line 156 (fixed):
        root_logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        
        
        Lines 165-167 (current):
        if debug_mode:
            file_handler.setLevel(logging.INFO)
        else:
            file_handler.addFilter(lambda record: record.levelno == logging.INFO)
        
        Lines 165-166 (fixed):
        file_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        
        
        Line 174 (current):
        logger.info(f"Logging configured: debug_mode={debug_mode}, level={logging.getLevelName(logging.INFO)}")
        
        Line 174 (fixed):
        logger.info(f"Logging configured: debug_mode={debug_mode}, level={logging.getLevelName(root_logger.level)}")

success_criteria:
  - "configure_logging() uses DEBUG_MODE environment variable"
  - "Root logger level set correctly for both debug modes"
  - "File handler inherits correct level"
  - "No filter logic on file handler"
  - "Log message shows actual configured level"

notes: |
  Critical fix for hardware validation. Without debug output, StateMonitor
  monitoring activity invisible, blocking CLIENT mode verification.
  
  Changes isolated to configure_logging() function only. No impact on
  other service functionality.

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
