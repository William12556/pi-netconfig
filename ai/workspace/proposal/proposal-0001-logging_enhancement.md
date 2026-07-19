# Proposal-0001: Logging Enhancement

**Date:** 2025-01-03  
**Status:** Draft for Review

---

## Problem Statement

Current logging implementation lacks:
1. Configurable log levels for service vs test execution
2. Log rotation policy (risk of disk exhaustion)
3. Structured error analysis workflow in test/debug cycles

---

## Proposed Solution

### Configuration

**Environment variable:** `PI_NETCONFIG_DEBUG`
- `true` or unset: Debug mode (logs INFO and ERROR) - DEFAULT
- `false`: Normal mode (logs INFO only)

**Implementation:** Single check in `configure_logging()`:
```python
debug_mode = os.environ.get('PI_NETCONFIG_DEBUG', 'true').lower() == 'true'
log_level = logging.INFO
# In normal mode, filter out ERROR level in handler
```

### Log Format

**Format string:**
```
%(asctime)s %(levelname)s %(name)s %(message)s
```

**Example output:**
```
2025-01-03 14:23:45 ERROR StateMonitor Failed to transition to CLIENT mode
2025-01-03 14:23:46 INFO ConnectionManager Network scan completed: 5 networks found
```

### Log Rotation

**Configuration:**
```python
handler = logging.handlers.RotatingFileHandler(
    '/var/log/pi-netconfig.log',
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=3
)
```

**Behavior:**
- Max file size: 10MB
- Keeps 3 backup files (pi-netconfig.log.1, .2, .3)
- Oldest backup deleted when limit reached

---

## Code Changes

### File: `src/pi_netconfig/main.py`

**Modify `configure_logging()` function:**

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
        
        logger.info(f"Logging configured: debug_mode={debug_mode}, level={logging.getLevelName(log_level)}")
        
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

**Add import:**
```python
import logging.handlers
```

---

## Test Execution

**Debug mode:**
```bash
PI_NETCONFIG_DEBUG=true pytest src/tests/
```

**Normal mode:**
```bash
PI_NETCONFIG_DEBUG=false pytest src/tests/
```

---

## Log Analysis Workflow

### During Development (Mac)

1. Run tests with debug mode enabled
2. Logs written to `/var/log/pi-netconfig.log` (mocked on Mac)
3. Review logs for errors after test failures
4. Create issue documents referencing specific log entries

### On Pi Hardware

1. Deploy to Pi
2. Production runs in normal mode (INFO only)
3. Debug mode enabled by default; disable with: `export PI_NETCONFIG_DEBUG=false`
4. Transfer logs to Mac: `scp pi:/var/log/pi-netconfig* workspace/logs/YYYY-MM-DD/`
5. Analyze logs, create issues as needed

---

## Governance Changes

### P00 Section 1.1.14 (new): Logging Standards

```markdown
#### 1.1.14 Logging Standards

- 1.1.14.1 Configuration
  - Generated applications implement environment-based log level control
  - Debug mode enables verbose logging for development and testing
  - Normal mode restricts logging to errors and critical events
  
- 1.1.14.2 Format
  - Flat file format recommended: timestamp level logger message
  - Centralized log location per application requirements
  - Log rotation policy prevents disk exhaustion
  
- 1.1.14.3 Test Execution
  - Test environments use debug mode for comprehensive logging
  - Production environments use normal mode for operational efficiency
  - Log artifacts preserved for failure analysis
```

### P01 Section 1.2.2 (.gitignore addition)

```
*.log
*.log.*
```

---

## Implementation

**Estimated effort:** 2 hours

**Steps:**
1. Modify `configure_logging()` in main.py
2. Update existing component loggers (no changes needed - use existing logger instances)
3. Add unit tests for log level configuration
4. Execute full test suite to verify behavior
5. Update governance.md

**Deliverables:**
- Change-NNNN: logging configuration enhancement
- Test results confirming log rotation and level switching

---

## Review Checklist

- [ ] Minimal changes to existing codebase
- [ ] Single environment variable control
- [ ] Flat file format maintained
- [ ] 10MB rotation implemented
- [ ] INFO/ERROR levels only
- [ ] Governance changes minimal

---

## Version History

| Version | Date       | Changes                    |
|---------|------------|----------------------------|
| 1.0     | 2025-01-03 | Minimal design proposal    |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
