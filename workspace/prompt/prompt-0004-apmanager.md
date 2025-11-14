Created: 2025 November 12

# T04 Prompt: APManager Module

```yaml
prompt_info:
  id: "prompt-0004"
  task_type: "code_generation"
  source_ref: "design-0004-apmanager"
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
  purpose: "Create and manage local WiFi access point for configuration when no router connection exists"
  integration: "Invoked by StateMonitor when transitioning to/from AP_MODE"
  constraints:
    - "Must use NetworkManager for AP mode"
    - "Single WiFi interface (cannot run AP + client simultaneously)"
    - "Requires root privileges"

specification:
  description: "Implement access point management with SSID generation from MAC address, WPA2 security, DHCP configuration, and lifecycle management"
  requirements:
    functional:
      - "Generate SSID: PiConfig-XXXX (XXXX = last 4 hex digits of MAC address)"
      - "Fixed password: piconfig123"
      - "Activate AP with NetworkManager: mode=ap, IP=192.168.50.1/24, DHCP enabled"
      - "Deactivate AP when transitioning to client mode"
      - "Fallback to open AP if WPA2 fails"
      - "Detect WiFi interface dynamically"
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Thread-safe, comprehensive error handling, debug logging, docstrings, type hints"
  performance:
    - target: "AP activation under 10 seconds"
      metric: "time"
    - target: "AP deactivation under 3 seconds"
      metric: "time"

design:
  architecture: "Class-based with NetworkManager integration via nmcli"
  components:
    - name: "AccessPoint"
      type: "class"
      purpose: "Manage AP connection profile lifecycle"
      interface:
        inputs: []
        outputs:
          type: "bool or str"
          description: "Activation status or SSID"
        raises:
          - "APManagerError"
          - "APActivationError"
          - "InterfaceDetectionError"
          - "ProfileCreationError"
      logic:
        - "get_wifi_interface(): Execute nmcli device status, find wifi type"
        - "get_mac_address(): Execute nmcli device show, extract HWADDR"
        - "generate_ssid(): Format PiConfig-XXXX from last 4 MAC hex digits"
        - "create_ap_profile(): nmcli con add type wifi mode ap, configure WPA2-PSK, set IP 192.168.50.1/24 with shared method"
        - "activate_ap(): nmcli con up, set ap_active=True"
        - "deactivate_ap(): nmcli con down, set ap_active=False"
        - "fallback_to_open_ap(): Remove WPA2, create open network"
    
    - name: "activate_ap"
      type: "function"
      purpose: "Public activation entry point"
      interface:
        inputs: []
        outputs:
          type: "bool"
          description: "True if activated"
        raises:
          - "APManagerError"
      logic:
        - "Check if already active (idempotent)"
        - "Create profile if not exists"
        - "Activate connection"
    
    - name: "deactivate_ap"
      type: "function"
      purpose: "Public deactivation entry point"
      interface:
        inputs: []
        outputs:
          type: "None"
        raises:
          - "APManagerError"
      logic:
        - "Check if active"
        - "Deactivate connection"
    
    - name: "get_ap_ssid"
      type: "function"
      purpose: "Return current AP SSID"
      interface:
        inputs: []
        outputs:
          type: "str"
          description: "Generated SSID"
        raises:
          - "APManagerError"
  
  dependencies:
    internal: []
    external:
      - "subprocess - nmcli execution"
      - "re - MAC address parsing"

data_schema:
  entities:
    - name: "APConfiguration"
      attributes:
        - name: "ssid"
          type: "str"
          constraints: "PiConfig-XXXX format"
        - name: "password"
          type: "str"
          constraints: "piconfig123 (fixed)"
        - name: "ip_address"
          type: "str"
          constraints: "192.168.50.1/24"
        - name: "security"
          type: "str"
          constraints: "WPA2-PSK or Open"
      validation:
        - "SSID generated from valid MAC address"
        - "IP configuration uses shared method (built-in DHCP)"

error_handling:
  strategy: "Raise specific exceptions, attempt fallback to open AP on WPA2 failure"
  exceptions:
    - exception: "APManagerError"
      condition: "Base exception"
      handling: "Log with traceback"
    - exception: "InterfaceDetectionError"
      condition: "No wifi interface found"
      handling: "Log critical, raise to StateMonitor"
    - exception: "APActivationError"
      condition: "nmcli con up fails"
      handling: "Attempt fallback to open AP"
    - exception: "ProfileCreationError"
      condition: "nmcli con add fails"
      handling: "Log error with command details, raise"
  logging:
    level: "DEBUG for commands, INFO for success, WARNING for fallback, ERROR for failures, CRITICAL for no interface"
    format: "Logger name 'APManager'"

testing:
  unit_tests:
    - scenario: "WiFi interface detection"
      expected: "Returns wlan0 or similar"
    - scenario: "MAC address extraction"
      expected: "Returns XX:XX:XX:XX:XX:XX format"
    - scenario: "SSID generation"
      expected: "PiConfig-XXXX with last 4 hex digits"
    - scenario: "AP activation"
      expected: "Connection active, ap_active=True"
    - scenario: "AP deactivation"
      expected: "Connection down, ap_active=False"
  edge_cases:
    - "No WiFi interface available"
    - "MAC address extraction fails"
    - "WPA2 AP creation fails"
    - "Interface busy with client connection"
  validation:
    - "SSID format matches PiConfig-XXXX pattern"
    - "AP network accessible at 192.168.50.1"
    - "Idempotent activation/deactivation"

output_format:
  structure: "code_only"
  integration_notes: "brief"

deliverable:
  files:
    - path: "src/apmanager.py"
      content: "Complete AP manager implementation"
  documentation:
    - "Integration: Import activate_ap(), deactivate_ap(), get_ap_ssid(), is_active(). Called by StateMonitor for mode transitions."

success_criteria:
  - "WiFi interface detected correctly"
  - "SSID generated from MAC address"
  - "AP activates with correct configuration"
  - "DHCP server functional (192.168.50.x)"
  - "AP deactivates cleanly"
  - "Fallback to open AP on WPA2 failure"
  - "Idempotent operations"

notes: "AP and client modes mutually exclusive. No internal dependencies. Uses NetworkManager via nmcli."

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

## Design Specification

**Purpose:** Manage temporary WiFi access point for configuration.

**Key Methods:**

- `get_wifi_interface() -> str`: nmcli device status, find wifi type
- `get_mac_address() -> str`: nmcli device show, extract HWADDR
- `generate_ssid() -> str`: Format PiConfig-XXXX from last 4 MAC hex digits
- `create_ap_profile() -> None`: nmcli con add + modify for AP mode, WPA2, IP 192.168.50.1/24 shared
- `activate_ap() -> bool`: nmcli con up, idempotent
- `deactivate_ap() -> None`: nmcli con down
- `fallback_to_open_ap() -> bool`: Remove WPA2, create open network

**NetworkManager Configuration:**
```bash
nmcli con add type wifi ifname wlan0 con-name pi-netconfig-ap mode ap ssid PiConfig-XXXX
nmcli con modify pi-netconfig-ap 802-11-wireless-security.key-mgmt wpa-psk
nmcli con modify pi-netconfig-ap 802-11-wireless-security.psk piconfig123
nmcli con modify pi-netconfig-ap ipv4.method shared ipv4.addresses 192.168.50.1/24
nmcli con up id pi-netconfig-ap
```

**Exception Hierarchy:** APManagerError → APActivationError, InterfaceDetectionError, ProfileCreationError

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
