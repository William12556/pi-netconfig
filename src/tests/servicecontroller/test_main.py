"""Unit tests for main.py (ServiceController).

Tests execution mode detection, logging, signal handling, and service lifecycle.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import asyncio
import signal
import sys

import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from main import (
    detect_execution_mode,
    verify_root_privileges,
    configure_logging,
    signal_handler,
    register_signal_handlers,
    graceful_shutdown,
    run_service,
    main,
    ServiceControllerError,
    LoggingConfigurationError,
    PrivilegeError
)


class TestExecutionModeDetection:
    """Test execution mode detection logic."""
    
    def test_detect_bootstrap_mode_when_service_not_installed(self):
        """Returns 'bootstrap' when service file doesn't exist."""
        with patch('main.Installer.is_service_installed', return_value=False):
            assert detect_execution_mode() == 'bootstrap'
    
    def test_detect_service_mode_when_systemd_context(self):
        """Returns 'service' when INVOCATION_ID present."""
        with patch('main.Installer.is_service_installed', return_value=True), \
             patch.dict('os.environ', {'INVOCATION_ID': 'test-id'}):
            assert detect_execution_mode() == 'service'
    
    def test_detect_manual_mode_when_service_installed_no_systemd(self):
        """Returns 'manual' when service exists but no INVOCATION_ID."""
        with patch('main.Installer.is_service_installed', return_value=True), \
             patch.dict('os.environ', {}, clear=True):
            assert detect_execution_mode() == 'manual'
    
    def test_detect_mode_returns_manual_on_exception(self):
        """Returns 'manual' as safe fallback on error."""
        with patch('main.Installer.is_service_installed', side_effect=Exception("Error")):
            assert detect_execution_mode() == 'manual'


class TestPrivilegeVerification:
    """Test root privilege checking."""
    
    def test_verify_root_privileges_returns_true_for_root(self):
        """Returns True when UID is 0."""
        with patch('os.geteuid', return_value=0):
            assert verify_root_privileges() is True
    
    def test_verify_root_privileges_returns_false_for_non_root(self):
        """Returns False when UID is not 0."""
        with patch('os.geteuid', return_value=1000):
            assert verify_root_privileges() is False
    
    def test_verify_root_privileges_handles_exception(self):
        """Returns False on exception."""
        with patch('os.geteuid', side_effect=Exception("Error")):
            assert verify_root_privileges() is False


class TestLoggingConfiguration:
    """Test logging setup."""
    
    def test_configure_logging_creates_file_handler(self):
        """File handler created for all modes."""
        with patch('pathlib.Path.mkdir'), \
             patch('logging.FileHandler') as mock_file_handler, \
             patch('logging.StreamHandler'), \
             patch('os.chmod'):
            
            configure_logging('service')
            
            mock_file_handler.assert_called_once()
    
    def test_configure_logging_adds_console_handler_in_manual_mode(self):
        """Console handler added only in manual mode."""
        with patch('pathlib.Path.mkdir'), \
             patch('logging.FileHandler'), \
             patch('logging.StreamHandler') as mock_console_handler, \
             patch('os.chmod'):
            
            configure_logging('manual')
            
            mock_console_handler.assert_called_once()
    
    def test_configure_logging_no_console_in_service_mode(self):
        """No console handler in service mode."""
        with patch('pathlib.Path.mkdir'), \
             patch('logging.FileHandler'), \
             patch('logging.StreamHandler') as mock_console_handler, \
             patch('os.chmod'):
            
            configure_logging('service')
            
            mock_console_handler.assert_not_called()
    
    def test_configure_logging_raises_on_file_failure(self):
        """Raises LoggingConfigurationError if log file inaccessible."""
        with patch('pathlib.Path.mkdir'), \
             patch('logging.FileHandler', side_effect=PermissionError("Denied")):
            
            with pytest.raises(LoggingConfigurationError):
                configure_logging('service')


class TestSignalHandling:
    """Test signal handler registration and execution."""
    
    def test_signal_handler_sets_shutdown_event(self):
        """Signal handler sets global shutdown event."""
        mock_event = Mock()
        
        with patch('main.shutdown_event', mock_event):
            signal_handler(signal.SIGTERM, None)
            
            mock_event.set.assert_called_once()
    
    def test_signal_handler_exits_if_no_event(self):
        """Signal handler calls sys.exit if event not initialized."""
        with patch('main.shutdown_event', None), \
             patch('sys.exit') as mock_exit:
            
            signal_handler(signal.SIGTERM, None)
            
            mock_exit.assert_called_once_with(0)
    
    def test_register_signal_handlers_registers_sigterm_sigint(self):
        """Registers handlers for SIGTERM and SIGINT."""
        with patch('signal.signal') as mock_signal:
            register_signal_handlers()
            
            calls = mock_signal.call_args_list
            assert len(calls) == 2
            assert calls[0][0][0] == signal.SIGTERM
            assert calls[1][0][0] == signal.SIGINT
    
    def test_register_signal_handlers_raises_on_failure(self):
        """Raises ServiceControllerError if registration fails."""
        with patch('signal.signal', side_effect=Exception("Failed")):
            with pytest.raises(ServiceControllerError):
                register_signal_handlers()


class TestGracefulShutdown:
    """Test graceful shutdown coordination."""
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown_calls_state_monitor_shutdown(self):
        """Calls StateMonitor.shutdown() when active."""
        mock_monitor = Mock()
        mock_monitor.shutdown = Mock(return_value=asyncio.sleep(0))
        
        with patch('main.state_monitor', mock_monitor):
            await graceful_shutdown()
            
            mock_monitor.shutdown.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown_handles_timeout(self):
        """Handles shutdown timeout gracefully."""
        mock_monitor = Mock()
        async def slow_shutdown():
            await asyncio.sleep(20)
        mock_monitor.shutdown = slow_shutdown
        
        with patch('main.state_monitor', mock_monitor):
            await graceful_shutdown()  # Should timeout but not raise
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown_handles_no_monitor(self):
        """Handles case where state_monitor is None."""
        with patch('main.state_monitor', None):
            await graceful_shutdown()  # Should not raise


class TestRunService:
    """Test service loop execution."""
    
    @pytest.mark.asyncio
    async def test_run_service_creates_shutdown_event(self):
        """Creates shutdown event on startup."""
        mock_monitor = Mock()
        mock_monitor.run = Mock(return_value=asyncio.sleep(0))
        
        with patch('main.StateMonitor', return_value=mock_monitor), \
             patch('main.graceful_shutdown', return_value=asyncio.sleep(0)), \
             patch('asyncio.Event') as mock_event_class:
            
            mock_event = Mock()
            mock_event.wait = Mock(return_value=asyncio.sleep(0))
            mock_event_class.return_value = mock_event
            
            await run_service()
            
            mock_event_class.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_service_initializes_state_monitor(self):
        """Initializes and starts StateMonitor."""
        mock_monitor = Mock()
        mock_monitor.run = Mock(return_value=asyncio.sleep(0))
        
        with patch('main.StateMonitor', return_value=mock_monitor) as mock_class, \
             patch('main.graceful_shutdown', return_value=asyncio.sleep(0)):
            
            await run_service()
            
            mock_class.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_service_raises_on_critical_failure(self):
        """Raises ServiceControllerError on critical failure."""
        with patch('main.StateMonitor', side_effect=Exception("Critical error")):
            with pytest.raises(ServiceControllerError):
                await run_service()


class TestMainFunction:
    """Test main() entry point."""
    
    def test_main_bootstrap_mode_calls_installer(self):
        """Bootstrap mode invokes Installer.install()."""
        with patch('main.detect_execution_mode', return_value='bootstrap'), \
             patch('main.verify_root_privileges', return_value=True), \
             patch('main.Installer.install', return_value=True) as mock_install:
            
            result = main()
            
            mock_install.assert_called_once()
            assert result == 0
    
    def test_main_bootstrap_mode_returns_error_without_root(self):
        """Bootstrap mode returns 1 without root privileges."""
        with patch('main.detect_execution_mode', return_value='bootstrap'), \
             patch('main.verify_root_privileges', return_value=False):
            
            result = main()
            
            assert result == 1
    
    def test_main_service_mode_configures_logging(self):
        """Service mode configures logging before startup."""
        with patch('main.detect_execution_mode', return_value='service'), \
             patch('main.configure_logging') as mock_logging, \
             patch('main.verify_root_privileges', return_value=True), \
             patch('main.register_signal_handlers'), \
             patch('asyncio.run'):
            
            main()
            
            mock_logging.assert_called_once_with('service')
    
    def test_main_service_mode_verifies_root(self):
        """Service mode verifies root privileges."""
        with patch('main.detect_execution_mode', return_value='service'), \
             patch('main.configure_logging'), \
             patch('main.verify_root_privileges', return_value=False):
            
            result = main()
            
            assert result == 1
    
    def test_main_service_mode_starts_event_loop(self):
        """Service mode starts asyncio event loop."""
        with patch('main.detect_execution_mode', return_value='service'), \
             patch('main.configure_logging'), \
             patch('main.verify_root_privileges', return_value=True), \
             patch('main.register_signal_handlers'), \
             patch('asyncio.run') as mock_run:
            
            main()
            
            mock_run.assert_called_once()
    
    def test_main_handles_keyboard_interrupt(self):
        """Handles KeyboardInterrupt gracefully."""
        with patch('main.detect_execution_mode', return_value='service'), \
             patch('main.configure_logging'), \
             patch('main.verify_root_privileges', return_value=True), \
             patch('main.register_signal_handlers'), \
             patch('asyncio.run', side_effect=KeyboardInterrupt()):
            
            result = main()
            
            assert result == 0
    
    def test_main_returns_error_on_service_controller_error(self):
        """Returns 1 on ServiceControllerError."""
        with patch('main.detect_execution_mode', return_value='service'), \
             patch('main.configure_logging'), \
             patch('main.verify_root_privileges', return_value=True), \
             patch('main.register_signal_handlers', side_effect=ServiceControllerError("Error")):
            
            result = main()
            
            assert result == 1
    
    def test_main_returns_error_on_unexpected_exception(self):
        """Returns 1 on unexpected exception."""
        with patch('main.detect_execution_mode', side_effect=Exception("Unexpected")):
            result = main()
            
            assert result == 1
