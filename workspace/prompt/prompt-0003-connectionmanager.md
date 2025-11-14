Created: 2025 November 12

# T04 Prompt: ConnectionManager Module

```yaml
prompt_info:
  id: "prompt-0003"
  task_type: "code_generation"
  source_ref: "design-0003-connectionmanager"
  date: "2025-11-12"
  priority: "high"

mcp_config:
  model: "claude-sonnet-4-20250514"
  temperature: 0.2
  max_tokens: 4096
  system_prompt: |
    Expert Python developer. Generate production-quality code following specifications.
    OUTPUT FORMAT: Code only with brief integration notes. No explanations.

context:
  purpose: "Manage WiFi client mode connections including connectivity testing, network scanning, configuration, and persistence"
  integration: "Invoked by StateMonitor for connection checks, by WebServer for scanning and configuration"
  constraints:
    - "Must use NetworkManager (nmcli) for all WiFi operations"
    - "Single network configuration (last successful only)"
    - "Non-blocking async operations"

specification:
  description: "Implement WiFi connection management with internet connectivity testing, network scanning, configuration application, and JSON persistence"
  requirements:
    functional:
      - "Test internet connectivity via ping to 8.8.8.8 and 1.1.1.1"
      - "Scan WiFi networks using nmcli, parse and return sorted by signal strength"
      - "Configure NetworkManager connection with SSID and password"
      - "Validate credentials (SSID 1-32 chars, password 8-63 chars for WPA2)"
      - "Persist configuration to /etc/pi-netconfig/config.json"
      - "Load persisted configuration on startup"
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Thread-safe, comprehensive error handling, debug logging, docstrings, type hints"
  performance:
    - target: "Connectivity test under 3 seconds"
      metric: "time"
    - target: "Network scan under 5 seconds"
      metric: "time"
    - target: "Configuration application under 10 seconds"
      metric: "time"

design:
  architecture: "Class-based with separation of testing, scanning, and configuration"
  components:
    - name: "ConnectionTester"
      type: "class"
      purpose: "Verify internet connectivity"
      interface:
        inputs: []
        outputs:
          type: "bool"
          description: "True if either host reachable"
        raises:
          - "ConnectionManagerError"
      logic:
        - "Socket connect to 8.8.8.8:53, timeout 1s"
        - "If fails, try 1.1.1.1:53, timeout 1s"
        - "Return True if either succeeds, False otherwise"
    
    - name: "NetworkScanner"
      type: "class"
      purpose: "Scan and parse WiFi networks"
      interface:
        inputs: []
        outputs:
          type: "List[NetworkInfo]"
          description: "Networks sorted by signal strength descending"
        raises:
          - "NetworkScanError"
      logic:
        - "Execute: nmcli -t -f SSID,SIGNAL,SECURITY,FREQ dev wifi list"
        - "Parse terse output: SSID:SIGNAL:SECURITY:FREQ"
        - "Create NetworkInfo dataclass instances"
        - "Filter duplicates (keep strongest)"
        - "Sort by signal descending"
    
    - name: "ConfigManager"
      type: "class"
      purpose: "Apply and persist NetworkManager configurations"
      interface:
        inputs:
          - name: "ssid"
            type: "str"
            description: "Network SSID"
          - name: "password"
            type: "str"
            description: "Network password"
        outputs:
          type: "bool"
          description: "Configuration success"
        raises:
          - "ConfigurationError"
      logic:
        - "Validate SSID: 1-32 chars, no shell special chars"
        - "Validate password: 8-63 chars for WPA2"
        - "Delete existing connection profile"
        - "Create new profile: nmcli con add type wifi ssid {ssid} wifi-sec.key-mgmt wpa-psk wifi-sec.psk {password}"
        - "Activate: nmcli con up id {ssid}"
        - "Persist to /etc/pi-netconfig/config.json"
    
    - name: "NetworkInfo"
      type: "dataclass"
      purpose: "Network scan result structure"
      interface:
        inputs:
          - name: "ssid"
            type: "str"
            description: "Network name"
          - name: "signal_strength"
            type: "int"
            description: "Signal 0-100"
          - name: "security"
            type: "str"
            description: "WPA2, WPA3, Open, etc"
          - name: "frequency"
            type: "str"
            description: "2.4GHz or 5GHz"
        outputs:
          type: "NetworkInfo"
          description: "Dataclass instance"
        raises: []
      logic:
        - "Simple dataclass with four fields"
  
  dependencies:
    internal: []
    external:
      - "subprocess - nmcli execution"
      - "socket - connectivity testing"
      - "json - config persistence"
      - "pathlib - file operations"

data_schema:
  entities:
    - name: "config.json"
      attributes:
        - name: "configured_ssid"
          type: "str"
          constraints: "Last configured network or null"
        - name: "last_connected"
          type: "str"
          constraints: "ISO 8601 timestamp"
        - name: "ap_password"
          type: "str"
          constraints: "Default: piconfig123"
      validation:
        - "SSID: 1-32 chars, no ;,&,|,$,`,\\,',\""
        - "Password: 8-63 chars for WPA2, no shell special chars"

error_handling:
  strategy: "Raise specific exceptions, nmcli failures logged with stderr"
  exceptions:
    - exception: "ConnectionManagerError"
      condition: "Base exception"
      handling: "Log with traceback"
    - exception: "ConfigurationError"
      condition: "Validation or application failure"
      handling: "Return error to WebServer for user correction"
    - exception: "NetworkScanError"
      condition: "nmcli scan failure"
      handling: "Log error, return empty list"
  logging:
    level: "DEBUG for commands, INFO for success, WARNING for failures, ERROR for errors"
    format: "Logger name 'ConnectionManager'"

testing:
  unit_tests:
    - scenario: "Connectivity test both hosts reachable"
      expected: "Returns True"
    - scenario: "Both hosts unreachable"
      expected: "Returns False"
    - scenario: "Network scan returns results"
      expected: "List of NetworkInfo sorted by signal"
    - scenario: "Valid SSID and password"
      expected: "Configuration succeeds, returns True"
    - scenario: "Invalid SSID (too long)"
      expected: "Raises ConfigurationError"
  edge_cases:
    - "No WiFi networks found"
    - "nmcli not available"
    - "Connection activation timeout"
    - "JSON parse error in config file"
  validation:
    - "Socket connections use 1-second timeout"
    - "nmcli commands include error checking"
    - "Config file created with proper permissions"

output_format:
  structure: "code_only"
  integration_notes: "brief"

deliverable:
  files:
    - path: "src/connectionmanager.py"
      content: "Complete connection manager implementation"
  documentation:
    - "Integration: Import test_connection(), scan_networks(), configure_network(), load_configuration(). Called by StateMonitor and WebServer."

success_criteria:
  - "Connectivity tests work for both reachable and unreachable hosts"
  - "Network scanning parses nmcli output correctly"
  - "Configuration validates credentials properly"
  - "nmcli commands execute with proper error handling"
  - "Configuration persists to JSON"
  - "All async operations non-blocking"

notes: "Core network operations module. No internal dependencies. Uses only stdlib plus NetworkManager via nmcli."

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

## Design Specification

**Purpose:** Manage WiFi client mode connections.

**Key Methods:**

- `test_connection() -> bool`: Socket connect to 8.8.8.8:53 and 1.1.1.1:53
- `scan_networks() -> List[NetworkInfo]`: nmcli dev wifi list, parse, sort
- `configure_network(ssid, password) -> bool`: Validate, create profile, activate, persist
- `load_configuration() -> Optional[str]`: Read /etc/pi-netconfig/config.json

**Validation:** SSID 1-32 chars, password 8-63 chars for WPA2, no shell special chars

**Config File:** `/etc/pi-netconfig/config.json`
```json
{
  "configured_ssid": "NetworkName",
  "last_connected": "2025-11-12T10:00:00Z",
  "ap_password": "piconfig123"
}
```

**Exception Hierarchy:** ConnectionManagerError → ConfigurationError, NetworkScanError

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
