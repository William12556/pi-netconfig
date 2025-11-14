"""
Unit tests for installer.py module

Test Specification: workspace/test/test-0002-installer.md
Requirements: FR-001 through FR-007
Coverage Target: 80%
"""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from installer import (
    InstallationDetector,
    SystemdInstaller,
    install,
    InstallerError,
    PrivilegeError,
    FileSystemError,
    SystemdError
)


class TestInstallationDetector:
    """Test installation detection functionality."""
    
    def test_is_service_installed_returns_true_when_exists(self):
        """Service file exists."""
        with patch('pathlib.Path.exists', return_value=True):
            assert InstallationDetector.is_service_installed() is True
    
    def test_is_service_installed_returns_false_when_missing(self):
        """Service file does not exist."""
        with patch('pathlib.Path.exists', return_value=False):
            assert InstallationDetector.is_service_installed() is False
    
    def test_get_current_script_path_returns_path(self):
        """Returns absolute path to current script."""
        path = InstallationDetector.get_current_script_path()
        assert isinstance(path, Path)
        assert path.is_absolute()


class TestSystemdInstaller:
    """Test systemd installation operations."""
    
    def test_verify_root_privileges_returns_true_for_root(self):
        """Root user verification succeeds."""
        with patch('os.geteuid', return_value=0):
            assert SystemdInstaller.verify_root_privileges() is True
    
    def test_verify_root_privileges_raises_for_non_root(self):
        """Non-root user raises PrivilegeError."""
        with patch('os.geteuid', return_value=1000):
            with pytest.raises(PrivilegeError):
                SystemdInstaller.verify_root_privileges()
    
    def test_create_directories_success(self):
        """Directories created with correct permissions."""
        with patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('os.chmod') as mock_chmod:
            
            SystemdInstaller.create_directories()
            
            assert mock_mkdir.call_count == 3
            assert mock_chmod.call_count == 3
    
    def test_create_directories_raises_on_failure(self):
        """Directory creation failure raises FileSystemError."""
        with patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied")):
            with pytest.raises(FileSystemError):
                SystemdInstaller.create_directories()
    
    def test_copy_application_success(self):
        """Application file copied with correct permissions."""
        mock_path = Path('/test/source.py')
        
        with patch('shutil.copy2') as mock_copy, \
             patch('os.chmod') as mock_chmod:
            
            SystemdInstaller.copy_application(mock_path)
            
            mock_copy.assert_called_once()
            mock_chmod.assert_called_once()
    
    def test_copy_application_raises_on_failure(self):
        """Copy failure raises FileSystemError."""
        mock_path = Path('/test/source.py')
        
        with patch('shutil.copy2', side_effect=OSError("Copy failed")):
            with pytest.raises(FileSystemError):
                SystemdInstaller.copy_application(mock_path)
    
    def test_generate_systemd_unit_returns_content(self):
        """Unit file content generated correctly."""
        content = SystemdInstaller.generate_systemd_unit()
        
        assert '[Unit]' in content
        assert '[Service]' in content
        assert '[Install]' in content
        assert 'ExecStart=/usr/bin/python3' in content
    
    def test_install_systemd_unit_success(self):
        """Unit file installed and daemon reloaded."""
        unit_content = "test content"
        
        with patch('builtins.open', mock_open()) as mock_file, \
             patch('subprocess.run') as mock_run:
            
            SystemdInstaller.install_systemd_unit(unit_content)
            
            mock_file.assert_called_once()
            mock_run.assert_called_once()
    
    def test_install_systemd_unit_raises_on_daemon_reload_failure(self):
        """Daemon reload failure raises SystemdError."""
        unit_content = "test content"
        
        with patch('builtins.open', mock_open()), \
             patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'systemctl', stderr='Failed')):
            
            with pytest.raises(SystemdError):
                SystemdInstaller.install_systemd_unit(unit_content)
    
    def test_enable_and_start_service_success(self):
        """Service enabled and started successfully."""
        with patch('subprocess.run') as mock_run:
            SystemdInstaller.enable_and_start_service()
            
            assert mock_run.call_count == 2
    
    def test_enable_and_start_service_raises_on_failure(self):
        """Service start failure raises SystemdError."""
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'systemctl', stderr='Failed')):
            with pytest.raises(SystemdError):
                SystemdInstaller.enable_and_start_service()
    
    def test_rollback_installation_best_effort(self):
        """Rollback attempts cleanup without raising."""
        with patch('os.path.isdir', return_value=True), \
             patch('shutil.rmtree') as mock_rmtree, \
             patch('os.path.exists', return_value=True), \
             patch('os.remove') as mock_remove:
            
            # Should not raise even if cleanup fails
            SystemdInstaller.rollback_installation()
            
            assert mock_rmtree.called or mock_remove.called


class TestInstallFunction:
    """Test main install() entry point."""
    
    def test_install_skips_when_already_installed(self):
        """Installation skipped if service already exists."""
        with patch('installer.InstallationDetector.is_service_installed', return_value=True):
            result = install()
            assert result is True
    
    def test_install_fails_without_root_privileges(self):
        """Installation fails for non-root user."""
        with patch('installer.InstallationDetector.is_service_installed', return_value=False), \
             patch('installer.SystemdInstaller.verify_root_privileges', side_effect=PrivilegeError("Need root")):
            
            result = install()
            assert result is False
    
    def test_install_succeeds_with_all_steps(self):
        """Complete installation succeeds."""
        with patch('installer.InstallationDetector.is_service_installed', return_value=False), \
             patch('installer.SystemdInstaller.verify_root_privileges', return_value=True), \
             patch('installer.SystemdInstaller.create_directories'), \
             patch('installer.InstallationDetector.get_current_script_path', return_value=Path('/test')), \
             patch('installer.SystemdInstaller.copy_application'), \
             patch('installer.SystemdInstaller.generate_systemd_unit', return_value='unit content'), \
             patch('installer.SystemdInstaller.install_systemd_unit'), \
             patch('installer.SystemdInstaller.enable_and_start_service'):
            
            result = install()
            assert result is True
    
    def test_install_rolls_back_on_filesystem_error(self):
        """Installation rolls back on FileSystemError."""
        with patch('installer.InstallationDetector.is_service_installed', return_value=False), \
             patch('installer.SystemdInstaller.verify_root_privileges', return_value=True), \
             patch('installer.SystemdInstaller.create_directories', side_effect=FileSystemError("Failed")), \
             patch('installer.SystemdInstaller.rollback_installation') as mock_rollback:
            
            result = install()
            
            assert result is False
            mock_rollback.assert_called_once()
    
    def test_install_rolls_back_on_systemd_error(self):
        """Installation rolls back on SystemdError."""
        with patch('installer.InstallationDetector.is_service_installed', return_value=False), \
             patch('installer.SystemdInstaller.verify_root_privileges', return_value=True), \
             patch('installer.SystemdInstaller.create_directories'), \
             patch('installer.InstallationDetector.get_current_script_path', return_value=Path('/test')), \
             patch('installer.SystemdInstaller.copy_application'), \
             patch('installer.SystemdInstaller.generate_systemd_unit', return_value='unit content'), \
             patch('installer.SystemdInstaller.install_systemd_unit', side_effect=SystemdError("Failed")), \
             patch('installer.SystemdInstaller.rollback_installation') as mock_rollback:
            
            result = install()
            
            assert result is False
            mock_rollback.assert_called_once()
