Created: 2025 November 12

# T04 Prompt: ServiceController Module

```yaml
prompt_info:
  id: "prompt-0006"
  task_type: "code_generation"
  source_ref: "design-0006-servicecontroller"
  date: "2025-11-12"
  priority: "critical"

mcp_config:
  model: "claude-sonnet-4-20250514"
  temperature: 0.2
  max_tokens: 4096
  system_prompt: |
    Expert Python developer. Generate production-quality code following specifications.
    OUTPUT FORMAT: Code only with brief integration notes. No explanations.

context:
  purpose: "Application entry point managing execution mode detection, installer invocation, logging configuration, and systemd service lifecycle"
  integration: "Main entry point invoked by Python interpreter or systemd service manager"
  constraints:
    - "Must work as both standalone script and systemd service"
    - "Requires root privileges for service mode"
    - "Single asyncio event loop for entire application"
    - "Must handle signals gracefully"

specification:
  description: "Implement application main entry point with mode detection, logging configuration, signal handling, StateMonitor lifecycle management, and graceful shutdown"
  requirements:
    functional:
      - "Detect execution mode: bootstrap (no service file), service (systemd), or manual"
      - "Bootstrap mode: verify root, call Installer.install(), exit with installer result"
      - "Service mode: configure logging, verify root, register signal handlers, initialize StateMonitor, run event loop"
      - "Register SIGTERM (systemd stop) and SIGINT (Ctrl+C) handlers"
      - "Coordinate graceful shutdown with 10-second timeout"
      - "Configure logging to /var/log/pi-netconfig.log with INFO level"
      - "Add console handler for DEBUG when not running under systemd"
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Thread-safe, comprehensive error handling, debug logging, docstrings, type hints"
  performance:
    - target: "Startup under 5 seconds (excluding installation)"
      metric: "time"
    - target: "Shutdown under 3 seconds (graceful cleanup)"
      metric: "time"

design:
  architecture: "Functional entry point with asyncio event loop coordination"
  components:
    - name: "main"
      type: "function"
      purpose: "Main entry point"
      interface:
        inputs: []
        outputs:
          type: "int"
          description: "Exit code 0 or 1"
        raises:
          - "None (catches all exceptions)"
      logic:
        - "Detect execution mode"
        - "Bootstrap mode: verify root, call installer, exit with result"
        - "Service mode: configure logging, verify root, register signals, run service"
        - "Return exit code"
    
    - name: "detect_execution_mode"
      type: "function"
      purpose: "Determine bootstrap, service, or manual mode"
      interface:
        inputs: []
        outputs:
          type: "str"
          description: "bootstrap, service, or manual"
      logic:
        - "Check service file existence via Installer.is_service_installed()"
        - "Check INVOCATION_ID environment variable (systemd indicator)"
        - "Return appropriate mode"
    
    - name: "verify_root_privileges"
      type: "function"
      purpose: "Check if running as root"
      interface:
        inputs: []
        outputs:
          type: "bool"
          description: "True if UID 0"
      logic:
        - "Check os.geteuid() == 0"
    
    - name: "configure_logging"
      type: "function"
      purpose: "Set up logging infrastructure"
      interface:
        inputs: []
        outputs:
          type: "None"
        raises:
          - "ServiceControllerError"
      logic:
        - "Configure FileHandler to /var/log/pi-netconfig.log, format with timestamp/name/level/message"
        - "Set root logger to INFO"
        - "Add console StreamHandler for DEBUG if terminal detected"
        - "Create log file if doesn't exist"
    
    - name: "register_signal_handlers"
      type: "function"
      purpose: "Register SIGTERM and SIGINT handlers"
      interface:
        inputs: []
        outputs:
          type: "None"
      logic:
        - "Register signal.SIGTERM handler"
        - "Register signal.SIGINT handler"
        - "Both call signal_handler()"
    
    - name: "signal_handler"
      type: "function"
      purpose: "Handle shutdown signals"
      interface:
        inputs:
          - name: "signum"
            type: "int"
            description: "Signal number"
          - name: "frame"
            type: "FrameType"
            description: "Stack frame"
        outputs:
          type: "None"
      logic:
        - "Log signal receipt"
        - "Set shutdown_event"
    
    - name: "run_service"
      type: "function (async)"
      purpose: "Run main service loop"
      interface:
        inputs: []
        outputs:
          type: "None"
        raises:
          - "ServiceControllerError"
      logic:
        - "Create shutdown_event (asyncio.Event)"
        - "Initialize StateMonitor"
        - "Start StateMonitor.run()"
        - "Wait for shutdown_event"
        - "Call StateMonitor.shutdown()"
    
    - name: "graceful_shutdown"
      type: "function (async)"
      purpose: "Coordinate component cleanup"
      interface:
        inputs: []
        outputs:
          type: "None"
      logic:
        - "Log shutdown initiation"
        - "Call StateMonitor.shutdown()"
        - "Wait up to 10 seconds for cleanup"
        - "Log completion or timeout"
        - "Best-effort, no exceptions raised"
  
  dependencies:
    internal:
      - "Installer - for installation check and invocation"
      - "StateMonitor - primary component managed"
    external:
      - "logging - logging infrastructure"
      - "signal - signal handling"
      - "asyncio - event loop"
      - "os - privilege checking"
      - "sys - exit codes"

data_schema:
  entities:
    - name: "LogConfiguration"
      attributes:
        - name: "file_path"
          type: "str"
          constraints: "/var/log/pi-netconfig.log"
        - name: "format"
          type: "str"
          constraints: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        - name: "level"
          type: "int"
          constraints: "INFO"
      validation:
        - "Log file writable"
        - "Format includes all required fields"

error_handling:
  strategy: "Catch all exceptions at main(), log critical errors, return appropriate exit codes"
  exceptions:
    - exception: "ServiceControllerError"
      condition: "Base exception"
      handling: "Log critical, exit code 1"
    - exception: "LoggingConfigurationError"
      condition: "Cannot write to log file"
      handling: "Print to stderr, exit code 1"
    - exception: "PrivilegeError"
      condition: "Not running as root in service mode"
      handling: "Print error message, exit code 1"
  logging:
    level: "DEBUG for initialization, INFO for service events, WARNING for manual mode, ERROR for failures, CRITICAL for unrecoverable"
    format: "Logger name 'ServiceController'"

testing:
  unit_tests:
    - scenario: "Bootstrap mode detection"
      expected: "Returns 'bootstrap' when service file not exists"
    - scenario: "Service mode detection"
      expected: "Returns 'service' when service file exists and INVOCATION_ID set"
    - scenario: "Root privilege check"
      expected: "Returns True if UID 0"
    - scenario: "Signal handler registration"
      expected: "SIGTERM and SIGINT handlers registered"
    - scenario: "Graceful shutdown"
      expected: "Components cleaned up within 10 seconds"
  edge_cases:
    - "Log file permissions denied"
    - "StateMonitor initialization failure"
    - "Shutdown timeout"
    - "Signal during initialization"
  validation:
    - "Correct exit codes (0 for success, 1 for error)"
    - "Logging configured before any logging calls"
    - "Signal handlers prevent abrupt termination"
    - "Shutdown completes within timeout"

output_format:
  structure: "code_only"
  integration_notes: "brief"

deliverable:
  files:
    - path: "src/main.py"
      content: "Complete service controller implementation with __main__ entry point"
  documentation:
    - "Integration: Execute as main.py. Systemd ExecStart=/usr/bin/python3 /usr/local/bin/pi-netconfig/main.py. Handles bootstrap and service modes automatically."

success_criteria:
  - "Mode detection accurate for all scenarios"
  - "Bootstrap mode installs service correctly"
  - "Service mode starts StateMonitor successfully"
  - "Logging configured properly"
  - "Signal handlers respond to SIGTERM and SIGINT"
  - "Graceful shutdown completes within timeout"
  - "Appropriate exit codes returned"

notes: "Application entry point - coordinates all modules. Reference Systemd Service Diagram (design-0008) for complete lifecycle. Must handle both bootstrap and service execution contexts."

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

## Design Specification

**Purpose:** Application entry point managing execution modes and service lifecycle.

**Execution Modes:**

1. **Bootstrap**: Service file not exists → verify root → install → exit
2. **Service**: Service file exists, running under systemd → configure logging → verify root → register signals → run StateMonitor
3. **Manual**: Service exists, not under systemd → same as Service + console logging

**Key Functions:**

- `main() -> int`: Entry point, returns exit code
- `detect_execution_mode() -> str`: Check service file and INVOCATION_ID
- `configure_logging() -> None`: FileHandler to /var/log/pi-netconfig.log
- `register_signal_handlers() -> None`: SIGTERM and SIGINT
- `signal_handler(signum, frame) -> None`: Set shutdown_event
- `run_service() -> None`: Initialize StateMonitor, run loop, handle shutdown
- `graceful_shutdown() -> None`: Cleanup with 10s timeout

**Signal Handling:**
- SIGTERM (15): systemctl stop → graceful shutdown
- SIGINT (2): Ctrl+C → graceful shutdown

**Logging:**
- File: /var/log/pi-netconfig.log
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Level: INFO (file), DEBUG (console if manual mode)

**Exit Codes:**
- 0: Success
- 1: Error or insufficient privileges

**Exception Hierarchy:** ServiceControllerError → LoggingConfigurationError, PrivilegeError

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
