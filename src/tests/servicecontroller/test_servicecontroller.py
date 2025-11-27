"""
Unit tests for main.py module

Test Specification: workspace/test/test-0006-servicecontroller.md
Requirements: FR-023, FR-070-074
Coverage Target: 80%
"""

import pytest
import asyncio
import signal
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from tempfile import TemporaryDirectory
from pathlib import Path

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
    LoggingConfigurationError
)


class TestExecutionModeDetection:
    """Test execution mode detection logic."""
    
    @patch('main.InstallationDetector.is_service_installed')
    def test_detect_execution_mode_returns_bootstrap_when_not_installed(self, mock_is_installed):
        """TC-001: Verify detect_execution_mode returns 'bootstrap' when service not installed."""
        mock_is_installed.return_value = False
        
        mode = detect_execution_mode()
        
        assert mode == 'bootstrap'
    
    @patch.dict('os.environ', {'INVOCATION_ID': 'test123'})
    @patch('main.InstallationDetector.is_service_installed')
    def test_detect_execution_mode_returns_service_when_under_systemd(self, mock_is_installed):
        """TC-002: Verify detect_execution_mode returns 'service' when under systemd."""
        mock_is_installed.return_value = True
        
        mode = detect_execution_mode()
        
        assert mode == 'service'
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('main.InstallationDetector.is_service_installed')
    def test_detect_execution_mode_returns_manual_when_installed_but_not_systemd(self, mock_is_installed):
        """TC-003: Verify detect_execution_mode returns 'manual' when installed but not systemd."""
        mock_is_installed.return_value = True
        
        mode = detect_execution_mode()
        
        assert mode == 'manual'


class TestPrivilegeVerification:
    """Test privilege checking functionality."""
    
    @patch('os.geteuid')
    def test_verify_root_privileges_returns_true_for_uid_zero(self, mock_geteuid):
        """TC-004: Verify verify_root_privileges returns True for UID 0."""
        mock_geteuid.return_value = 0
        
        result = verify_root_privileges()
        
        assert result is True
    
    @patch('os.geteuid')
    def test_verify_root_privileges_returns_false_for_non_root_uid(self, mock_geteuid):
        """TC-005: Verify verify_root_privileges returns False for non-root UID."""
        mock_geteuid.return_value = 1000
        
        result = verify_root_privileges()
        
        assert result is False


class TestLoggingConfiguration:
    """Test logging configuration functionality."""
    
    def test_configure_logging_creates_file_handler(self):
        """TC-006: Verify configure_logging creates file handler."""
        with patch('pathlib.Path.mkdir'), \
             patch('logging.FileHandler'), \
             patch('logging.getLogger') as mock_get_logger:
            
            mock_logger = Mock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            
            configure_logging('service')
            
            # Should add file handler
            assert mock_logger.addHandler.call_count >= 1
    
    def test_configure_logging_adds_console_handler_in_manual_mode(self):
        """TC-007: Verify configure_logging adds console handler in manual mode."""
        with patch('pathlib.Path.mkdir'), \
             patch('logging.FileHandler'), \
             patch('logging.StreamHandler'), \
             patch('logging.getLogger') as mock_get_logger:
            
            mock_logger = Mock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            
            configure_logging('manual')
            
            # Should have at least 2 handlers (file + console)
            assert mock_logger.addHandler.call_count >= 2
    
    def test_configure_logging_raises_error_on_permission_denied(self):
        """TC-008: Verify configure_logging raises LoggingConfigurationError on permission denied."""
        with patch('logging.FileHandler', side_effect=PermissionError("Permission denied")):
            with pytest.raises(LoggingConfigurationError):
                configure_logging('service')


class TestSignalHandling:
    """Test signal handling functionality."""
    
    def test_signal_handler_sets_shutdown_event(self):
        """TC-009: Verify signal_handler sets shutdown_event."""
        mock_event = Mock()
        
        with patch('main.shutdown_event', mock_event):
            signal_handler(signal.SIGTERM, None)
            
            mock_event.set.assert_called_once()
    
    @patch('signal.signal')
    def test_register_signal_handlers_registers_sigterm_and_sigint(self, mock_signal):
        """TC-010: Verify register_signal_handlers registers SIGTERM and SIGINT."""
        register_signal_handlers()
        
        # Should register both SIGTERM and SIGINT
        assert mock_signal.call_count == 2
        registered_signals = [call[0][0] for call in mock_signal.call_args_list]
        assert signal.SIGTERM in registered_signals
        assert signal.SIGINT in registered_signals


class TestGracefulShutdown:
    """Test graceful shutdown functionality."""
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown_calls_state_monitor_shutdown(self):
        """TC-011: Verify graceful_shutdown calls StateMonitor.shutdown()."""
        mock_state_monitor = Mock()
        mock_state_monitor.shutdown = AsyncMock()
        
        with patch('main.state_monitor', mock_state_monitor):
            await graceful_shutdown()
            
            mock_state_monitor.shutdown.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown_handles_timeout_gracefully(self):
        """TC-012: Verify graceful_shutdown handles timeout gracefully."""
        mock_state_monitor = Mock()
        mock_state_monitor.shutdown = AsyncMock(side_effect=asyncio.TimeoutError())
        
        # Should not raise an exception
        with patch('main.state_monitor', mock_state_monitor), \
             patch('asyncio.wait_for', side_effect=asyncio.TimeoutError()):
            await graceful_shutdown()


class TestRunService:
    """Test service execution functionality."""
    
    @pytest.mark.asyncio
    async def test_run_service_creates_state_monitor_and_waits_for_shutdown(self):
        """TC-013: Verify run_service creates StateMonitor and waits for shutdown."""
        with patch('main.StateMonitor') as mock_state_monitor_class, \
             patch('main.graceful_shutdown', return_value=asyncio.sleep(0)), \
             patch('asyncio.Event') as mock_event_class:
            
            mock_state_monitor = Mock()
            mock_state_monitor.run = Mock(return_value=asyncio.sleep(0))
            mock_state_monitor_class.return_value = mock_state_monitor
            
            mock_event = Mock()
            mock_event.wait = Mock(return_value=asyncio.sleep(0))
            mock_event_class.return_value = mock_event
            
            await run_service()
            
            mock_state_monitor_class.assert_called_once()


class TestMainFunction:
    """Test main entry point functionality."""
    
    @patch('main.install')
    @patch('main.verify_root_privileges')
    @patch('main.detect_execution_mode')
    def test_main_calls_install_in_bootstrap_mode(self, mock_detect, mock_verify, mock_install):
        """TC-014: Verify main() calls install() in bootstrap mode."""
        mock_detect.return_value = 'bootstrap'
        mock_verify.return_value = True
        mock_install.return_value = True
        
        exit_code = main()
        
        assert exit_code == 0
        mock_install.assert_called_once()
    
    @patch('main.install')
    @patch('main.verify_root_privileges')
    @patch('main.detect_execution_mode')
    def test_main_returns_one_when_install_fails(self, mock_detect, mock_verify, mock_install):
        """TC-015: Verify main() returns 1 when install() fails."""
        mock_detect.return_value = 'bootstrap'
        mock_verify.return_value = True
        mock_install.return_value = False
        
        exit_code = main()
        
        assert exit_code == 1
    
    @patch('main.register_signal_handlers')
    @patch('main.configure_logging')
    @patch('main.verify_root_privileges')
    @patch('main.detect_execution_mode')
    def test_main_runs_service_in_service_mode(self, mock_detect, mock_verify, mock_configure, mock_register):
        """TC-016: Verify main() runs service in service mode."""
        mock_detect.return_value = 'service'
        mock_verify.return_value = True
        
        with patch('asyncio.run') as mock_asyncio_run:
            main()
            
            mock_configure.assert_called_once_with('service')
            mock_register.assert_called_once()
            mock_asyncio_run.assert_called_once()
    
    @patch('main.verify_root_privileges')
    def test_main_returns_one_without_root_privileges(self, mock_verify):
        """TC-017: Verify main() returns 1 without root privileges."""
        mock_verify.return_value = False
        
        exit_code = main()
        
        assert exit_code == 1