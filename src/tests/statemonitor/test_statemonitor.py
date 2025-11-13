"""Unit tests for statemonitor module.

Tests state machine transitions, monitoring loop, and component coordination.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from statemonitor import (
    SystemState,
    StateMachine,
    run,
    StateMonitorError,
    StateTransitionError,
    ComponentInitializationError
)


class TestSystemState:
    """Test SystemState enum."""
    
    def test_system_state_has_required_values(self):
        """SystemState enum contains all required states."""
        assert hasattr(SystemState, 'CHECKING')
        assert hasattr(SystemState, 'CLIENT')
        assert hasattr(SystemState, 'AP_MODE')


class TestStateMachineInitialization:
    """Test StateMachine initialization."""
    
    def test_state_machine_initializes_with_components(self):
        """Initializes with provided component instances."""
        mock_conn = Mock()
        mock_ap = Mock()
        mock_web = Mock()
        
        sm = StateMachine(mock_conn, mock_ap, mock_web)
        
        assert sm.connection_manager is mock_conn
        assert sm.ap_manager is mock_ap
        assert sm.web_server is mock_web
    
    def test_state_machine_starts_in_checking_state(self):
        """Initial state is CHECKING."""
        sm = StateMachine(Mock(), Mock(), Mock())
        assert sm.current_state == SystemState.CHECKING
    
    def test_state_machine_initializes_failure_count_zero(self):
        """Failure count starts at zero."""
        sm = StateMachine(Mock(), Mock(), Mock())
        assert sm.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_initialize_creates_shutdown_event(self):
        """Initialize creates shutdown event."""
        sm = StateMachine(Mock(), Mock(), Mock())
        await sm.initialize()
        
        assert sm.shutdown_event is not None
        assert isinstance(sm.shutdown_event, asyncio.Event)
    
    @pytest.mark.asyncio
    async def test_initialize_starts_monitoring_task(self):
        """Initialize starts monitoring loop task."""
        sm = StateMachine(Mock(), Mock(), Mock())
        
        with patch.object(sm, 'monitoring_loop', return_value=asyncio.sleep(0)):
            await sm.initialize()
            
            assert sm.monitoring_task is not None


class TestConnectionChecking:
    """Test connection status checking."""
    
    @pytest.mark.asyncio
    async def test_check_connection_returns_true_when_connected(self):
        """Returns True when connection manager reports connected."""
        mock_conn = Mock()
        mock_conn.test_connection = AsyncMock(return_value=True)
        sm = StateMachine(mock_conn, Mock(), Mock())
        
        result = await sm.check_connection()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_connection_returns_false_when_disconnected(self):
        """Returns False when connection manager reports disconnected."""
        mock_conn = Mock()
        mock_conn.test_connection = AsyncMock(return_value=False)
        sm = StateMachine(mock_conn, Mock(), Mock())
        
        result = await sm.check_connection()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_connection_returns_false_on_exception(self):
        """Returns False when connection check raises exception."""
        mock_conn = Mock()
        mock_conn.test_connection = AsyncMock(side_effect=Exception("Network error"))
        sm = StateMachine(mock_conn, Mock(), Mock())
        
        result = await sm.check_connection()
        
        assert result is False


class TestStateTransitions:
    """Test state transition logic."""
    
    @pytest.mark.asyncio
    async def test_transition_to_client_from_ap_mode(self):
        """Transitions from AP_MODE to CLIENT, deactivating AP."""
        mock_ap = Mock()
        mock_ap.deactivate_ap = AsyncMock()
        mock_web = Mock()
        mock_web.stop_server = AsyncMock()
        
        sm = StateMachine(Mock(), mock_ap, mock_web)
        sm.current_state = SystemState.AP_MODE
        sm.failure_count = 5
        
        await sm.transition_to_client()
        
        assert sm.current_state == SystemState.CLIENT
        assert sm.failure_count == 0
        mock_ap.deactivate_ap.assert_called_once()
        mock_web.stop_server.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_transition_to_client_from_checking(self):
        """Transitions from CHECKING to CLIENT without deactivating AP."""
        mock_ap = Mock()
        mock_ap.deactivate_ap = AsyncMock()
        
        sm = StateMachine(Mock(), mock_ap, Mock())
        sm.current_state = SystemState.CHECKING
        
        await sm.transition_to_client()
        
        assert sm.current_state == SystemState.CLIENT
        mock_ap.deactivate_ap.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_transition_to_client_raises_on_failure(self):
        """Raises StateTransitionError if transition fails."""
        mock_ap = Mock()
        mock_ap.deactivate_ap = AsyncMock(side_effect=Exception("Failed"))
        
        sm = StateMachine(Mock(), mock_ap, Mock())
        sm.current_state = SystemState.AP_MODE
        
        with pytest.raises(StateTransitionError):
            await sm.transition_to_client()
    
    @pytest.mark.asyncio
    async def test_transition_to_ap_mode_activates_ap_and_web(self):
        """Transitions to AP_MODE, activating AP and web server."""
        mock_ap = Mock()
        mock_ap.activate_ap = AsyncMock()
        mock_web = Mock()
        mock_web.start_server = AsyncMock()
        
        sm = StateMachine(Mock(), mock_ap, mock_web)
        sm.current_state = SystemState.CHECKING
        
        await sm.transition_to_ap_mode()
        
        assert sm.current_state == SystemState.AP_MODE
        mock_ap.activate_ap.assert_called_once()
        mock_web.start_server.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_transition_to_ap_mode_raises_on_failure(self):
        """Raises StateTransitionError if AP activation fails."""
        mock_ap = Mock()
        mock_ap.activate_ap = AsyncMock(side_effect=Exception("Failed"))
        
        sm = StateMachine(Mock(), mock_ap, Mock())
        
        with pytest.raises(StateTransitionError):
            await sm.transition_to_ap_mode()


class TestMonitoringLoop:
    """Test main monitoring loop behavior."""
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_transitions_to_client_when_connected(self):
        """Transitions to CLIENT state when connection succeeds."""
        mock_conn = Mock()
        mock_conn.test_connection = AsyncMock(return_value=True)
        
        sm = StateMachine(mock_conn, Mock(), Mock())
        sm.shutdown_event = asyncio.Event()
        sm.current_state = SystemState.CHECKING
        
        with patch.object(sm, 'transition_to_client', new_callable=AsyncMock) as mock_transition:
            # Run one iteration then shutdown
            async def run_once():
                await asyncio.sleep(0.1)
                sm.shutdown_event.set()
            
            await asyncio.gather(
                sm.monitoring_loop(),
                run_once()
            )
            
            mock_transition.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_transitions_to_ap_after_three_failures(self):
        """Transitions to AP_MODE after 3 consecutive failures."""
        mock_conn = Mock()
        mock_conn.test_connection = AsyncMock(return_value=False)
        
        sm = StateMachine(mock_conn, Mock(), Mock())
        sm.shutdown_event = asyncio.Event()
        sm.current_state = SystemState.CHECKING
        
        with patch.object(sm, 'transition_to_ap_mode', new_callable=AsyncMock) as mock_transition:
            # Simulate enough iterations to hit 3 failures
            call_count = 0
            async def run_and_shutdown():
                nonlocal call_count
                while call_count < 3:
                    await asyncio.sleep(0.1)
                    call_count += 1
                sm.shutdown_event.set()
            
            await asyncio.gather(
                sm.monitoring_loop(),
                run_and_shutdown()
            )
            
            assert sm.failure_count >= 3
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_resets_failure_count_in_client_state(self):
        """Resets failure count when connection succeeds in CLIENT state."""
        mock_conn = Mock()
        mock_conn.test_connection = AsyncMock(return_value=True)
        
        sm = StateMachine(mock_conn, Mock(), Mock())
        sm.shutdown_event = asyncio.Event()
        sm.current_state = SystemState.CLIENT
        sm.failure_count = 2
        
        async def run_once():
            await asyncio.sleep(0.1)
            sm.shutdown_event.set()
        
        await asyncio.gather(
            sm.monitoring_loop(),
            run_once()
        )
        
        assert sm.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_handles_transition_errors(self):
        """Handles state transition errors gracefully."""
        mock_conn = Mock()
        mock_conn.test_connection = AsyncMock(return_value=True)
        
        sm = StateMachine(mock_conn, Mock(), Mock())
        sm.shutdown_event = asyncio.Event()
        
        with patch.object(sm, 'transition_to_client', new_callable=AsyncMock, side_effect=StateTransitionError("Failed")), \
             patch.object(sm, 'handle_state_transition_failure', new_callable=AsyncMock) as mock_handle:
            
            async def run_once():
                await asyncio.sleep(0.1)
                sm.shutdown_event.set()
            
            await asyncio.gather(
                sm.monitoring_loop(),
                run_once()
            )
            
            mock_handle.assert_called()


class TestShutdown:
    """Test shutdown coordination."""
    
    @pytest.mark.asyncio
    async def test_shutdown_cancels_monitoring_task(self):
        """Shutdown cancels the monitoring task."""
        sm = StateMachine(Mock(), Mock(), Mock())
        sm.shutdown_event = asyncio.Event()
        sm.monitoring_task = asyncio.create_task(asyncio.sleep(1000))
        
        await sm.shutdown()
        
        assert sm.monitoring_task.cancelled()
    
    @pytest.mark.asyncio
    async def test_shutdown_deactivates_ap_when_in_ap_mode(self):
        """Shutdown deactivates AP if in AP_MODE."""
        mock_ap = Mock()
        mock_ap.deactivate_ap = AsyncMock()
        mock_web = Mock()
        mock_web.stop_server = AsyncMock()
        
        sm = StateMachine(Mock(), mock_ap, mock_web)
        sm.shutdown_event = asyncio.Event()
        sm.current_state = SystemState.AP_MODE
        sm.monitoring_task = None
        
        await sm.shutdown()
        
        mock_ap.deactivate_ap.assert_called_once()
        mock_web.stop_server.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_shutdown_handles_component_errors(self):
        """Shutdown continues despite component errors."""
        mock_ap = Mock()
        mock_ap.deactivate_ap = AsyncMock(side_effect=Exception("Failed"))
        
        sm = StateMachine(Mock(), mock_ap, Mock())
        sm.shutdown_event = asyncio.Event()
        sm.current_state = SystemState.AP_MODE
        sm.monitoring_task = None
        
        # Should not raise
        await sm.shutdown()


class TestRunFunction:
    """Test run() entry point."""
    
    @pytest.mark.asyncio
    async def test_run_initializes_state_machine(self):
        """Run function initializes StateMachine."""
        mock_conn = Mock()
        mock_ap = Mock()
        mock_web = Mock()
        
        with patch('statemonitor.StateMachine') as mock_sm_class:
            mock_sm = Mock()
            mock_sm.initialize = AsyncMock()
            mock_sm.shutdown_event = asyncio.Event()
            mock_sm.shutdown_event.set()  # Immediate shutdown
            mock_sm.shutdown = AsyncMock()
            mock_sm_class.return_value = mock_sm
            
            await run(mock_conn, mock_ap, mock_web)
            
            mock_sm_class.assert_called_once_with(mock_conn, mock_ap, mock_web)
            mock_sm.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_handles_keyboard_interrupt(self):
        """Run handles KeyboardInterrupt gracefully."""
        with patch('statemonitor.StateMachine') as mock_sm_class:
            mock_sm = Mock()
            mock_sm.initialize = AsyncMock(side_effect=KeyboardInterrupt())
            mock_sm.shutdown = AsyncMock()
            mock_sm_class.return_value = mock_sm
            
            # Should not raise
            await run(Mock(), Mock(), Mock())
    
    @pytest.mark.asyncio
    async def test_run_raises_state_monitor_error_on_failure(self):
        """Run raises StateMonitorError on critical failure."""
        with patch('statemonitor.StateMachine') as mock_sm_class:
            mock_sm = Mock()
            mock_sm.initialize = AsyncMock(side_effect=Exception("Critical error"))
            mock_sm.shutdown = AsyncMock()
            mock_sm_class.return_value = mock_sm
            
            with pytest.raises(StateMonitorError):
                await run(Mock(), Mock(), Mock())
    
    @pytest.mark.asyncio
    async def test_run_calls_shutdown_in_finally(self):
        """Run always calls shutdown in finally block."""
        with patch('statemonitor.StateMachine') as mock_sm_class:
            mock_sm = Mock()
            mock_sm.initialize = AsyncMock()
            mock_sm.shutdown_event = asyncio.Event()
            mock_sm.shutdown_event.set()
            mock_sm.shutdown = AsyncMock()
            mock_sm_class.return_value = mock_sm
            
            await run(Mock(), Mock(), Mock())
            
            mock_sm.shutdown.assert_called_once()
