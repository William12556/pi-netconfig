Created: 2025 November 11

# T01 Design Template v1.0 - YAML Format
# Pi Network Configuration Tool - Master Design (MASTER)

project_info:
  name: "pi-netconfig"
  version: "0.2.0"
  date: "2025-11-10"
  author: "William Watson"

scope:
  purpose: "Autonomous WiFi management service for Raspberry Pi that auto-configures network connectivity via web interface when no router connection exists"
  in_scope:
    - "Self-installation as systemd service on first run"
    - "WiFi connection detection and management"
    - "Automatic AP mode activation for configuration"
    - "Web-based configuration interface (port 8080)"
    - "Systemd service integration"
    - "Network scanning and selection"
    - "Single network configuration persistence"
  out_scope:
    - "Ethernet configuration"
    - "VPN management"
    - "Network diagnostics beyond connectivity testing"
    - "Multi-language support (English only)"
    - "Mobile app interface"
    - "Multiple network profile management"
    - "Web interface authentication"
    - "Status LED/notification system"
  terminology:
    - term: "AP Mode"
      definition: "Access Point mode where device creates WiFi network for configuration"
    - term: "Client Mode"
      definition: "Standard mode where device connects to existing WiFi network"
    - term: "Network Manager"
      definition: "Linux system service managing network interfaces"

system_overview:
  description: "Self-installing service that monitors WiFi connectivity, switches between client/AP modes, and provides web interface for network configuration"
  context_flow: "First Run → Detect Service → [Not Installed] → Self-Install → Systemd Start → Boot → Connectivity Check → [No Connection] → AP Mode + Web Server → User Config → Client Mode"
  primary_functions:
    - "Self-install as systemd service on first execution"
    - "Monitor WiFi connection status"
    - "Create temporary access point for configuration"
    - "Scan and display available networks"
    - "Configure WiFi credentials"
    - "Persist configuration across reboots"

design_constraints:
  technical:
    - "Must work with NetworkManager (standard in Raspbian Bookworm)"
    - "Requires root privileges for network operations"
    - "Single WiFi interface constraint"
    - "No external dependencies beyond standard Debian packages"
  implementation:
    language: "Python"
    framework: "asyncio for concurrent operations"
    libraries:
      - "http.server (stdlib) - web interface"
      - "subprocess - NetworkManager CLI interaction"
      - "json - configuration persistence"
      - "socket - connectivity testing"
    standards:
      - "PEP 8 style compliance"
      - "Type hints for all functions"
      - "Systemd service unit specification"
  performance_targets:
    - metric: "Connection detection"
      value: "< 10 seconds after boot"
    - metric: "AP mode activation"
      value: "< 15 seconds after failed connection"
    - metric: "Web interface response"
      value: "< 500ms page load"

architecture:
  pattern: "Self-bootstrapping state machine with monitoring loop"
  component_relationships: "Installer → [First Run] → ServiceController → StateMonitor → ConnectionManager ↔ APManager + WebServer"
  technology_stack:
    language: "Python 3.11+"
    framework: "asyncio event loop"
    libraries:
      - "NetworkManager via nmcli"
      - "http.server"
      - "systemd integration"
    data_store: "JSON file (/etc/pi-netconfig/config.json)"
  directory_structure:
    - "/usr/local/bin/pi-netconfig/main.py - application code (installed location)"
    - "/etc/pi-netconfig/config.json - configuration files"
    - "/var/log/pi-netconfig.log - service logs"
    - "/etc/systemd/system/pi-netconfig.service - service unit (auto-generated)"

components:
  - name: "Installer"
    purpose: "Self-installation mechanism detecting and configuring systemd service on first run"
    responsibilities:
      - "Detect if systemd service already installed"
      - "Create required directories (/etc/pi-netconfig, logs)"
      - "Copy script to installation location (/usr/local/bin/pi-netconfig/)"
      - "Generate and install systemd unit file"
      - "Enable and start systemd service"
      - "Verify installation success"
    inputs:
      - field: "run_mode"
        type: "str"
        description: "bootstrap or service mode indicator"
    outputs:
      - field: "installation_status"
        type: "bool"
        description: "Installation success/failure"
    key_elements:
      - name: "InstallationDetector"
        type: "class"
        purpose: "Check for existing systemd service installation"
      - name: "SystemdInstaller"
        type: "class"
        purpose: "Perform installation steps and systemd configuration"
    dependencies:
      internal: []
      external:
        - "subprocess (systemctl, cp, mkdir)"
        - "shutil (file operations)"
        - "os (path operations)"
    processing_logic:
      - "Check for service file: /etc/systemd/system/pi-netconfig.service"
      - "If exists: exit installer, proceed to normal operation"
      - "If not exists and root privileges: begin installation"
      - "Create directories: /usr/local/bin/pi-netconfig/, /etc/pi-netconfig/, /var/log/"
      - "Copy self to /usr/local/bin/pi-netconfig/main.py"
      - "Generate systemd unit file with proper ExecStart path"
      - "Install unit: cp to /etc/systemd/system/"
      - "Enable: systemctl daemon-reload && systemctl enable pi-netconfig"
      - "Start: systemctl start pi-netconfig"
      - "Exit bootstrap mode (systemd will restart in service mode)"
    error_conditions:
      - condition: "Insufficient privileges (not root)"
        handling: "Exit with error message: 'Installation requires root privileges'"
      - condition: "Directory creation fails"
        handling: "Raise InstallerError with details, rollback partial installation"
      - condition: "Systemd commands fail"
        handling: "Log error details, attempt manual cleanup instructions"

  - name: "StateMonitor"
    purpose: "Main state machine managing service operational mode"
    responsibilities:
      - "Determine current operational state (CHECKING, CLIENT, AP_MODE)"
      - "Coordinate transitions between states"
      - "Initialize and shutdown components"
    inputs:
      - field: "connection_status"
        type: "bool"
        description: "Result from connectivity check"
    outputs:
      - field: "current_state"
        type: "Enum[CHECKING, CLIENT, AP_MODE]"
        description: "Current operational state"
    key_elements:
      - name: "StateMachine"
        type: "class"
        purpose: "Implement state transitions and mode coordination"
    dependencies:
      internal:
        - "ConnectionManager"
        - "APManager"
        - "WebServer"
      external:
        - "asyncio"
    processing_logic:
      - "Loop: check connection every 30 seconds"
      - "On boot or connection loss: transition to AP_MODE after 3 failed checks"
      - "In AP_MODE: monitor for successful configuration"
      - "After config: attempt connection, return to CLIENT or remain AP_MODE"
    error_conditions:
      - condition: "State transition failure"
        handling: "Log error, attempt recovery to last known good state"

  - name: "ConnectionManager"
    purpose: "Manage WiFi client mode connections and scanning"
    responsibilities:
      - "Test active connection to router/AP"
      - "Scan for available networks"
      - "Configure and activate WiFi connections"
      - "Persist connection configurations"
    inputs:
      - field: "ssid"
        type: "str"
        description: "Network SSID to connect"
      - field: "password"
        type: "str"
        description: "Network PSK"
    outputs:
      - field: "connection_active"
        type: "bool"
        description: "Connection status result"
      - field: "available_networks"
        type: "List[NetworkInfo]"
        description: "Scanned networks with signal strength"
    key_elements:
      - name: "ConnectionTester"
        type: "class"
        purpose: "Verify active internet connectivity"
      - name: "NetworkScanner"
        type: "class"
        purpose: "Scan and parse available WiFi networks"
      - name: "ConfigManager"
        type: "class"
        purpose: "Apply and persist NetworkManager configurations"
    dependencies:
      internal: []
      external:
        - "subprocess (nmcli)"
        - "socket (connectivity test)"
    processing_logic:
      - "Test connection: ping known hosts (8.8.8.8, 1.1.1.1)"
      - "Scan: nmcli dev wifi list"
      - "Configure: nmcli connection add/modify"
      - "Persist to JSON: active SSID and credentials"
    error_conditions:
      - condition: "nmcli command fails"
        handling: "Raise ConnectionManagerError with stderr output"
      - condition: "Invalid credentials"
        handling: "Return error status, maintain previous config"

  - name: "APManager"
    purpose: "Create and manage local access point for configuration"
    responsibilities:
      - "Activate WiFi interface in AP mode"
      - "Configure DHCP for connected clients"
      - "Provide predictable SSID and credentials"
      - "Deactivate AP when switching to client mode"
    inputs:
      - field: "enable"
        type: "bool"
        description: "Activate or deactivate AP mode"
    outputs:
      - field: "ap_active"
        type: "bool"
        description: "Current AP mode status"
      - field: "ap_ssid"
        type: "str"
        description: "Access point network name"
    key_elements:
      - name: "AccessPoint"
        type: "class"
        purpose: "Manage NetworkManager AP connection profile"
    dependencies:
      internal: []
      external:
        - "subprocess (nmcli)"
    processing_logic:
      - "Create AP profile: SSID='PiConfig-<MAC_LAST_4>', WPA2, password='piconfig123'"
      - "Activate: nmcli connection up <profile>"
      - "Deactivate: nmcli connection down <profile>"
      - "IP range: 192.168.50.1/24"
    error_conditions:
      - condition: "AP activation fails"
        handling: "Raise APManagerError, attempt fallback to open AP"
      - condition: "Interface unavailable"
        handling: "Log critical error, enter degraded mode"

  - name: "WebServer"
    purpose: "Provide HTTP interface for network configuration"
    responsibilities:
      - "Serve HTML configuration interface"
      - "Handle network scan requests"
      - "Process configuration submissions"
      - "Provide API endpoints for status queries"
    inputs:
      - field: "http_request"
        type: "HTTPRequest"
        description: "Incoming web requests"
    outputs:
      - field: "http_response"
        type: "HTTPResponse"
        description: "HTML pages or JSON API responses"
    key_elements:
      - name: "ConfigHTTPHandler"
        type: "class"
        purpose: "Custom HTTP request handler"
      - name: "APIEndpoints"
        type: "class"
        purpose: "REST-like API for AJAX calls"
    dependencies:
      internal:
        - "ConnectionManager"
        - "StateMonitor"
      external:
        - "http.server"
        - "json"
    processing_logic:
      - "Serve static HTML/CSS/JS from embedded strings"
      - "GET /: main configuration page"
      - "GET /api/scan: trigger network scan, return JSON"
      - "POST /api/configure: accept SSID/password, apply config"
      - "GET /api/status: return current state and connection info"
    error_conditions:
      - condition: "Port 8080 unavailable"
        handling: "Raise WebServerError, log and exit service"
      - condition: "Invalid configuration POST"
        handling: "Return 400 with error details in JSON"

  - name: "ServiceController"
    purpose: "Application entry point managing bootstrap vs service mode and systemd lifecycle"
    responsibilities:
      - "Determine execution mode (bootstrap vs service)"
      - "Delegate to Installer if not installed"
      - "Initialize logging"
      - "Start/stop state monitor loop"
      - "Handle service signals (SIGTERM, SIGINT)"
      - "Cleanup on shutdown"
    inputs:
      - field: "system_signal"
        type: "signal"
        description: "OS signals for service control"
      - field: "execution_context"
        type: "str"
        description: "Detected run mode"
    outputs:
      - field: "exit_code"
        type: "int"
        description: "Service exit status"
    key_elements:
      - name: "ServiceMain"
        type: "function"
        purpose: "Entry point for application, routes to installer or service loop"
    dependencies:
      internal:
        - "Installer"
        - "StateMonitor"
        - "All other components"
      external:
        - "logging"
        - "signal"
        - "systemd"
        - "os (privilege detection)"
    processing_logic:
      - "Detect execution mode: check if running under systemd or manual invocation"
      - "If systemd service not installed: invoke Installer and exit"
      - "If installed: proceed with normal service operation"
      - "Setup logging to /var/log/pi-netconfig.log"
      - "Register signal handlers for graceful shutdown"
      - "Initialize StateMonitor and start event loop"
      - "On shutdown: deactivate AP, close web server, exit cleanly"
    error_conditions:
      - condition: "Insufficient privileges for service mode"
        handling: "Log critical error, exit with code 1"
      - condition: "Unhandled exception"
        handling: "Log traceback, attempt cleanup, exit with code 1"

data_design:
  entities:
    - name: "NetworkInfo"
      purpose: "Represent scanned WiFi network"
      attributes:
        - name: "ssid"
          type: "str"
          constraints: "non-empty"
        - name: "signal_strength"
          type: "int"
          constraints: "0-100"
        - name: "security"
          type: "str"
          constraints: "enum: WPA2, WPA3, Open"
        - name: "frequency"
          type: "str"
          constraints: "2.4GHz or 5GHz"
      relationships: []
    - name: "ConfigurationData"
      purpose: "Persist single network configuration"
      attributes:
        - name: "configured_ssid"
          type: "str"
          constraints: "nullable, last successful connection only"
        - name: "timestamp"
          type: "datetime"
          constraints: "ISO 8601 format"
      relationships: []
  storage:
    - name: "/etc/pi-netconfig/config.json"
      fields:
        - name: "configured_ssid"
          type: "string"
          constraints: "nullable"
        - name: "last_connected"
          type: "string (ISO datetime)"
          constraints: "nullable"
        - name: "ap_password"
          type: "string"
          constraints: "default: piconfig123"
      indexes: []
  validation_rules:
    - "SSID length: 1-32 characters"
    - "Password length: 8-63 characters for WPA2"
    - "No special shell characters in credentials"

interfaces:
  internal:
    - name: "test_connection"
      purpose: "Verify active internet connectivity"
      signature: "async def test_connection() -> bool"
      parameters: []
      returns:
        type: "bool"
        description: "True if connection active"
      raises:
        - exception: "ConnectionManagerError"
          condition: "Unable to perform connectivity test"
    - name: "scan_networks"
      purpose: "Scan for available WiFi networks"
      signature: "async def scan_networks() -> List[NetworkInfo]"
      parameters: []
      returns:
        type: "List[NetworkInfo]"
        description: "Available networks sorted by signal strength"
      raises:
        - exception: "ConnectionManagerError"
          condition: "Scan operation fails"
    - name: "configure_network"
      purpose: "Apply WiFi configuration"
      signature: "async def configure_network(ssid: str, password: str) -> bool"
      parameters:
        - name: "ssid"
          type: "str"
          description: "Target network SSID"
        - name: "password"
          type: "str"
          description: "Network password"
      returns:
        type: "bool"
        description: "True if configuration successful"
      raises:
        - exception: "ConnectionManagerError"
          condition: "Configuration fails"
    - name: "activate_ap"
      purpose: "Enable access point mode"
      signature: "async def activate_ap() -> bool"
      parameters: []
      returns:
        type: "bool"
        description: "True if AP activated successfully"
      raises:
        - exception: "APManagerError"
          condition: "AP activation fails"
  external:
    - name: "Web API"
      protocol: "HTTP/1.1"
      data_format: "JSON"
      specification: |
        GET /api/scan -> {"networks": [{"ssid": str, "signal": int, "security": str}]}
        POST /api/configure {"ssid": str, "password": str} -> {"success": bool, "message": str}
        GET /api/status -> {"state": str, "ssid": str|null, "ap_active": bool}

error_handling:
  exception_hierarchy:
    base: "PiNetConfigError"
    specific:
      - "InstallerError"
      - "ConnectionManagerError"
      - "APManagerError"
      - "WebServerError"
      - "ConfigurationError"
  strategy:
    validation_errors: "Return descriptive message via web interface, log warning"
    runtime_errors: "Log with traceback, attempt recovery to known state"
    external_failures: "Retry with exponential backoff, fallback to degraded mode"
  logging:
    levels:
      - "DEBUG: state transitions, nmcli commands"
      - "INFO: connection status changes, configuration updates"
      - "WARNING: failed connection attempts, retries"
      - "ERROR: component failures, unrecoverable errors"
      - "CRITICAL: service shutdown due to error"
    required_info:
      - "Timestamp"
      - "Log level"
      - "Component name"
      - "Message"
      - "Stack trace (for errors)"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

nonfunctional_requirements:
  performance:
    - metric: "Boot to ready"
      target: "< 30 seconds"
    - metric: "Network scan"
      target: "< 5 seconds"
    - metric: "Configuration application"
      target: "< 10 seconds"
  security:
    authentication: "None - local network access only"
    authorization: "Root privileges required for service"
    data_protection:
      - "WiFi passwords stored in NetworkManager secure storage"
      - "Configuration file readable only by root"
      - "No credential logging"
  reliability:
    error_recovery: "Automatic recovery to AP mode on repeated failures"
    fault_tolerance:
      - "Continue operation if single component fails"
      - "Graceful degradation if WiFi hardware unavailable"
  maintainability:
    code_organization:
      - "Single-file implementation for simplicity"
      - "Clear separation of concerns via classes"
      - "Type hints throughout"
    documentation:
      - "Docstrings for all public methods"
      - "Self-installation guide (run as root on first execution)"
      - "Systemd service management instructions"
    testing:
      coverage_target: "80%"
      approaches:
        - "Unit tests for state transitions"
        - "Mock NetworkManager for integration tests"
        - "Manual end-to-end testing on Raspberry Pi"

version_history:
  - version: "0.2.0"
    date: "2025-11-10"
    author: "William Watson"
    changes:
      - "Added Installer module for self-installation as systemd service"
      - "Updated ServiceController to handle bootstrap vs service mode"
      - "Modified architecture to self-bootstrapping pattern"
      - "Added InstallerError exception type"
  - version: "0.1.1"
    date: "2025-11-10"
    author: "William Watson"
    changes:
      - "Clarified single network configuration approach"
      - "Removed web authentication requirement"
      - "Removed LED/notification system from scope"
  - version: "0.1.0"
    date: "2025-11-10"
    author: "William Watson"
    changes:
      - "Initial master design document"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t01_design"
