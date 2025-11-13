"""Unit tests for apmanager module.

Tests access point creation, activation, and management.
"""

import pytest
from unittest.mock import Mock, patch
from subprocess import CalledProcessError

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from apmanager import (
    AccessPoint,
    activate_ap,
    deactivate_ap,
    get_ap_ssid,
    is_active,
    APManagerError,
    InterfaceDetectionError,
    APActivationError,
    ProfileCreationError
)


class TestAccessPointInitialization:
    """Test AccessPoint initialization."""
    
    def test_access_point_initializes_with_interface(self):
        """Initializes and detects WiFi interface."""
        nmcli_output = b"DEVICE  TYPE  STATE\nwlan0   wifi  connected\n"
        
        with patch('subprocess.check_output', return_value=nmcli_output):
            ap = AccessPoint()
            
            assert ap.interface == "wlan0"
    
    def test_access_point_raises_when_no_wifi_interface(self):
        """Raises InterfaceDetectionError when no WiFi interface found."""
        nmcli_output = b"DEVICE  TYPE  STATE\neth0   ethernet  connected\n"
        
        with patch('subprocess.check_output', return_value=nmcli_output):
            with pytest.raises(InterfaceDetectionError):
                AccessPoint()
    
    def test_access_point_gets_mac_address(self):
        """Retrieves MAC address from nmcli."""
        device_output = b"DEVICE  TYPE  STATE\nwlan0   wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]):
            ap = AccessPoint()
            
            assert ap.mac_address == "AA:BB:CC:DD:EE:FF"
    
    def test_access_point_generates_ssid_from_mac(self):
        """Generates SSID using last 4 MAC chars."""
        device_output = b"DEVICE  TYPE  STATE\nwlan0   wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]):
            ap = AccessPoint()
            
            assert ap.ssid == "PiConfig-EE:FF"
    
    def test_access_point_initializes_ap_active_false(self):
        """Initializes with ap_active set to False."""
        device_output = b"DEVICE  TYPE  STATE\nwlan0   wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]):
            ap = AccessPoint()
            
            assert ap.ap_active is False


class TestInterfaceDetection:
    """Test WiFi interface detection."""
    
    def test_get_wifi_interface_parses_nmcli_output(self):
        """Parses nmcli device status output correctly."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]):
            ap = AccessPoint()
            
            assert ap.interface is not None
    
    def test_get_wifi_interface_raises_on_nmcli_failure(self):
        """Raises InterfaceDetectionError on nmcli failure."""
        with patch('subprocess.check_output', side_effect=CalledProcessError(1, 'nmcli')):
            with pytest.raises(InterfaceDetectionError):
                AccessPoint()


class TestProfileCreation:
    """Test AP profile creation."""
    
    def test_create_ap_profile_creates_connection(self):
        """Creates nmcli AP connection profile."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]), \
             patch('subprocess.check_output') as mock_check:
            
            ap = AccessPoint()
            ap.create_ap_profile()
            
            # Should call nmcli con add
            assert any('add' in str(call) for call in mock_check.call_args_list)
    
    def test_create_ap_profile_sets_wpa2_security(self):
        """Configures WPA2-PSK security."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]), \
             patch('subprocess.check_output') as mock_check:
            
            ap = AccessPoint()
            ap.create_ap_profile()
            
            # Should call nmcli con modify for security
            assert any('wpa-psk' in str(call) for call in mock_check.call_args_list)
    
    def test_create_ap_profile_configures_ip_range(self):
        """Configures IP address range."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]), \
             patch('subprocess.check_output') as mock_check:
            
            ap = AccessPoint()
            ap.create_ap_profile()
            
            # Should set IP to 192.168.50.1/24
            assert any('192.168.50.1/24' in str(call) for call in mock_check.call_args_list)
    
    def test_create_ap_profile_raises_on_failure(self):
        """Raises ProfileCreationError on nmcli failure."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output, CalledProcessError(1, 'nmcli')]):
            ap = AccessPoint()
            
            with pytest.raises(ProfileCreationError):
                ap.create_ap_profile()


class TestAPActivation:
    """Test AP activation and deactivation."""
    
    def test_activate_ap_brings_connection_up(self):
        """Activates AP connection."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]), \
             patch('subprocess.check_output') as mock_check:
            
            ap = AccessPoint()
            ap.activate_ap()
            
            # Should call nmcli con up
            assert any('up' in str(call) for call in mock_check.call_args_list)
    
    def test_activate_ap_sets_ap_active_true(self):
        """Sets ap_active flag to True."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]), \
             patch('subprocess.check_output'):
            
            ap = AccessPoint()
            result = ap.activate_ap()
            
            assert result is True
            assert ap.ap_active is True
    
    def test_activate_ap_raises_on_failure(self):
        """Raises APActivationError on nmcli failure."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output, CalledProcessError(1, 'nmcli')]):
            ap = AccessPoint()
            
            with pytest.raises(APActivationError):
                ap.activate_ap()
    
    def test_deactivate_ap_brings_connection_down(self):
        """Deactivates AP connection."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]), \
             patch('subprocess.check_output') as mock_check:
            
            ap = AccessPoint()
            ap.deactivate_ap()
            
            # Should call nmcli con down
            assert any('down' in str(call) for call in mock_check.call_args_list)
    
    def test_deactivate_ap_sets_ap_active_false(self):
        """Sets ap_active flag to False."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]), \
             patch('subprocess.check_output'):
            
            ap = AccessPoint()
            ap.ap_active = True
            ap.deactivate_ap()
            
            assert ap.ap_active is False
    
    def test_deactivate_ap_handles_failure_gracefully(self):
        """Logs error but doesn't raise on deactivation failure."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output, CalledProcessError(1, 'nmcli')]):
            ap = AccessPoint()
            
            # Should not raise
            ap.deactivate_ap()


class TestFallbackOpenAP:
    """Test fallback to open AP."""
    
    def test_fallback_removes_security(self):
        """Removes security configuration."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]), \
             patch('subprocess.check_output') as mock_check:
            
            ap = AccessPoint()
            ap.fallback_to_open_ap()
            
            # Should modify security to empty
            assert any('key-mgmt' in str(call) and '""' in str(call) for call in mock_check.call_args_list)
    
    def test_fallback_returns_ap_active_status(self):
        """Returns current ap_active status."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]), \
             patch('subprocess.check_output'):
            
            ap = AccessPoint()
            ap.ap_active = True
            result = ap.fallback_to_open_ap()
            
            assert result is True


class TestModuleFunctions:
    """Test module-level convenience functions."""
    
    def test_activate_ap_function_creates_and_activates(self):
        """activate_ap() creates AccessPoint and activates."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output, b'', b'', b'', b'']):
            result = activate_ap()
            
            assert result is True
    
    def test_activate_ap_function_falls_back_on_profile_error(self):
        """Falls back to open AP if profile creation fails."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output, CalledProcessError(1, 'nmcli'), b'']):
            result = activate_ap()
            
            # Should return ap_active status even after fallback
            assert isinstance(result, bool)
    
    def test_deactivate_ap_function_deactivates(self):
        """deactivate_ap() creates AccessPoint and deactivates."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output, b'']):
            deactivate_ap()  # Should not raise
    
    def test_get_ap_ssid_function_returns_ssid(self):
        """get_ap_ssid() returns generated SSID."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]):
            ssid = get_ap_ssid()
            
            assert ssid.startswith("PiConfig-")
    
    def test_is_active_function_returns_status(self):
        """is_active() returns AP activation status."""
        device_output = b"DEVICE  TYPE=wifi  STATE\nwlan0   TYPE=wifi  connected\n"
        show_output = b"GENERAL.HWADDR: AA:BB:CC:DD:EE:FF\n"
        
        with patch('subprocess.check_output', side_effect=[device_output, show_output]):
            status = is_active()
            
            assert isinstance(status, bool)
