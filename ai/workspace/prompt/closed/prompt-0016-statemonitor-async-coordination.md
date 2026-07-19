# prompt-0016-statemonitor-async-coordination.md

```yaml
prompt_info:
  id: "prompt-0016"
  task_type: "debug"
  source_ref: "change-0011-statemonitor-async-coordination"
  date: "2025-11-28"
  priority: "high"
  iteration: 1
  coupled_docs:
    change_ref: "change-0011"
    change_iteration: 1

context:
  purpose: "Add async lock coordination to StateMonitor for atomic state transitions"
  integration: "Modifies StateMonitor class to prevent concurrent transition race conditions"
  constraints:
    - "Maintain backward compatibility - no API signature changes"
    - "Minimal performance impact - lock uncontended in normal operation"
    - "Must not break existing 164 passing tests"

specification:
  description: |
    Implement asyncio.Lock coordination in StateMonitor to ensure atomic state
    transitions under concurrent access. Add test case to verify concurrent
    transition safety.
  requirements:
    functional:
      - "State transitions execute atomically under lock protection"
      - "Concurrent transition attempts serialize automatically"
      - "Lock initialized during StateMonitor.initialize()"
      - "New test case test_concurrent_transition_safety passes"
    technical:
      language: "Python"
      version: "3.9+"
      standards:
        - "Thread-safe async operation with asyncio.Lock"
        - "Comprehensive error handling with traceback logging"
        - "Professional docstrings documenting concurrency behavior"
  performance:
    - target: "No measurable overhead"
      metric: "Lock uncontended in single-task monitoring loop"

design:
  architecture: "Add async mutual exclusion to state transition methods"
  components:
    - name: "StateMonitor.__init__"
      type: "method"
      purpose: "Add _transition_lock attribute initialization"
      interface:
        inputs:
          - name: "connection_manager"
            type: "ConnectionManager"
            description: "Unchanged"
          - name: "ap_manager"
            type: "APManager"
            description: "Unchanged"
          - name: "web_server"
            type: "WebServer"
            description: "Unchanged"
        outputs:
          type: "None"
          description: "Constructor with added lock attribute"
        raises: []
      logic:
        - "Add self._transition_lock: Optional[asyncio.Lock] = None"
        - "Maintain all existing initialization"
    
    - name: "StateMonitor.initialize"
      type: "method"
      purpose: "Create asyncio.Lock instance for transition coordination"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Async initialization with lock creation"
        raises:
          - "ComponentInitializationError"
      logic:
        - "Create self._transition_lock = asyncio.Lock()"
        - "Maintain all existing initialization logic"
    
    - name: "StateMonitor.transition_to_client"
      type: "method"
      purpose: "Transition to CLIENT mode with lock protection"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Async transition under lock"
        raises:
          - "StateTransitionError"
      logic:
        - "Wrap entire method body with: async with self._transition_lock:"
        - "Indent existing transition logic under lock context"
        - "Maintain all existing deactivation and state update logic"
    
    - name: "StateMonitor.transition_to_ap_mode"
      type: "method"
      purpose: "Transition to AP_MODE with lock protection"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Async transition under lock"
        raises:
          - "StateTransitionError"
      logic:
        - "Wrap entire method body with: async with self._transition_lock:"
        - "Indent existing transition logic under lock context"
        - "Maintain all existing activation and state update logic"
    
    - name: "test_concurrent_transition_safety"
      type: "function"
      purpose: "Test case verifying concurrent transition coordination"
      interface:
        inputs: []
        outputs:
          type: "None"
          description: "Pytest test function"
        raises:
          - "AssertionError on failure"
      logic:
        - "Create StateMonitor with mock components"
        - "Call initialize() to create lock"
        - "Launch 5 concurrent transition_to_client() tasks"
        - "Launch 5 concurrent transition_to_ap_mode() tasks"
        - "Await all tasks with asyncio.gather()"
        - "Assert final state is consistent (CLIENT or AP_MODE)"
        - "Assert no exceptions raised during transitions"
        - "Verify component methods called appropriate number of times"
  
  dependencies:
    internal:
      - "asyncio.Lock from Python stdlib"
    external:
      - "pytest for test case"
      - "unittest.mock for component mocking"

data_schema:
  entities:
    - name: "StateMonitor"
      attributes:
        - name: "_transition_lock"
          type: "Optional[asyncio.Lock]"
          constraints: "Initialized in initialize(), used for transition coordination"
      validation:
        - "Lock created during initialize()"
        - "Lock acquired before state modifications"

error_handling:
  strategy: "Maintain existing error handling with lock protection"
  exceptions:
    - exception: "StateTransitionError"
      condition: "Transition failure under lock"
      handling: "Release lock automatically via context manager, propagate exception"
  logging:
    level: "DEBUG"
    format: "Standard module logger with traceback on errors"

testing:
  unit_tests:
    - scenario: "Concurrent calls to transition_to_client"
      expected: "Transitions serialize, no state corruption, final state CLIENT"
    - scenario: "Concurrent calls to transition_to_ap_mode"
      expected: "Transitions serialize, no state corruption, final state AP_MODE"
    - scenario: "Mixed concurrent transitions"
      expected: "Transitions serialize, consistent final state"
  edge_cases:
    - "Lock acquisition during shutdown"
    - "Transition error with lock held (auto-release)"
  validation:
    - "All 164 existing tests continue passing"
    - "New test_concurrent_transition_safety passes"
    - "No performance regression in monitoring loop"

deliverable:
  format_requirements:
    - "Modify src/pi_netconfig/statemonitor.py in place"
    - "Add test case to src/tests/statemonitor/test_statemonitor.py"
    - "Create completion document in workspace/prompt/"
  files:
    - path: "src/pi_netconfig/statemonitor.py"
      content: |
        Modified StateMonitor class with:
        - _transition_lock attribute in __init__
        - Lock initialization in initialize()
        - Lock context managers in transition_to_client()
        - Lock context managers in transition_to_ap_mode()
    - path: "src/tests/statemonitor/test_statemonitor.py"
      content: |
        Added test class TestConcurrentTransitions with:
        - test_concurrent_transition_safety method
        - Concurrent task launching with asyncio.gather()
        - State consistency verification
  completion_document:
    path: "workspace/prompt/prompt-0016-completion.md"
    required_fields:
      - "timestamp"
      - "files_created: [src/pi_netconfig/statemonitor.py, src/tests/statemonitor/test_statemonitor.py]"
      - "status: SUCCESS or FAILURE"
      - "test_results: pytest output showing all tests pass"

success_criteria:
  - "StateMonitor uses asyncio.Lock for transition coordination"
  - "All state transitions execute under lock protection"
  - "test_concurrent_transition_safety test passes"
  - "All existing 164 tests continue passing"
  - "No backward compatibility breaks"
  - "Code maintains thread-safety guarantees (NFR-007)"

notes: |
  Implementation details:
  
  1. Lock attribute initialization in __init__:
     ```python
     self._transition_lock: Optional[asyncio.Lock] = None
     ```
  
  2. Lock creation in initialize():
     ```python
     self._transition_lock = asyncio.Lock()
     ```
  
  3. Lock protection in transitions:
     ```python
     async def transition_to_client(self) -> None:
         async with self._transition_lock:
             # existing transition logic indented here
     ```
  
  4. Test structure:
     ```python
     @pytest.mark.asyncio
     async def test_concurrent_transition_safety():
         sm = StateMonitor(mock_conn, mock_ap, mock_web)
         await sm.initialize()
         
         tasks = [
             sm.transition_to_client() for _ in range(5)
         ] + [
             sm.transition_to_ap_mode() for _ in range(5)
         ]
         
         await asyncio.gather(*tasks, return_exceptions=False)
         
         assert sm.current_state in [SystemState.CLIENT, SystemState.AP_MODE]
     ```
  
  Lock scope strictly limited to state transition methods. Monitoring loop
  unchanged - lock transparent to existing single-task usage pattern.

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

**Copyright**: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
