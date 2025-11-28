"""
WebServer Module - HTTP Configuration Interface

Provides HTTP server on port 8080 for WiFi configuration during AP mode.
Serves embedded HTML interface and REST API endpoints.

Design: workspace/design/design-0005-webserver.md
Requirements: FR-050, FR-051, FR-052, FR-053, FR-054, FR-055
              NFR-007 (thread safety), NFR-008 (error logging)
Traceability: workspace/trace/trace-0001-requirements-traceability-matrix.md

Copyright (c) 2025 William Watson. Licensed under MIT License.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import logging
import threading
import traceback
from typing import Optional

# Configure module logger
logger = logging.getLogger('WebServer')


class WebServerError(Exception):
    """Base exception for web server errors"""
    pass


class PortInUseError(WebServerError):
    """Port 8080 unavailable"""
    pass


class ConfigurationError(WebServerError):
    """Invalid configuration"""
    pass


class ConfigHTTPHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests with embedded resources"""

    def log_message(self, format: str, *args) -> None:
        """Override to use custom logger"""
        logger.debug(f"{self.address_string()} - {format % args}")

    def do_GET(self) -> None:
        """Route GET requests"""
        try:
            if self.path == '/':
                self.serve_html_page()
            elif self.path == '/api/scan':
                self.handle_scan_request()
            elif self.path == '/api/status':
                self.handle_status_request()
            else:
                self.send_error_response(404, "Not Found")
        except Exception as e:
            logger.error(f"GET request error: {e}\n{traceback.format_exc()}")
            self.send_error_response(500, "Internal Server Error")

    def do_POST(self) -> None:
        """Route POST requests"""
        try:
            if self.path == '/api/configure':
                self.handle_configure_request()
            else:
                self.send_error_response(404, "Not Found")
        except Exception as e:
            logger.error(f"POST request error: {e}\n{traceback.format_exc()}")
            self.send_error_response(500, "Internal Server Error")

    def serve_html_page(self) -> None:
        """Send embedded HTML page with CSS and JavaScript"""
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WiFi Configuration</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: Arial, sans-serif; 
            background: #1a1a1a; 
            color: #fff; 
            padding: 20px;
            max-width: 600px;
            margin: 0 auto;
        }
        h1 { 
            text-align: center; 
            color: #007acc; 
            margin-bottom: 30px;
            font-size: 28px;
        }
        button, input, select { 
            min-height: 48px; 
            font-size: 18px; 
            margin: 10px 0; 
            width: 100%;
            border-radius: 4px;
        }
        button { 
            background: #007acc; 
            color: #fff; 
            border: none; 
            cursor: pointer;
            font-weight: bold;
            transition: background 0.2s;
        }
        button:hover { background: #005a9e; }
        button:active { background: #004578; }
        button:disabled {
            background: #444;
            cursor: not-allowed;
        }
        input, select { 
            padding: 12px; 
            border: 2px solid #444; 
            background: #2a2a2a; 
            color: #fff;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #007acc;
        }
        select {
            min-height: 150px;
        }
        select option {
            padding: 8px;
        }
        #statusDiv { 
            padding: 15px; 
            margin: 20px 0; 
            background: #2a2a2a; 
            border-left: 4px solid #007acc;
            border-radius: 4px;
            font-size: 16px;
        }
        #statusDiv.error { border-left-color: #cc0000; }
        #statusDiv.success { border-left-color: #00cc00; }
        .section {
            margin: 20px 0;
        }
        .label {
            display: block;
            margin-bottom: 5px;
            color: #aaa;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <h1>WiFi Configuration</h1>
    
    <div class="section">
        <button id="scanBtn">Scan Networks</button>
    </div>
    
    <div class="section">
        <label class="label">Available Networks:</label>
        <select id="networkList" size="5"></select>
    </div>
    
    <div class="section">
        <label class="label">Network Name (SSID):</label>
        <input id="ssidInput" type="text" placeholder="Enter network name" />
    </div>
    
    <div class="section">
        <label class="label">Password:</label>
        <input id="passwordInput" type="password" placeholder="Enter password" />
    </div>
    
    <div class="section">
        <button id="connectBtn">Connect</button>
    </div>
    
    <div id="statusDiv">Ready to configure WiFi</div>
    
    <script>
        const scanBtn = document.getElementById('scanBtn');
        const networkList = document.getElementById('networkList');
        const ssidInput = document.getElementById('ssidInput');
        const passwordInput = document.getElementById('passwordInput');
        const connectBtn = document.getElementById('connectBtn');
        const statusDiv = document.getElementById('statusDiv');
        
        function showStatus(msg, type = 'info') {
            statusDiv.textContent = msg;
            statusDiv.className = type;
        }
        
        function setLoading(isLoading) {
            scanBtn.disabled = isLoading;
            connectBtn.disabled = isLoading;
        }
        
        scanBtn.onclick = async () => {
            showStatus('Scanning for networks...', 'info');
            setLoading(true);
            try {
                const resp = await fetch('/api/scan');
                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                const data = await resp.json();
                networkList.innerHTML = '';
                if (data.networks && data.networks.length > 0) {
                    data.networks.forEach(net => {
                        const opt = document.createElement('option');
                        opt.value = net.ssid;
                        opt.textContent = `${net.ssid} (${net.signal}% ${net.security})`;
                        networkList.appendChild(opt);
                    });
                    showStatus(`Found ${data.networks.length} network(s)`, 'success');
                } else {
                    showStatus('No networks found', 'error');
                }
            } catch (e) {
                showStatus('Scan failed: ' + e.message, 'error');
            } finally {
                setLoading(false);
            }
        };
        
        networkList.onchange = () => {
            if (networkList.value) {
                ssidInput.value = networkList.value;
            }
        };
        
        connectBtn.onclick = async () => {
            const ssid = ssidInput.value.trim();
            const password = passwordInput.value;
            
            if (!ssid) {
                showStatus('Please enter a network name', 'error');
                return;
            }
            if (!password) {
                showStatus('Please enter a password', 'error');
                return;
            }
            
            showStatus('Configuring network...', 'info');
            setLoading(true);
            
            try {
                const resp = await fetch('/api/configure', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ssid, password})
                });
                
                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                const data = await resp.json();
                
                if (data.success) {
                    showStatus(data.message || 'Configuration successful. Attempting connection...', 'success');
                    passwordInput.value = '';
                } else {
                    showStatus(data.message || 'Configuration failed', 'error');
                }
            } catch (e) {
                showStatus('Configuration failed: ' + e.message, 'error');
            } finally {
                setLoading(false);
            }
        };
        
        // Initial status check
        (async () => {
            try {
                const resp = await fetch('/api/status');
                if (resp.ok) {
                    const data = await resp.json();
                    if (data.ap_active) {
                        showStatus('Access Point mode - configure WiFi to connect', 'info');
                    }
                }
            } catch (e) {
                // Ignore initial status check failures
            }
        })();
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
        logger.debug("Served HTML configuration page")

    def handle_scan_request(self) -> None:
        """Call ConnectionManager.scan_networks(), return JSON with CORS"""
        try:
            # Import here to avoid circular dependencies
            from connection_manager import ConnectionManager
            
            logger.info("Network scan requested")
            networks = ConnectionManager.scan_networks()
            self.send_json_response({"networks": networks})
            logger.info(f"Scan completed: {len(networks)} networks found")
        except Exception as e:
            logger.error(f"Scan failed: {e}\n{traceback.format_exc()}")
            self.send_error_response(500, "Network scan failed")

    def handle_status_request(self) -> None:
        """Query StateMonitor/APManager, return JSON with CORS"""
        try:
            # Import here to avoid circular dependencies
            from state_monitor import StateMonitor
            from connection_manager import ConnectionManager
            from ap_manager import APManager
            
            logger.debug("Status query requested")
            state = StateMonitor.get_current_state()
            ssid = ConnectionManager.get_current_ssid()
            ap_active = APManager.is_active()
            
            response = {
                "state": state,
                "ssid": ssid,
                "ap_active": ap_active
            }
            self.send_json_response(response)
            logger.debug(f"Status returned: {response}")
        except Exception as e:
            logger.error(f"Status query failed: {e}\n{traceback.format_exc()}")
            self.send_error_response(500, "Status query failed")

    def handle_configure_request(self) -> None:
        """Parse JSON body, validate, call ConnectionManager.configure_network()"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_response(400, "Empty request body")
                return
            
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            ssid = data.get('ssid', '').strip()
            password = data.get('password', '')
            
            if not ssid:
                logger.warning("Configuration attempt with empty SSID")
                self.send_json_response({
                    "success": False,
                    "message": "SSID is required"
                }, 400)
                return
            
            if not password:
                logger.warning("Configuration attempt with empty password")
                self.send_json_response({
                    "success": False,
                    "message": "Password is required"
                }, 400)
                return
            
            # Import here to avoid circular dependencies
            from connection_manager import ConnectionManager
            
            logger.info(f"Configuration requested for SSID: {ssid}")
            ConnectionManager.configure_network(ssid, password)
            
            self.send_json_response({
                "success": True,
                "message": f"Configured network '{ssid}'. Connection will be attempted."
            })
            logger.info(f"Successfully configured network: {ssid}")
            
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in configuration request: {e}")
            self.send_error_response(400, "Invalid JSON format")
        except KeyError as e:
            logger.warning(f"Missing required field: {e}")
            self.send_error_response(400, f"Missing required field: {e}")
        except Exception as e:
            logger.error(f"Configuration failed: {e}\n{traceback.format_exc()}")
            self.send_json_response({
                "success": False,
                "message": f"Configuration failed: {str(e)}"
            }, 500)

    def send_json_response(self, data: dict, status_code: int = 200) -> None:
        """Send JSON with CORS headers"""
        try:
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to send JSON response: {e}\n{traceback.format_exc()}")

    def send_error_response(self, status_code: int, message: str) -> None:
        """Send JSON error response"""
        self.send_json_response({"error": message}, status_code)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads"""
    daemon_threads = True
    allow_reuse_address = True


class WebServerManager:
    """Manage HTTP server lifecycle"""

    def __init__(self, port: int = 8080):
        """Initialize server on specified port"""
        self.port = port
        self.server: Optional[ThreadedHTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start_server(self) -> None:
        """Start server in daemon thread"""
        with self._lock:
            if self.is_running():
                logger.warning("Server already running")
                raise PortInUseError("Server is already running")
            
            try:
                self.server = ThreadedHTTPServer(('0.0.0.0', self.port), ConfigHTTPHandler)
                self.server_thread = threading.Thread(target=self.server.serve_forever)
                self.server_thread.daemon = True
                self.server_thread.start()
                logger.info(f"Web server started on 0.0.0.0:{self.port}")
            except OSError as e:
                logger.critical(f"Failed to start server on port {self.port}: {e}\n{traceback.format_exc()}")
                raise PortInUseError(f"Port {self.port} is unavailable: {e}")
            except Exception as e:
                logger.critical(f"Unexpected error starting server: {e}\n{traceback.format_exc()}")
                raise WebServerError(f"Failed to start server: {e}")

    def stop_server(self) -> None:
        """Shutdown server gracefully"""
        with self._lock:
            if not self.is_running():
                logger.warning("Server not running")
                return
            
            try:
                if self.server:
                    logger.info("Shutting down web server")
                    self.server.shutdown()
                    self.server.server_close()
                    self.server = None
                
                if self.server_thread:
                    self.server_thread.join(timeout=5.0)
                    self.server_thread = None
                
                logger.info("Web server stopped")
            except Exception as e:
                logger.error(f"Error stopping server: {e}\n{traceback.format_exc()}")

    def is_running(self) -> bool:
        """Return server status"""
        return (self.server is not None and 
                self.server_thread is not None and 
                self.server_thread.is_alive())


# Module-level singleton and functions
_server_manager: Optional[WebServerManager] = None
_manager_lock = threading.Lock()


def start_server(port: int = 8080) -> None:
    """
    Public entry point to start server
    
    Args:
        port: Port number (default 8080)
    
    Raises:
        PortInUseError: If port is unavailable or server already running
        WebServerError: If server fails to start
    """
    global _server_manager
    
    with _manager_lock:
        if _server_manager is None:
            _server_manager = WebServerManager(port)
        
        try:
            _server_manager.start_server()
        except PortInUseError:
            raise
        except Exception as e:
            logger.critical(f"Failed to start web server: {e}")
            raise WebServerError(f"Server start failed: {e}")


def stop_server() -> None:
    """
    Public entry point to stop server
    """
    global _server_manager
    
    with _manager_lock:
        if _server_manager is not None:
            _server_manager.stop_server()
        else:
            logger.warning("No server manager instance to stop")


def is_running() -> bool:
    """
    Public entry point to check server status
    
    Returns:
        bool: True if server is running, False otherwise
    """
    global _server_manager
    
    with _manager_lock:
        return _server_manager is not None and _server_manager.is_running()
