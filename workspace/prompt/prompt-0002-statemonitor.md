Created: 2025 November 12

# T04 Prompt: StateMonitor Module

```yaml
prompt_info:
  id: "prompt-0002"
  task_type: "code_generation"
  source_ref: "design-0002-statemonitor"
  date: "2025-11-12"
  priority: "critical"

mcp_config:
  model: "claude-sonnet-4-20250514"
  temperature: 0.2
  max_tokens: 4096
  system_prompt: |
    Expert Python developer. Generate production-quality code following specifications.
    
    OUTPUT FORMAT REQUIREMENTS:
    - Return code only, no explanations or commentary
    - Include brief integration instructions after code
    - No markdown code blocks unless explicitly requested
    - No conversational text or preamble

context:
  purpose: "Main state machine managing service operational mode transitions between checking, client, and AP modes"
  integration: "Core orchestrator initialized by ServiceController, coordinates ConnectionManager, APManager, and WebServer"
  constraints:
    - "Single asyncio event loop"
    - "Non-blocking operations required"
    - "Must coordinate three independent modules"
    - "State persistence across monitoring cycles"

specification:
  description: "Implement state machine with three states (CHECKING, CLIENT, AP_MODE), 30-second monitoring loop, 3-failure threshold for mode transitions"
  requirements:
    functional:
      - "Implement SystemState enum with CHECKING, CLIENT, AP_MODE states"
      - "30-second connection monitoring loop"
      - "Track consecutive connection failures"
      - "Transition to AP_MODE after 3 consecutive failures"
      - "Coordinate component initialization and shutdown"
      - "Handle state transition failures with recovery"
      - "Respond to shutdown signals gracefully"
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Thread-safe if concurrent access"
        - "Comprehensive error handling"
        - "Debug logging with traceback"
        - "Professional docstrings (Google style)"
        - "Type hints"
  performance:
    - target: "State check interval 30 seconds"
      metric: "time"
    - target: "State transition under 2 seconds"
      metric: "time"
    - target: "Failure detection within 90 seconds (3 checks)"
      metric: "time"

design:
  architecture: "State machine pattern with asyncio coordination"
  components:
    - name: "SystemState"
      type: "enum"
      purpose: "Define system operational states"
      interface:
        inputs:
          - name: "N/A"
            type: "enum"
            description: "Enum values: CHECKING, CLIENT, AP_MODE"
        outputs:
          type: "SystemState"
          description: "State enumeration values"
        raises: []
      logic:
        - "CHECKING: Verifying connection status"
        - "CLIENT: Connected to router/AP"
        - "AP_MODE: Running as access point"
    
    - name: "StateMachine"
      type: "class"
      purpose: "Implement state transitions and mode coordination"
      interface:
        inputs:
          - name: "connection_manager"
            type: "ConnectionManager"
            description: "Connection testing module"
          - name: "ap_manager"
            type: "APManager"
            description: "Access point management module"
          - name: "web_server"
            type: "WebServer"
            description: "HTTP interface module"
        outputs:
          type: "None"
          description: "Runs until shutdown"
        raises:
          - "StateMonitorError - critical failures"
          - "StateTransitionError - transition failures"
          - "ComponentInitializationError - component init failures"
      logic:
        - "Initialize with CHECKING state"
        - "Create monitoring task"
        - "Loop: check connection every 30 seconds"
        - "CHECKING state: test connection, transition to CLIENT if connected, transition to AP_MODE if 3 failures"
        - "CLIENT state: test connection every 30 seconds, track failures, transition to AP_MODE if 3 consecutive failures"
        - "AP_MODE state: wait for configuration, test new connection, transition to CLIENT if successful"
        - "Handle asyncio.CancelledError for shutdown"
        - "Coordinate graceful component cleanup"
    
    - name: "run"
      type: "function"
      purpose: "Main entry point for state monitoring"
      interface:
        inputs:
          - name: "None"
            type: "N/A"
            description: "No parameters"
        outputs:
          type: "None"
          description: "Runs until shutdown"
        raises:
          - "StateMonitorError - on critical failures"
      logic:
        - "Initialize components"
        - "Start monitoring loop"
        - "Handle shutdown signal"
        - "Cleanup resources"
  
  dependencies:
    internal:
      - "ConnectionManager - for test_connection()"
      - "APManager - for activate_ap(), deactivate_ap()"
      - "WebServer - for start_server(), stop_server(), wait_for_configuration()"
    external:
      - "asyncio - for event loop and async operations"
      - "enum - for SystemState enumeration"

data_schema:
  entities:
    - name: "StateContext"
      attributes:
        - name: "current_state"
          type: "SystemState"
          constraints: "One of CHECKING, CLIENT, AP_MODE"
        - name: "failure_count"
          type: "int"
          constraints: "0 to 3, reset on successful connection"
        - name: "shutdown_event"
          type: "asyncio.Event"
          constraints: "Set when shutdown requested"
      validation:
        - "failure_count increments on each failed check"
        - "failure_count resets to 0 on successful connection"
        - "transition to AP_MODE when failure_count >= 3"

error_handling:
  strategy: "Log errors, attempt recovery to last known good state, enter degraded mode if recovery fails"
  exceptions:
    - exception: "StateMonitorError"
      condition: "Base exception for state monitor operations"
      handling: "Log with traceback, attempt recovery"
    - exception: "StateTransitionError"
      condition: "State transition failure"
      handling: "Log error, attempt recovery to previous state, enter degraded mode if recovery fails"
    - exception: "ComponentInitializationError"
      condition: "Component initialization failure"
      handling: "Log critical error, raise to ServiceController"
  logging:
    level: "DEBUG for transitions, INFO for state changes, WARNING for failures, ERROR for errors, CRITICAL for unrecoverable"
    format: "Use logging module with logger name 'StateMonitor'"

testing:
  unit_tests:
    - scenario: "Initial CHECKING state"
      expected: "current_state == SystemState.CHECKING"
    - scenario: "Connection successful from CHECKING"
      expected: "Transition to CLIENT state, failure_count = 0"
    - scenario: "Connection fails 3 times from CHECKING"
      expected: "Transition to AP_MODE state"
    - scenario: "Connection maintained in CLIENT"
      expected: "Remain in CLIENT, failure_count = 0"
    - scenario: "Connection lost 3 times in CLIENT"
      expected: "Transition to AP_MODE state"
    - scenario: "Configuration successful in AP_MODE"
      expected: "Transition to CLIENT state"
  edge_cases:
    - "Component method raises exception"
    - "Shutdown during state transition"
    - "Connection check timeout"
    - "Rapid state oscillation"
  validation:
    - "States transition according to state machine rules"
    - "failure_count increments correctly"
    - "Components activated/deactivated appropriately"
    - "Shutdown completes within 10 seconds"

output_format:
  structure: "code_only"
  integration_notes: "brief"
  constraints:
    - "No explanatory prose"
    - "No conversational preamble"
    - "Integration instructions: 2-3 lines maximum"

deliverable:
  format_requirements:
    - "Return raw Python code without markdown blocks"
    - "Add integration notes after code (max 3 lines)"
    - "No additional commentary or explanations"
  files:
    - path: "src/statemonitor.py"
      content: "Complete state monitor module implementation"
  documentation:
    - "Integration: Import run() from statemonitor. Pass ConnectionManager, APManager, WebServer instances. Call run() to start monitoring loop."

success_criteria:
  - "State machine transitions correctly between all states"
  - "30-second monitoring interval maintained"
  - "3-failure threshold triggers AP_MODE transition"
  - "Components coordinated correctly"
  - "Graceful shutdown on signal"
  - "Recovery from state transition failures"
  - "No unhandled exceptions in monitoring loop"

notes: "Core orchestrator - depends on ConnectionManager, APManager, WebServer interfaces. Reference System Flow Diagram (design-0007) for complete transition logic."

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

## Design Specification

### Module: StateMonitor

**Purpose:** Main state machine managing service operational mode transitions between checking, client, and AP modes.

**State Machine:**

```
CHECKING → (connected) → CLIENT
CHECKING → (3 failures) → AP_MODE

CLIENT → (connection maintained) → CLIENT
CLIENT → (3 failures) → AP_MODE

AP_MODE → (config success) → CLIENT
AP_MODE → (config failed) → AP_MODE
```

**Key Components:**

1. **SystemState Enum**
   - CHECKING: Verifying connection status
   - CLIENT: Connected to router/AP
   - AP_MODE: Running as access point

2. **StateMachine Class**
   - Attributes: `current_state`, `failure_count`, `shutdown_event`, component references
   - `initialize() -> None`: Creates component instances
   - `monitoring_loop() -> None`: 30-second check interval, infinite loop
   - `check_connection() -> bool`: Delegates to ConnectionManager
   - `transition_to_client() -> None`: Deactivates AP, stops web server
   - `transition_to_ap_mode() -> None`: Activates AP, starts web server
   - `handle_state_transition_failure(error) -> None`: Recovery logic
   - `shutdown() -> None`: Graceful component cleanup

3. **run() Function**
   - Main entry point
   - Coordinates initialization and monitoring

**State Transition Logic:**

- **CHECKING State:** Test connection, transition to CLIENT if connected, increment failure_count if not, transition to AP_MODE at 3 failures
- **CLIENT State:** Monitor every 30s, maintain failure_count, transition to AP_MODE at 3 failures, reset failure_count on success
- **AP_MODE State:** Web server active, wait for configuration, attempt connection with new credentials, transition to CLIENT if successful

**Exception Hierarchy:**
- StateMonitorError (base)
  - StateTransitionError
  - ComponentInitializationError

**Error Handling:**
- Connection check failure: Log warning, treat as connection failure, increment failure_count
- AP activation failure: Log error, retry after 60 seconds
- Web server failure: Log critical, enter degraded mode
- State transition failure: Log error with traceback, attempt recovery to last known state
- Shutdown failure: Best-effort, continue shutdown

**Logging Levels:**
- DEBUG: State transition initiation, connection checks, failure count, component calls
- INFO: Successful state transitions, connection status changes, monitoring loop start/stop
- WARNING: Connection check failures, retry attempts, degraded mode
- ERROR: State transition failures, component errors, recovery attempts
- CRITICAL: Unrecoverable state machine failure, component init failure, shutdown failures

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
