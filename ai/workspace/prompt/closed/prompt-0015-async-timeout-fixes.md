# T04 Prompt: Async Test Timeout Fixes

## Prompt Information

- **ID**: prompt-0015
- **Task Type**: debug
- **Source**: Test hang in test_run_service_initializes_state_monitor
- **Date**: 2025-11-27
- **Priority**: critical

## Context

Tests hanging on async functions that create infinite loops. `run_service()` and `monitoring_loop()` run indefinitely until shutdown_event set.

## Specification

### Requirements

**Functional**:
- Wrap all `run_service()` and `monitoring_loop()` calls with `asyncio.wait_for(timeout=1.0)`
- Mock `CHECK_INTERVAL` to 0.05s in StateMonitor tests
- Ensure shutdown_event set before timeout

**Technical**:
- Python 3.9+
- pytest-asyncio
- asyncio.wait_for for timeout protection

## Design

### Pattern for run_service() tests

```python
@pytest.mark.asyncio
async def test_run_service_initializes_state_monitor(self):
    """Test run_service initializes StateMonitor."""
    with patch('main.StateMonitor') as mock_sm, \
         patch('main.ConnectionManager'), \
         patch('main.APManager'), \
         patch('main.WebServerManager'):
        
        mock_instance = Mock()
        mock_instance.initialize = AsyncMock()
        mock_instance.shutdown_event = asyncio.Event()
        mock_sm.return_value = mock_instance
        
        # Set shutdown immediately to prevent hang
        async def run_with_shutdown():
            mock_instance.shutdown_event.set()
            await asyncio.sleep(0.01)
        
        await asyncio.wait_for(
            asyncio.gather(run_service(), run_with_shutdown()),
            timeout=1.0
        )
        
        mock_sm.assert_called_once()
```

### Pattern for monitoring_loop() tests

```python
@pytest.mark.asyncio
async def test_monitoring_loop_transitions_to_ap_after_three_failures(self):
    """Monitoring loop transitions after 3 failures."""
    with patch('statemonitor.CHECK_INTERVAL', 0.05):
        connection = Mock()
        connection.test_connection = Mock(return_value=False)
        ap_manager = Mock()
        web_server = Mock()
        
        sm = StateMonitor(connection, ap_manager, web_server)
        sm.initialize()
        
        async def shutdown_after_iterations():
            await asyncio.sleep(0.25)  # 5 iterations at 0.05s
            sm.shutdown_event.set()
        
        await asyncio.wait_for(
            asyncio.gather(sm.monitoring_loop(), shutdown_after_iterations()),
            timeout=1.0
        )
        
        assert sm.failure_count >= 3
```

## Deliverable

### Files

1. `src/tests/servicecontroller/test_main.py` - Add timeouts to run_service tests
2. `src/tests/servicecontroller/test_servicecontroller.py` - Add timeouts to run_service tests  
3. `src/tests/statemonitor/test_statemonitor.py` - Add timeouts and CHECK_INTERVAL mocks

### Completion Document

Path: `workspace/prompt/prompt-0015-completion.md`

## Success Criteria

- No tests hang (all complete within 5 seconds total)
- All async tests use `asyncio.wait_for(timeout=1.0)`
- StateMonitor tests mock CHECK_INTERVAL to 0.05s

---

**Metadata**:
- Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
- Template Version: 1.0
- Schema Type: t04_prompt
