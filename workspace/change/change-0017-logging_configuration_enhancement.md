# Change-0012: Logging Configuration Enhancement

Created: 2025-12-03

---

## Table of Contents

- [Change Information](<#change information>)
- [Source](<#source>)
- [Scope](<#scope>)
- [Rationale](<#rationale>)
- [Technical Details](<#technical details>)
- [Dependencies](<#dependencies>)
- [Testing Requirements](<#testing requirements>)
- [Implementation](<#implementation>)
- [Verification](<#verification>)
- [Traceability](<#traceability>)
- [Version History](<#version history>)

---

## Change Information

```yaml
change_info:
  id: "change-0012"
  title: "Logging Configuration Enhancement"
  date: "2025-12-03"
  author: "Claude"
  status: "proposed"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0012"
    issue_iteration: 1
```

[Return to Table of Contents](<#table of contents>)

---

## Source

```yaml
source:
  type: "issue"
  reference: "issue-0012"
  description: "Add environment-based logging control with rotation"
```

[Return to Table of Contents](<#table of contents>)

---

## Scope

```yaml
scope:
  summary: "Modify configure_logging() to support debug/normal modes and log rotation"
  affected_components:
    - name: "ServiceController"
      file_path: "src/pi_netconfig/main.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-0000-master_pi-netconfig"
      sections:
        - "error_handling.logging"
  out_of_scope:
    - "Structured logging (JSON format)"
    - "Log aggregation workflows"
    - "Automated log analysis tools"
```

[Return to Table of Contents](<#table of contents>)

---

## Rationale

```yaml
rational:
  problem_statement: "Current logging lacks runtime configurability and rotation policy, risking disk exhaustion and limiting debug capabilities"
  proposed_solution: "Implement environment variable control with RotatingFileHandler"
  alternatives_considered:
    - option: "Configuration file-based logging"
      reason_rejected: "Adds complexity, environment variable is simpler"
    - option: "Structured JSON logging"
      reason_rejected: "Conflicts with minimalist design philosophy"
  benefits:
    - "Runtime log level toggle via systemd Environment directive"
    - "Automatic log rotation prevents disk exhaustion"
    - "Default debug mode aids development and testing"
    - "Normal mode suitable for production deployment"
  risks:
    - risk: "Log rotation may truncate active investigation data"
      mitigation: "10MB threshold provides ample history, 3 backups retain 30MB total"
```

[Return to Table of Contents](<#table of contents>)

---

## Technical Details

```yaml
technical_details:
  current_behavior: "Fixed log level, basic FileHandler, no rotation, manual mode logs to console and file"
  proposed_behavior: "Environment-controlled log level, RotatingFileHandler with 10MB/3 backup policy, filtered ERROR in normal mode"
  implementation_approach: "Modify configure_logging() to check PI_NETCONFIG_DEBUG environment variable, replace FileHandler with RotatingFileHandler, add filter for normal mode"
  code_changes:
    - component: "ServiceController"
      file: "src/pi_netconfig/main.py"
      change_summary: "Update configure_logging() function"
      functions_affected:
        - "configure_logging"
      classes_affected: []
  data_changes: []
  interface_changes:
    - interface: "configure_logging(mode: str)"
      change_type: "behavior"
      details: "Function signature unchanged, internal behavior modified to read environment variable and configure rotation"
      backward_compatible: "yes"
```

**Code Changes:**

File: `src/pi_netconfig/main.py`

Add import:
```python
import logging.handlers
```

Modify `configure_logging()`:
```python
def configure_logging(mode: str) -> None:
    """
    Configure logging infrastructure.
    
    Args:
        mode: Execution mode ('bootstrap', 'service', 'manual')
    
    Configuration:
        - Debug mode (PI_NETCONFIG_DEBUG=true): INFO and ERROR
        - Normal mode (default): INFO only
        - File: /var/log/pi-netconfig.log (10MB, 3 backups)
        - Console: Manual mode only, same level as file
        - Format: timestamp level logger message
    """
    try:
        # Determine log filtering from environment
        debug_mode = os.environ.get('PI_NETCONFIG_DEBUG', 'true').lower() == 'true'
        
        # Create log directory
        log_path = Path('/var/log/pi-netconfig.log')
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # File handler with rotation and filtering
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=3
        )
        
        # Normal mode: INFO only; Debug mode: INFO and ERROR
        if debug_mode:
            file_handler.setLevel(logging.INFO)
        else:
            file_handler.addFilter(lambda record: record.levelno == logging.INFO)
        
        file_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        logger.info(f"Logging configured: debug_mode={debug_mode}, level={logging.getLevelName(logging.INFO)}")
        
        # Console handler (manual mode only)
        if mode == 'manual':
            console_handler = logging.StreamHandler(sys.stdout)
            if debug_mode:
                console_handler.setLevel(logging.INFO)
            else:
                console_handler.addFilter(lambda record: record.levelno == logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s %(levelname)s %(name)s %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
            logger.debug("Console logging configured for manual mode")
        
        logger.info("Logging configuration complete")
    
    except Exception as e:
        print(f"ERROR: Cannot configure logging: {e}", file=sys.stderr)
        raise LoggingConfigurationError(f"Cannot configure logging: {e}")
```

[Return to Table of Contents](<#table of contents>)

---

## Dependencies

```yaml
dependencies:
  internal: []
  external:
    - library: "logging.handlers"
      version_change: "stdlib (new import)"
      impact: "None - standard library"
  required_changes: []
```

[Return to Table of Contents](<#table of contents>)

---

## Testing Requirements

```yaml
testing_requirements:
  test_approach: "Unit tests for log level configuration and rotation behavior"
  test_cases:
    - scenario: "Debug mode enabled (PI_NETCONFIG_DEBUG=true)"
      expected_result: "INFO and ERROR messages logged"
    - scenario: "Normal mode (PI_NETCONFIG_DEBUG=false)"
      expected_result: "INFO messages logged, ERROR filtered"
    - scenario: "Log rotation at 10MB threshold"
      expected_result: "New log file created, backup files (.1, .2, .3) present"
    - scenario: "Manual mode with debug"
      expected_result: "Console and file both receive INFO and ERROR"
    - scenario: "Manual mode normal"
      expected_result: "Console and file both receive INFO only"
  regression_scope:
    - "All existing ServiceController unit tests"
    - "Full application startup in service mode"
  validation_criteria:
    - "Environment variable correctly controls log filtering"
    - "Log rotation occurs at 10MB boundary"
    - "Backup files maintain proper naming (.1, .2, .3)"
    - "Log format matches specification"
```

[Return to Table of Contents](<#table of contents>)

---

## Implementation

```yaml
implementation:
  effort_estimate: "2 hours"
  implementation_steps:
    - step: "Add logging.handlers import to main.py"
      owner: "Claude Code"
    - step: "Modify configure_logging() function per specification"
      owner: "Claude Code"
    - step: "Create unit tests for log configuration"
      owner: "Claude Desktop"
    - step: "Execute tests and verify behavior"
      owner: "Claude Desktop"
  rollback_procedure: "Revert main.py to previous commit"
  deployment_notes: "Set PI_NETCONFIG_DEBUG=false in systemd service for production"
```

[Return to Table of Contents](<#table of contents>)

---

## Verification

```yaml
verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []
```

[Return to Table of Contents](<#table of contents>)

---

## Traceability

```yaml
traceability:
  design_updates:
    - design_ref: "design-0000-master_pi-netconfig"
      sections_updated:
        - "error_handling.logging"
      update_date: ""
  related_changes: []
  related_issues:
    - issue_ref: "issue-0012"
      relationship: "resolves"
```

[Return to Table of Contents](<#table of contents>)

---

## Notes

Implements minimal logging enhancement per proposal-0001-logging_enhancement.md. Debug mode defaults to true for development convenience.

---

## Version History

| Version | Date       | Author | Changes                  |
|---------|------------|--------|--------------------------|
| 1.0     | 2025-12-03 | Claude | Initial change proposal  |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
