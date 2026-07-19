Created: 2025 December 23

```yaml
prompt_info:
  id: "prompt-0025"
  task_type: "debug"
  source_ref: "change-0025-statemonitor-initialization.md"
  date: "2025-12-23"
  priority: "critical"
  iteration: 1
  coupled_docs:
    change_ref: "change-0025"
    change_iteration: 1

context:
  purpose: "Fix StateMonitor initialization to enable monitoring functionality"
  integration: "Main service loop initializes StateMonitor before starting monitoring"
  knowledge_references: []
  constraints:
    - "Minimal change - only fix initialization sequence"
    - "Maintain async/await pattern"
    - "Preserve error handling"

specification:
  description: "Add StateMonitor.initialize() call in main.py run_service() function"
  requirements:
    functional:
      - "Call state_monitor.initialize() after construction"
      - "Remove explicit monitoring_loop() call (initialize handles it)"
      - "Update log messages for clarity"
    technical:
      language: "Python"
      version: "3.9+"
      standards:
        - "Async/await pattern"
        - "Proper error handling"
        - "Clear debug logging"
  performance: []

design:
  architecture: "Fix initialization sequence in run_service()"
  components:
    - name: "run_service"
      type: "function"
      purpose: "Main service loop with correct StateMonitor initialization"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Runs until shutdown"
        raises:
          - "ServiceControllerError"
      logic:
        - "Create StateMonitor instance"
        - "Call await state_monitor.initialize()"
        - "Remove explicit monitoring_loop() call"
        - "Wait for shutdown signal"
        - "Graceful shutdown using state_monitor.monitoring_task"
  dependencies:
    internal:
      - "StateMonitor.initialize()"
      - "StateMonitor.shutdown()"
    external: []

data_schema:
  entities: []

error_handling:
  strategy: "Maintain existing exception handling"
  exceptions: []
  logging:
    level: "DEBUG"
    format: "Existing format"

testing:
  unit_tests: []
  edge_cases:
    - "Service startup"
    - "Graceful shutdown"
  validation:
    - "Connection checks logged every 30 seconds"
    - "No AttributeError"
    - "Monitoring loop runs continuously"

deliverable:
  format_requirements:
    - "Modify src/pi_netconfig/main.py only"
    - "Preserve all other functionality"
  files:
    - path: "src/pi_netconfig/main.py"
      content: |
        Modify run_service() function around lines 288-308:
        
        CURRENT CODE (lines 288-308):
        ```python
        # Initialize components
        logger.debug("Initializing components")
        config_manager = ConfigManager()
        access_point = AccessPoint()
        web_server_manager = WebServerManager(config_manager)
        
        # Initialize StateMonitor
        logger.debug("Initializing StateMonitor")
        state_monitor = StateMonitor(config_manager, access_point, web_server_manager)
        
        # Start StateMonitor
        logger.debug("Starting StateMonitor")
        monitor_task = asyncio.create_task(state_monitor.monitoring_loop())
        
        # Wait for shutdown signal
        logger.info("Service running, waiting for shutdown signal")
        await shutdown_event.wait()
        
        # Graceful shutdown
        logger.info("Shutdown signal received")
        await graceful_shutdown()
        
        # Wait for monitor task to complete
        try:
            await asyncio.wait_for(monitor_task, timeout=2.0)
        except asyncio.TimeoutError:
            logger.warning("StateMonitor task did not complete within timeout")
        ```
        
        FIXED CODE (lines 288-305):
        ```python
        # Initialize components
        logger.debug("Initializing components")
        config_manager = ConfigManager()
        access_point = AccessPoint()
        web_server_manager = WebServerManager(config_manager)
        
        # Initialize StateMonitor
        logger.debug("Initializing StateMonitor")
        state_monitor = StateMonitor(config_manager, access_point, web_server_manager)
        await state_monitor.initialize()
        
        logger.debug("StateMonitor initialized and monitoring started")
        
        # Wait for shutdown signal
        logger.info("Service running, waiting for shutdown signal")
        await shutdown_event.wait()
        
        # Graceful shutdown
        logger.info("Shutdown signal received")
        await graceful_shutdown()
        
        # Wait for monitor task to complete
        if state_monitor.monitoring_task:
            try:
                await asyncio.wait_for(state_monitor.monitoring_task, timeout=2.0)
            except asyncio.TimeoutError:
                logger.warning("StateMonitor task did not complete within timeout")
        ```
        
        KEY CHANGES:
        1. Line 291: Add "await state_monitor.initialize()"
        2. Line 293: New log message confirming initialization
        3. Remove line 294: "monitor_task = asyncio.create_task(state_monitor.monitoring_loop())"
        4. Line 304: Change "monitor_task" to "state_monitor.monitoring_task"
        5. Line 303: Add null check "if state_monitor.monitoring_task:"

success_criteria:
  - "initialize() called before monitoring starts"
  - "No explicit monitoring_loop() call"
  - "Service starts without errors"
  - "Connection checks appear in logs"

notes: |
  Critical fix - StateMonitor.initialize() creates shutdown_event and
  starts monitoring_task internally. Explicit monitoring_loop() call
  was incorrect and redundant.
  
  After fix, monitoring loop will execute continuously and log connection
  checks every 30 seconds.

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
