"""Unit tests for webserver module.

Tests HTTP server, request handlers, and API endpoints.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import threading
from http.server import BaseHTTPRequestHandler

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from webserver import (
    ConfigHTTPHandler,
    ThreadedHTTPServer,
    WebServerManager,
    start_server,
    stop_server,
    is_running,
    WebServerError,
    PortInUseError,
    ConfigurationError
)


class TestConfigHTTPHandler:
    """Test HTTP request handler."""
    
    def test_do_get_serves_html_for_root(self):
        """GET / returns HTML configuration page."""
        handler = ConfigHTTPHandler(Mock(), ('127.0.0.1', 8080), Mock())
        handler.path = '/'
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()
        
        handler.do_GET()
        
        handler.send_response.assert_called_with(200)
        assert handler.wfile.write.called
    
    def test_do_get_handles_scan_request(self):
        """GET /api/scan triggers network scan."""
        handler = ConfigHTTPHandler(Mock(), ('127.0.0.1', 8080), Mock())
        handler.path = '/api/scan'
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()
        
        with patch('webserver.ConnectionManager') as mock_cm:
            mock_cm.scan_networks = Mock(return_value=[])
            handler.do_GET()
            
            mock_cm.scan_networks.assert_called_once()
    
    def test_do_get_handles_status_request(self):
        """GET /api/status returns system status."""
        handler = ConfigHTTPHandler(Mock(), ('127.0.0.1', 8080), Mock())
        handler.path = '/api/status'
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()
        
        with patch('webserver.StateMonitor') as mock_sm, \
             patch('webserver.ConnectionManager') as mock_cm, \
             patch('webserver.APManager') as mock_ap:
            
            mock_sm.get_current_state = Mock(return_value='CLIENT')
            mock_cm.get_current_ssid = Mock(return_value='TestSSID')
            mock_ap.is_active = Mock(return_value=False)
            
            handler.do_GET()
            
            assert handler.wfile.write.called
    
    def test_do_get_returns_404_for_unknown_path(self):
        """GET /unknown returns 404."""
        handler = ConfigHTTPHandler(Mock(), ('127.0.0.1', 8080), Mock())
        handler.path = '/unknown'
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()
        
        handler.do_GET()
        
        # Should send error response
        assert handler.send_response.called or handler.send_header.called
    
    def test_do_post_handles_configure_request(self):
        """POST /api/configure processes network configuration."""
        handler = ConfigHTTPHandler(Mock(), ('127.0.0.1', 8080), Mock())
        handler.path = '/api/configure'
        handler.headers = {'Content-Length': '50'}
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()
        
        config_data = json.dumps({'ssid': 'TestSSID', 'password': 'password123'})
        handler.rfile = Mock()
        handler.rfile.read = Mock(return_value=config_data.encode('utf-8'))
        
        with patch('webserver.ConnectionManager') as mock_cm:
            mock_cm.configure_network = Mock()
            handler.do_POST()
            
            mock_cm.configure_network.assert_called_once_with('TestSSID', 'password123')
    
    def test_do_post_validates_ssid_required(self):
        """POST /api/configure rejects empty SSID."""
        handler = ConfigHTTPHandler(Mock(), ('127.0.0.1', 8080), Mock())
        handler.path = '/api/configure'
        handler.headers = {'Content-Length': '30'}
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()
        
        config_data = json.dumps({'ssid': '', 'password': 'password123'})
        handler.rfile = Mock()
        handler.rfile.read = Mock(return_value=config_data.encode('utf-8'))
        
        handler.do_POST()
        
        # Should send error response
        written_data = handler.wfile.write.call_args[0][0].decode('utf-8')
        response = json.loads(written_data)
        assert response['success'] is False
    
    def test_do_post_validates_password_required(self):
        """POST /api/configure rejects empty password."""
        handler = ConfigHTTPHandler(Mock(), ('127.0.0.1', 8080), Mock())
        handler.path = '/api/configure'
        handler.headers = {'Content-Length': '30'}
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()
        
        config_data = json.dumps({'ssid': 'TestSSID', 'password': ''})
        handler.rfile = Mock()
        handler.rfile.read = Mock(return_value=config_data.encode('utf-8'))
        
        handler.do_POST()
        
        # Should send error response
        written_data = handler.wfile.write.call_args[0][0].decode('utf-8')
        response = json.loads(written_data)
        assert response['success'] is False
    
    def test_do_post_returns_404_for_unknown_path(self):
        """POST /unknown returns 404."""
        handler = ConfigHTTPHandler(Mock(), ('127.0.0.1', 8080), Mock())
        handler.path = '/unknown'
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()
        
        handler.do_POST()
        
        # Should send error response
        assert handler.send_response.called or handler.send_header.called
    
    def test_send_json_response_includes_cors_headers(self):
        """JSON responses include CORS headers."""
        handler = ConfigHTTPHandler(Mock(), ('127.0.0.1', 8080), Mock())
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()
        
        handler.send_json_response({'test': 'data'})
        
        # Check CORS headers were set
        header_calls = [call[0] for call in handler.send_header.call_args_list]
        assert any('Access-Control-Allow-Origin' in str(call) for call in header_calls)


class TestWebServerManager:
    """Test WebServerManager lifecycle."""
    
    def test_manager_initializes_with_port(self):
        """Initializes with specified port."""
        manager = WebServerManager(port=8080)
        assert manager.port == 8080
    
    def test_manager_initializes_without_server(self):
        """Initializes with no active server."""
        manager = WebServerManager()
        assert manager.server is None
        assert manager.server_thread is None
    
    def test_start_server_creates_http_server(self):
        """start_server() creates ThreadedHTTPServer."""
        manager = WebServerManager(port=8080)
        
        with patch('webserver.ThreadedHTTPServer') as mock_server:
            mock_instance = Mock()
            mock_server.return_value = mock_instance
            
            manager.start_server()
            
            mock_server.assert_called_once()
    
    def test_start_server_starts_daemon_thread(self):
        """start_server() starts server in daemon thread."""
        manager = WebServerManager(port=8080)
        
        with patch('webserver.ThreadedHTTPServer'), \
             patch('threading.Thread') as mock_thread:
            
            mock_instance = Mock()
            mock_thread.return_value = mock_instance
            
            manager.start_server()
            
            assert mock_instance.daemon is True
            mock_instance.start.assert_called_once()
    
    def test_start_server_raises_if_already_running(self):
        """start_server() raises PortInUseError if server active."""
        manager = WebServerManager(port=8080)
        manager.server = Mock()
        manager.server_thread = Mock()
        manager.server_thread.is_alive = Mock(return_value=True)
        
        with pytest.raises(PortInUseError):
            manager.start_server()
    
    def test_start_server_raises_on_port_unavailable(self):
        """start_server() raises PortInUseError if port taken."""
        manager = WebServerManager(port=8080)
        
        with patch('webserver.ThreadedHTTPServer', side_effect=OSError("Address in use")):
            with pytest.raises(PortInUseError):
                manager.start_server()
    
    def test_stop_server_shuts_down_gracefully(self):
        """stop_server() shuts down and closes server."""
        manager = WebServerManager(port=8080)
        manager.server = Mock()
        manager.server_thread = Mock()
        
        manager.stop_server()
        
        manager.server.shutdown.assert_called_once()
        manager.server.server_close.assert_called_once()
    
    def test_stop_server_joins_thread(self):
        """stop_server() waits for thread to complete."""
        manager = WebServerManager(port=8080)
        manager.server = Mock()
        manager.server_thread = Mock()
        
        manager.stop_server()
        
        manager.server_thread.join.assert_called_once()
    
    def test_stop_server_handles_no_server(self):
        """stop_server() handles case where server not running."""
        manager = WebServerManager(port=8080)
        
        # Should not raise
        manager.stop_server()
    
    def test_is_running_returns_true_when_active(self):
        """is_running() returns True when server active."""
        manager = WebServerManager(port=8080)
        manager.server = Mock()
        manager.server_thread = Mock()
        manager.server_thread.is_alive = Mock(return_value=True)
        
        assert manager.is_running() is True
    
    def test_is_running_returns_false_when_inactive(self):
        """is_running() returns False when server not active."""
        manager = WebServerManager(port=8080)
        
        assert manager.is_running() is False


class TestModuleFunctions:
    """Test module-level convenience functions."""
    
    def test_start_server_creates_manager_and_starts(self):
        """start_server() creates WebServerManager and starts."""
        with patch('webserver.WebServerManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            
            start_server(port=8080)
            
            mock_manager_class.assert_called_once_with(8080)
            mock_manager.start_server.assert_called_once()
    
    def test_start_server_uses_default_port(self):
        """start_server() defaults to port 8080."""
        with patch('webserver.WebServerManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            
            start_server()
            
            mock_manager_class.assert_called_once_with(8080)
    
    def test_start_server_raises_port_in_use_error(self):
        """start_server() propagates PortInUseError."""
        with patch('webserver.WebServerManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.start_server = Mock(side_effect=PortInUseError("Port taken"))
            mock_manager_class.return_value = mock_manager
            
            with pytest.raises(PortInUseError):
                start_server()
    
    def test_stop_server_stops_existing_manager(self):
        """stop_server() stops active WebServerManager."""
        mock_manager = Mock()
        
        with patch('webserver._server_manager', mock_manager):
            stop_server()
            
            mock_manager.stop_server.assert_called_once()
    
    def test_stop_server_handles_no_manager(self):
        """stop_server() handles case where no manager exists."""
        with patch('webserver._server_manager', None):
            # Should not raise
            stop_server()
    
    def test_is_running_returns_manager_status(self):
        """is_running() returns WebServerManager status."""
        mock_manager = Mock()
        mock_manager.is_running = Mock(return_value=True)
        
        with patch('webserver._server_manager', mock_manager):
            assert is_running() is True
    
    def test_is_running_returns_false_when_no_manager(self):
        """is_running() returns False when no manager."""
        with patch('webserver._server_manager', None):
            assert is_running() is False
    
    def test_module_functions_thread_safe(self):
        """Module functions use lock for thread safety."""
        with patch('webserver._manager_lock') as mock_lock, \
             patch('webserver._server_manager', None):
            
            stop_server()
            
            mock_lock.__enter__.assert_called()
