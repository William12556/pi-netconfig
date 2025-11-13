"""Unit tests for connectionmanager module.

Tests network scanning, connection testing, and configuration management.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import subprocess
import socket
import json
from pathlib import Path
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from connectionmanager import (
    NetworkInfo,
    ConnectionTester,
    NetworkScanner,
    ConfigManager,
    ConnectionManagerError,
    ConfigurationError,
    NetworkScanError
)


class TestNetworkInfo:
    """Test NetworkInfo dataclass."""
    
    def test_network_info_creation(self):
        """NetworkInfo initializes with all fields."""
        net = NetworkInfo("TestSSID", 85, "WPA2", "2.4GHz")
        
        assert net.ssid == "TestSSID"
        assert net.signal_strength == 85
        assert net.security == "WPA2"
        assert net.frequency == "2.4GHz"


class TestConnectionTester:
    """Test connection testing functionality."""
    
    def test_connection_test_returns_true_when_connected(self):
        """Returns True when socket connection succeeds."""
        with patch('socket.create_connection', return_value=Mock()):
            result = ConnectionTester.test_connection()
            assert result is True
    
    def test_connection_test_returns_false_when_all_fail(self):
        """Returns False when all hosts fail."""
        with patch('socket.create_connection', side_effect=socket.error("Failed")):
            result = ConnectionTester.test_connection()
            assert result is False
    
    def test_connection_test_tries_multiple_hosts(self):
        """Attempts both 8.8.8.8 and 1.1.1.1."""
        with patch('socket.create_connection', side_effect=[socket.error("Failed"), Mock()]) as mock_conn:
            result = ConnectionTester.test_connection()
            
            assert result is True
            assert mock_conn.call_count == 2


class TestNetworkScanner:
    """Test network scanning functionality."""
    
    def test_scan_networks_returns_list(self):
        """Scan returns list of NetworkInfo objects."""
        nmcli_output = b"WiFi1:75:WPA2:2.4GHz\nWiFi2:90:WPA3:5GHz\n"
        
        with patch('subprocess.check_output', return_value=nmcli_output):
            networks = NetworkScanner.scan_networks()
            
            assert len(networks) == 2
            assert all(isinstance(n, NetworkInfo) for n in networks)
    
    def test_scan_networks_sorts_by_signal_strength(self):
        """Networks sorted by signal strength descending."""
        nmcli_output = b"WiFi1:75:WPA2:2.4GHz\nWiFi2:90:WPA3:5GHz\nWiFi3:60:WPA2:2.4GHz\n"
        
        with patch('subprocess.check_output', return_value=nmcli_output):
            networks = NetworkScanner.scan_networks()
            
            assert networks[0].signal_strength == 90
            assert networks[1].signal_strength == 75
            assert networks[2].signal_strength == 60
    
    def test_scan_networks_removes_duplicates(self):
        """Duplicate SSIDs removed."""
        nmcli_output = b"WiFi1:75:WPA2:2.4GHz\nWiFi1:70:WPA2:2.4GHz\n"
        
        with patch('subprocess.check_output', return_value=nmcli_output):
            networks = NetworkScanner.scan_networks()
            
            assert len(networks) == 1
            assert networks[0].ssid == "WiFi1"
    
    def test_scan_networks_raises_on_nmcli_failure(self):
        """Raises NetworkScanError when nmcli fails."""
        with patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(1, 'nmcli')):
            with pytest.raises(NetworkScanError):
                NetworkScanner.scan_networks()


class TestConfigManager:
    """Test configuration management."""
    
    def test_configure_network_validates_ssid(self):
        """Rejects invalid SSID format."""
        with pytest.raises(ConfigurationError, match="Invalid SSID"):
            ConfigManager.configure_network("", "password123")
        
        with pytest.raises(ConfigurationError, match="Invalid SSID"):
            ConfigManager.configure_network("a" * 33, "password123")
        
        with pytest.raises(ConfigurationError, match="Invalid SSID"):
            ConfigManager.configure_network("test;ssid", "password123")
    
    def test_configure_network_validates_password(self):
        """Rejects invalid password length."""
        with pytest.raises(ConfigurationError, match="Invalid password"):
            ConfigManager.configure_network("TestSSID", "short")
        
        with pytest.raises(ConfigurationError, match="Invalid password"):
            ConfigManager.configure_network("TestSSID", "a" * 64)
    
    def test_configure_network_deletes_existing_connection(self):
        """Deletes existing connection with same SSID."""
        with patch('subprocess.run') as mock_run, \
             patch.object(ConfigManager, 'persist_configuration'):
            
            ConfigManager.configure_network("TestSSID", "password123")
            
            # First call should be delete
            assert mock_run.call_args_list[0][0][0][2] == 'delete'
    
    def test_configure_network_creates_new_connection(self):
        """Creates new WiFi connection."""
        with patch('subprocess.run') as mock_run, \
             patch.object(ConfigManager, 'persist_configuration'):
            
            ConfigManager.configure_network("TestSSID", "password123")
            
            # Second call should be add
            add_call = mock_run.call_args_list[1][0][0]
            assert 'add' in add_call
            assert 'TestSSID' in add_call
    
    def test_configure_network_activates_connection(self):
        """Activates newly created connection."""
        with patch('subprocess.run') as mock_run, \
             patch.object(ConfigManager, 'persist_configuration'):
            
            ConfigManager.configure_network("TestSSID", "password123")
            
            # Third call should be up
            up_call = mock_run.call_args_list[2][0][0]
            assert 'up' in up_call
    
    def test_configure_network_persists_configuration(self):
        """Calls persist_configuration with SSID."""
        with patch('subprocess.run'), \
             patch.object(ConfigManager, 'persist_configuration') as mock_persist:
            
            ConfigManager.configure_network("TestSSID", "password123")
            
            mock_persist.assert_called_once_with("TestSSID")
    
    def test_configure_network_raises_on_nmcli_failure(self):
        """Raises ConfigurationError on nmcli failure."""
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'nmcli', stderr=b'Error')):
            with pytest.raises(ConfigurationError):
                ConfigManager.configure_network("TestSSID", "password123")
    
    def test_configure_network_thread_safe(self):
        """Uses lock for thread safety."""
        with patch('subprocess.run'), \
             patch.object(ConfigManager, 'persist_configuration'), \
             patch.object(ConfigManager._lock, 'acquire', wraps=ConfigManager._lock.acquire) as mock_acquire:
            
            ConfigManager.configure_network("TestSSID", "password123")
            
            mock_acquire.assert_called()
    
    def test_persist_configuration_creates_directory(self):
        """Creates config directory if missing."""
        config_data = {
            'configured_ssid': 'TestSSID',
            'last_connected': '2025-11-13T10:00:00',
            'ap_password': 'piconfig123'
        }
        
        with patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('builtins.open', mock_open()), \
             patch('json.dump'):
            
            ConfigManager.persist_configuration("TestSSID")
            
            mock_mkdir.assert_called_once()
    
    def test_persist_configuration_writes_json(self):
        """Writes configuration to JSON file."""
        with patch('pathlib.Path.mkdir'), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('json.dump') as mock_json_dump:
            
            ConfigManager.persist_configuration("TestSSID")
            
            mock_json_dump.assert_called_once()
            written_config = mock_json_dump.call_args[0][0]
            assert written_config['configured_ssid'] == "TestSSID"
    
    def test_persist_configuration_thread_safe(self):
        """Uses lock for thread safety."""
        with patch('pathlib.Path.mkdir'), \
             patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch.object(ConfigManager._lock, 'acquire', wraps=ConfigManager._lock.acquire) as mock_acquire:
            
            ConfigManager.persist_configuration("TestSSID")
            
            mock_acquire.assert_called()
    
    def test_load_configuration_returns_ssid_when_exists(self):
        """Returns SSID from existing config file."""
        config_data = json.dumps({
            'configured_ssid': 'TestSSID',
            'last_connected': '2025-11-13T10:00:00'
        })
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=config_data)):
            
            ssid = ConfigManager.load_configuration()
            
            assert ssid == "TestSSID"
    
    def test_load_configuration_returns_none_when_missing(self):
        """Returns None when config file doesn't exist."""
        with patch('pathlib.Path.exists', return_value=False):
            ssid = ConfigManager.load_configuration()
            
            assert ssid is None
    
    def test_load_configuration_thread_safe(self):
        """Uses lock for thread safety."""
        with patch('pathlib.Path.exists', return_value=False), \
             patch.object(ConfigManager._lock, 'acquire', wraps=ConfigManager._lock.acquire) as mock_acquire:
            
            ConfigManager.load_configuration()
            
            mock_acquire.assert_called()
