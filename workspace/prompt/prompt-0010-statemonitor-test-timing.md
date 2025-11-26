Created: 2025 November 26

# T04 Prompt: StateMonitor Test Timing Fix

```yaml
prompt_info:
  id: "prompt-0010"
  task_type: "test_fix"
  source_ref: "change-0007-statemonitor-async-test-timing-fix"
  date: "2025-11-26"
  priority: "medium"

mcp_config:
  model: "claude-sonnet-4-20250514"
  temperature: 0.2
  max_tokens: 2048
  system_prompt: "Expert Python test developer. Output: corrected test method only."

context:
  purpose: "Fix async test timing by mocking CHECK_INTERVAL"
  integration: "Replace test method in src/tests/statemonitor/test_statemonitor.py"

specification:
  target: "TestMonitoringLoop.test_monitoring_loop_transitions_to_ap_after_three_failures"
  change: "Add @patch decorator to mock CHECK_INTERVAL to 0.05 seconds"

implementation:
  corrected_test: |
    @pytest.mark.asyncio
    @patch('statemonitor.CHECK_INTERVAL', 0.05)
    async def test_monitoring_loop_transitions_to_ap_after_three_failures(self):
        """Transitions to AP_MODE after 3 consecutive failures."""
        mock_conn = Mock()
        mock_conn.test_connection = AsyncMock(return_value=False)
        
        sm = StateMonitor(mock_conn, Mock(), Mock())
        sm.shutdown_event = asyncio.Event()
        sm.current_state = SystemState.CHECKING
        
        with patch.object(sm, 'transition_to_ap_mode', new_callable=AsyncMock) as mock_transition:
            call_count = 0
            async def run_and_shutdown():
                nonlocal call_count
                while call_count < 6:  # Increased from 3 to allow more iterations
                    await asyncio.sleep(0.05)
                    call_count += 1
                sm.shutdown_event.set()
            
            await asyncio.gather(
                sm.monitoring_loop(),
                run_and_shutdown()
            )
            
            assert sm.failure_count >= 3
            mock_transition.assert_called_once()

deliverable:
  code: "Corrected test method with @patch decorator"
  integration: "Replace method in test_statemonitor.py line ~226"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
