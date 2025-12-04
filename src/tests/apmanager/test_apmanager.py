"""Unit tests for apmanager module.

Tests access point creation, activation, and management.
"""

import pytest
from unittest.mock import Mock, patch, call
from subprocess import CalledProcessError

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from pi_netconfig.apmanager import (
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


@pytest.fixture
def mock_nmcli():
    """Mock nmcli calls before any AccessPoint instantiation."""
    with patch('pi_netconfig.apmanager.check_output') as mock:
        device_output = b"DEVICE  TYPE      STATE\nwlan0   wifi      connected\n"
        mac_output = b"GENERAL.HWADDR:        AA:BB:CC:DD:EE:FF\n"
        mock.side_effect = [device_output, mac_output]
        yield mock


@pytest.fixture
def mock_nmcli_no_wifi():
    """Mock nmcli calls with no WiFi interface."""
    with patch('pi_netconfig.apmanager.check_output') as mock:
        device_output = b"DEVICE  TYPE      STATE\neth0    ethernet  connected\n"
        mock.return_value = device_output
        yield mock


@pytest.fixture
def mock_nmcli_extended():
    """Mock nmcli calls for tests requiring additional subprocess calls."""
    with patch('pi_netconfig.apmanager.check_output') as mock:
        device_output = b"DEVICE  TYPE      STATE\nwlan0   wifi      connected\n"
        mac_output = b"GENERAL.HWADDR:        AA:BB:CC:DD:EE:FF\n"
        # Default to success for additional calls
        mock.side_effect = [device_output, mac_output, b'', b'', b'', b'', b'']
        yield mock


@pytest.fixture
def mock_nmcli_profile_creation_fail():
    """Mock nmcli calls with profile creation failure."""
    with patch('pi_netconfig.apmanager.check_output') as mock:
        device_output = b"DEVICE  TYPE      STATE\nwlan0   wifi      connected\n"
        mac_output = b"GENERAL.HWADDR:        AA:BB:CC:DD:EE:FF\n"
        mock.side_effect = [device_output, mac_output, CalledProcessError(1, 'nmcli')]
        yield mock


@pytest.fixture
def mock_nmcli_activation_fail():
    """Mock nmcli calls with activation failure."""
    with patch('pi_netconfig.apmanager.check_output') as mock:
        device_output = b"DEVICE  TYPE      STATE\nwlan0   wifi      connected\n"
        mac_output = b"GENERAL.HWADDR:        AA:BB:CC:DD:EE:FF\n"
        mock.side_effect = [device_output, mac_output, CalledProcessError(1, 'nmcli')]
        yield mock


class TestAccessPointInitialization:
    """Test AccessPoint initialization."""
    
    def test_access_point_initializes_with_interface(self, mock_nmcli):
        """Initializes and detects WiFi interface."""
        ap = AccessPoint()
        assert ap.interface == "wlan0"
    
    def test_access_point_raises_when_no_wifi_interface(self, mock_nmcli_no_wifi):
        """Raises InterfaceDetectionError when no WiFi interface found."""
        with pytest.raises(InterfaceDetectionError):
            AccessPoint()
    
    def test_access_point_gets_mac_address(self, mock_nmcli):
        """Retrieves MAC address from nmcli."""
        ap = AccessPoint()
        assert ap.mac_address == "AA:BB:CC:DD:EE:FF"
    
    def test_access_point_generates_ssid_from_mac(self, mock_nmcli):
        """Generates SSID using last 4 MAC chars."""
        ap = AccessPoint()
        assert ap.ssid == "PiConfig-E:FF"
    
    def test_access_point_initializes_ap_active_false(self, mock_nmcli):
        """Initializes with ap_active set to False."""
        ap = AccessPoint()
        assert ap.ap_active is False


class TestInterfaceDetection:
    """Test WiFi interface detection."""
    
    def test_get_wifi_interface_parses_nmcli_output(self, mock_nmcli):
        """Parses nmcli device status output correctly."""
        ap = AccessPoint()
        assert ap.interface == "wlan0"
    
    def test_get_wifi_interface_raises_on_nmcli_failure(self):
        """Raises InterfaceDetectionError on nmcli failure."""
        with patch('pi_netconfig.apmanager.check_output') as mock_check:
            mock_check.side_effect = CalledProcessError(1, 'nmcli')
            with pytest.raises(InterfaceDetectionError):
                AccessPoint()


class TestProfileCreation:
    """Test AP profile creation."""
    
    def test_create_ap_profile_creates_connection(self, mock_nmcli_extended):
        """Creates nmcli AP connection profile."""
        ap = AccessPoint()
        ap.create_ap_profile()
        
        # Verify nmcli con add was called (3rd call after init)
        assert mock_nmcli_extended.call_count >= 3
        add_call = mock_nmcli_extended.call_args_list[2]
        assert b'add' in add_call[0][0] or 'add' in str(add_call)
    
    def test_create_ap_profile_sets_wpa2_security(self, mock_nmcli_extended):
        """Configures WPA2-PSK security."""
        ap = AccessPoint()
        ap.create_ap_profile()
        
        # Check for wpa-psk in modify calls
        calls_str = str(mock_nmcli_extended.call_args_list)
        assert 'wpa-psk' in calls_str
    
    def test_create_ap_profile_configures_ip_range(self, mock_nmcli_extended):
        """Configures IP address range."""
        ap = AccessPoint()
        ap.create_ap_profile()
        
        # Check for IP configuration
        calls_str = str(mock_nmcli_extended.call_args_list)
        assert '192.168.50.1/24' in calls_str
    
    def test_create_ap_profile_raises_on_failure(self, mock_nmcli_profile_creation_fail):
        """Raises ProfileCreationError on nmcli failure."""
        ap = AccessPoint()
        
        with pytest.raises(ProfileCreationError):
            ap.create_ap_profile()


class TestAPActivation:
    """Test AP activation and deactivation."""
    
    def test_activate_ap_brings_connection_up(self, mock_nmcli_extended):
        """Activates AP connection."""
        ap = AccessPoint()
        ap.activate_ap()
        
        # Verify nmcli con up was called
        calls_str = str(mock_nmcli_extended.call_args_list)
        assert 'up' in calls_str
    
    def test_activate_ap_sets_ap_active_true(self, mock_nmcli_extended):
        """Sets ap_active flag to True."""
        ap = AccessPoint()
        result = ap.activate_ap()
        
        assert result is True
        assert ap.ap_active is True
    
    def test_activate_ap_raises_on_failure(self, mock_nmcli_activation_fail):
        """Raises APActivationError on nmcli failure."""
        ap = AccessPoint()
        
        with pytest.raises(APActivationError):
            ap.activate_ap()
    
    def test_deactivate_ap_brings_connection_down(self, mock_nmcli_extended):
        """Deactivates AP connection."""
        ap = AccessPoint()
        ap.deactivate_ap()
        
        # Verify nmcli con down was called
        calls_str = str(mock_nmcli_extended.call_args_list)
        assert 'down' in calls_str
    
    def test_deactivate_ap_sets_ap_active_false(self, mock_nmcli_extended):
        """Sets ap_active flag to False."""
        ap = AccessPoint()
        ap.ap_active = True
        ap.deactivate_ap()
        
        assert ap.ap_active is False
    
    def test_deactivate_ap_handles_failure_gracefully(self):
        """Logs error but doesn't raise on deactivation failure."""
        device_output = b"DEVICE  TYPE  STATE\nwlan0   wifi  connected\n"
        mac_output = b"GENERAL.HWADDR:        AA:BB:CC:DD:EE:FF\n"
        
        with patch('pi_netconfig.apmanager.check_output') as mock_check:
            mock_check.side_effect = [device_output, mac_output, CalledProcessError(1, 'nmcli')]
            ap = AccessPoint()
            
            # Should not raise
            ap.deactivate_ap()


class TestFallbackOpenAP:
    """Test fallback to open AP."""
    
    def test_fallback_removes_security(self, mock_nmcli_extended):
        """Removes security configuration."""
        ap = AccessPoint()
        ap.fallback_to_open_ap()
        
        # Check for key-mgmt modification
        calls_str = str(mock_nmcli_extended.call_args_list)
        assert 'key-mgmt' in calls_str
    
    def test_fallback_returns_ap_active_status(self, mock_nmcli_extended):
        """Returns current ap_active status."""
        ap = AccessPoint()
        ap.ap_active = True
        result = ap.fallback_to_open_ap()
        
        assert result is True


class TestModuleFunctions:
    """Test module-level convenience functions."""
    
    def test_activate_ap_function_creates_and_activates(self, mock_nmcli_extended):
        """activate_ap() creates AccessPoint and activates."""
        result = activate_ap()
        assert result is True
    
    def test_activate_ap_function_falls_back_on_profile_error(self):
        """Falls back to open AP if profile creation fails."""
        device_output = b"DEVICE  TYPE  STATE\nwlan0   wifi  connected\n"
        mac_output = b"GENERAL.HWADDR:        AA:BB:CC:DD:EE:FF\n"
        
        with patch('pi_netconfig.apmanager.check_output') as mock_check:
            mock_check.side_effect = [device_output, mac_output, CalledProcessError(1, 'nmcli'), b'', b'', b'']
            result = activate_ap()
            
            # Should return ap_active status even after fallback
            assert isinstance(result, bool)
    
    def test_deactivate_ap_function_deactivates(self, mock_nmcli_extended):
        """deactivate_ap() creates AccessPoint and deactivates."""
        deactivate_ap()  # Should not raise
    
    def test_get_ap_ssid_function_returns_ssid(self, mock_nmcli):
        """get_ap_ssid() returns generated SSID."""
        ssid = get_ap_ssid()
        assert ssid.startswith("PiConfig-")
    
    def test_is_active_function_returns_status(self, mock_nmcli):
        """is_active() returns AP activation status."""
        status = is_active()
        assert isinstance(status, bool)
