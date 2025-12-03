# Prompt-0012: Logging Configuration Enhancement

---

```yaml
prompt_info:
  id: "prompt-0012"
  task_type: "code_generation"
  source_ref: "change-0012"
  date: "2025-12-03"
  priority: "medium"
  iteration: 1
  coupled_docs:
    change_ref: "change-0012"
    change_iteration: 1

context:
  purpose: "Add environment-based logging control with rotation to ServiceController"
  integration: "Modifies existing configure_logging() in main.py"
  constraints:
    - "Maintain backward compatibility"
    - "Preserve all existing functionality"
    - "Use standard library only"

specification:
  description: "Implement configurable logging with debug/normal modes and rotation policy"
  requirements:
    functional:
      - "Environment variable PI_NETCONFIG_DEBUG controls log level (default: true)"
      - "Debug mode: logs INFO and ERROR levels"
      - "Normal mode: logs INFO only, filters ERROR"
      - "RotatingFileHandler: 10MB max size, 3 backup files"
      - "Flat log format: timestamp level logger message"
    technical:
      language: "Python"
      version: "3.9+"
      standards:
        - "Thread-safe logging configuration"
        - "Comprehensive error handling"
        - "Professional docstrings"
  performance: []

design:
  architecture: "Modify single function in existing module"
  components:
    - name: "configure_logging"
      type: "function"
      purpose: "Configure logging with environment-based control and rotation"
      interface:
        inputs:
          - name: "mode"
            type: "str"
            description: "Execution mode: bootstrap, service, or manual"
        outputs:
          type: "None"
          description: "Configures root logger as side effect"
        raises:
          - "LoggingConfigurationError"
      logic:
        - "Read PI_NETCONFIG_DEBUG environment variable (default true)"
        - "Create log directory if needed"
        - "Configure root logger at INFO level"
        - "Remove existing handlers"
        - "Create RotatingFileHandler (10MB, 3 backups)"
        - "If debug mode: set handler to INFO level"
        - "If normal mode: add filter for INFO only (exclude ERROR)"
        - "Format: %(asctime)s %(levelname)s %(name)s %(message)s"
        - "If manual mode: add console handler with same filtering"
  dependencies:
    internal: []
    external:
      - "logging.handlers (RotatingFileHandler)"

error_handling:
  strategy: "Catch exceptions during configuration, print to stderr, raise LoggingConfigurationError"
  exceptions:
    - exception: "LoggingConfigurationError"
      condition: "Configuration fails"
      handling: "Print error, raise exception"
  logging:
    level: "INFO"
    format: "%(asctime)s %(levelname)s %(name)s %(message)s"

deliverable:
  format_requirements:
    - "Modify src/pi_netconfig/main.py only"
    - "Add import: logging.handlers"
    - "Replace configure_logging() function"
    - "Create completion document"
  files:
    - path: "src/pi_netconfig/main.py"
      content: "Modified configure_logging() function with new imports"
  completion_document:
    path: "workspace/prompt/prompt-0012-completion.md"
    required_fields:
      - "timestamp"
      - "files_modified: [src/pi_netconfig/main.py]"
      - "status: SUCCESS or FAILURE"
      - "notes: [any warnings]"

success_criteria:
  - "Import logging.handlers added"
  - "configure_logging() implements environment variable check"
  - "RotatingFileHandler configured with 10MB/3 backup policy"
  - "Debug mode allows INFO and ERROR"
  - "Normal mode filters ERROR, allows INFO only"
  - "Log format matches specification"
  - "Manual mode console handler mirrors file handler behavior"

notes: "Default debug mode (true) aids development. Production should set PI_NETCONFIG_DEBUG=false in systemd Environment directive."

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

## Code Specification

### Required Import
```python
import logging.handlers
```

### Modified Function
Replace existing `configure_logging()` with:

```python
def configure_logging(mode: str) -> None:
    """
    Configure logging infrastructure.
    
    Args:
        mode: Execution mode ('bootstrap', 'service', 'manual')
    
    Configuration:
        - Debug mode (PI_NETCONFIG_DEBUG=true): INFO and ERROR
        - Normal mode (PI_NETCONFIG_DEBUG=false): INFO only
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

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
