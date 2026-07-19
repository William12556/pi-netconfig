Created: 2025 November 12

# T05 Test: APManager Module

## Table of Contents

[Test Info](<#test info>)
[Source](<#source>)
[Scope](<#scope>)
[Test Environment](<#test environment>)
[Test Cases](<#test cases>)
[Coverage](<#coverage>)
[Test Execution Summary](<#test execution summary>)
[Defect Summary](<#defect summary>)
[Verification](<#verification>)
[Traceability](<#traceability>)
[Version History](<#version history>)

---

## Test Info

```yaml
test_info:
  id: "test-0001"
  title: "APManager Module Testing"
  date: "2025-11-12"
  author: "William Watson"
  status: "planned"
  type: "unit"
  priority: "high"
```

[Return to Table of Contents](<#table of contents>)

---

## Source

```yaml
source:
  test_target: "APManager Module (src/apmanager.py)"
  design_refs:
    - "design-0004-apmanager.md"
  change_refs: []
  requirement_refs:
    - "R-APM-001: Generate SSID from MAC address"
    - "R-APM-002: Create WPA2-PSK access point"
    - "R-APM-003: Configure DHCP at 192.168.50.1/24"
    - "R-APM-004: Fallback to open AP on WPA2 failure"
    - "R-APM-005: Idempotent activation/deactivation"
```

[Return to Table of Contents](<#table of contents>)

---

## Scope

```yaml
scope:
  description: "Verify APManager correctly creates, activates, and manages WiFi access point for network configuration"
  test_objectives:
    - "Validate WiFi interface detection"
    - "Verify MAC address extraction and SSID generation"
    - "Test AP profile creation with NetworkManager"
    - "Validate AP activation and deactivation"
    - "Verify DHCP functionality at 192.168.50.1/24"
    - "Test fallback to open AP"
    - "Verify exception handling"
  in_scope:
    - "WiFi interface detection"
    - "MAC address parsing"
    - "SSID format validation"
    - "NetworkManager profile operations"
    - "Connection activation/deactivation"
    - "Error condition handling"
    - "State tracking (ap_active)"
  out_scope:
    - "Actual WiFi radio transmission"
    - "Client device connections"
    - "Web interface integration"
    - "StateMonitor coordination"
  dependencies:
    - "NetworkManager service running"
    - "WiFi hardware present"
    - "Root privileges for nmcli commands"
```

[Return to Table of Contents](<#table of contents>)

---

## Test Environment

```yaml
test_environment:
  python_version: "3.11+"
  os: "Raspberry Pi OS / Debian"
  libraries:
    - name: "pytest"
      version: "7.0.0+"
    - name: "pytest-asyncio"
      version: "0.21.0+"
  test_framework: "pytest"
  test_data_location: "workspace/test/result/"
```

[Return to Table of Contents](<#table of contents>)

---

## Test Cases

### TC-001: WiFi Interface Detection

```yaml
case_id: "TC-001"
description: "Verify get_wifi_interface() correctly identifies WiFi device"
category: "positive"
preconditions:
  - "NetworkManager running"
  - "WiFi hardware present"
test_steps:
  - step: "1"
    action: "Create AccessPoint instance"
  - step: "2"
    action: "Call get_wifi_interface()"
  - step: "3"
    action: "Verify returned interface name"
inputs:
  - parameter: "nmcli device status output"
    value: "wifi device present"
    type: "system state"
expected_outputs:
  - field: "interface"
    expected_value: "wlan0 or similar"
    validation: "String matching wifi interface pattern"
postconditions:
  - "Interface name stored in self.interface"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "Returns valid wifi interface name"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-002: WiFi Interface Not Found

```yaml
case_id: "TC-002"
description: "Verify InterfaceDetectionError raised when no WiFi interface exists"
category: "negative"
preconditions:
  - "NetworkManager running"
  - "No WiFi hardware"
test_steps:
  - step: "1"
    action: "Mock nmcli to return no wifi devices"
  - step: "2"
    action: "Attempt to create AccessPoint instance"
  - step: "3"
    action: "Catch InterfaceDetectionError"
inputs:
  - parameter: "nmcli device status output"
    value: "no wifi devices"
    type: "mocked system state"
expected_outputs:
  - field: "exception"
    expected_value: "InterfaceDetectionError"
    validation: "Exception raised with appropriate message"
postconditions:
  - "Error logged at CRITICAL level"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "InterfaceDetectionError raised"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-003: MAC Address Extraction

```yaml
case_id: "TC-003"
description: "Verify get_mac_address() extracts MAC from nmcli output"
category: "positive"
preconditions:
  - "WiFi interface detected"
  - "Interface has valid MAC address"
test_steps:
  - step: "1"
    action: "Execute get_mac_address()"
  - step: "2"
    action: "Parse nmcli device show output"
  - step: "3"
    action: "Extract GENERAL.HWADDR value"
inputs:
  - parameter: "nmcli device show wlan0"
    value: "GENERAL.HWADDR: XX:XX:XX:XX:XX:XX"
    type: "system command output"
expected_outputs:
  - field: "mac_address"
    expected_value: "XX:XX:XX:XX:XX:XX format"
    validation: "Valid MAC address pattern"
postconditions:
  - "MAC address stored in self.mac_address"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "Returns MAC in XX:XX:XX:XX:XX:XX format"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-004: SSID Generation Format

```yaml
case_id: "TC-004"
description: "Verify generate_ssid() creates PiConfig-XXXX format"
category: "positive"
preconditions:
  - "MAC address extracted: AA:BB:CC:DD:EE:FF"
test_steps:
  - step: "1"
    action: "Set mac_address = 'AA:BB:CC:DD:EE:FF'"
  - step: "2"
    action: "Call generate_ssid()"
  - step: "3"
    action: "Verify SSID format"
inputs:
  - parameter: "mac_address"
    value: "AA:BB:CC:DD:EE:FF"
    type: "string"
expected_outputs:
  - field: "ssid"
    expected_value: "PiConfig-EEFF"
    validation: "Matches PiConfig-[0-9A-F]{4} pattern"
postconditions:
  - "SSID stored in self.ssid"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "SSID matches PiConfig-XXXX format with last 4 hex digits"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-005: AP Profile Creation

```yaml
case_id: "TC-005"
description: "Verify create_ap_profile() executes correct nmcli commands"
category: "positive"
preconditions:
  - "WiFi interface available"
  - "SSID generated"
  - "No existing pi-netconfig-ap profile"
test_steps:
  - step: "1"
    action: "Mock subprocess.check_output"
  - step: "2"
    action: "Call create_ap_profile()"
  - step: "3"
    action: "Verify nmcli commands executed"
inputs:
  - parameter: "interface"
    value: "wlan0"
    type: "string"
  - parameter: "ssid"
    value: "PiConfig-EEFF"
    type: "string"
expected_outputs:
  - field: "nmcli con add"
    expected_value: "type=wifi ifname=wlan0 con-name=pi-netconfig-ap mode=ap ssid=PiConfig-EEFF"
    validation: "Command executed"
  - field: "nmcli con modify (security)"
    expected_value: "802-11-wireless-security.key-mgmt wpa-psk"
    validation: "Command executed"
  - field: "nmcli con modify (password)"
    expected_value: "802-11-wireless-security.psk piconfig123"
    validation: "Command executed"
  - field: "nmcli con modify (ip)"
    expected_value: "ipv4.method shared ipv4.addresses 192.168.50.1/24"
    validation: "Command executed"
postconditions:
  - "AP profile exists in NetworkManager"
  - "INFO log: 'AP profile created successfully'"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "All nmcli commands execute successfully"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-006: AP Activation

```yaml
case_id: "TC-006"
description: "Verify activate_ap() brings up AP connection"
category: "positive"
preconditions:
  - "AP profile created"
  - "AP not currently active"
test_steps:
  - step: "1"
    action: "Call public activate_ap()"
  - step: "2"
    action: "Verify profile creation"
  - step: "3"
    action: "Verify connection activation"
inputs:
  - parameter: "profile_name"
    value: "pi-netconfig-ap"
    type: "string"
expected_outputs:
  - field: "nmcli con up"
    expected_value: "id pi-netconfig-ap"
    validation: "Command executed"
  - field: "ap_active"
    expected_value: "True"
    validation: "State updated"
  - field: "return_value"
    expected_value: "True"
    validation: "Function returns True"
postconditions:
  - "AP connection active"
  - "INFO log: 'Access point activated successfully'"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "Returns True and AP accessible at 192.168.50.1"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-007: AP Deactivation

```yaml
case_id: "TC-007"
description: "Verify deactivate_ap() brings down AP connection"
category: "positive"
preconditions:
  - "AP currently active"
test_steps:
  - step: "1"
    action: "Call public deactivate_ap()"
  - step: "2"
    action: "Verify connection deactivation"
inputs:
  - parameter: "profile_name"
    value: "pi-netconfig-ap"
    type: "string"
expected_outputs:
  - field: "nmcli con down"
    expected_value: "id pi-netconfig-ap"
    validation: "Command executed"
  - field: "ap_active"
    expected_value: "False"
    validation: "State updated"
postconditions:
  - "AP connection inactive"
  - "INFO log: 'Access point deactivated successfully'"
  - "Profile still exists for reuse"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "AP no longer accessible"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-008: Idempotent Activation

```yaml
case_id: "TC-008"
description: "Verify activate_ap() succeeds when already active"
category: "edge"
preconditions:
  - "AP already active"
test_steps:
  - step: "1"
    action: "Call activate_ap() first time"
  - step: "2"
    action: "Call activate_ap() second time"
  - step: "3"
    action: "Verify no errors, returns True"
inputs:
  - parameter: "ap_active"
    value: "True"
    type: "state"
expected_outputs:
  - field: "return_value"
    expected_value: "True"
    validation: "Function returns True without error"
  - field: "nmcli calls"
    expected_value: "Minimal or none"
    validation: "No redundant activation attempts"
postconditions:
  - "AP remains active"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "Returns True without exceptions"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-009: Idempotent Deactivation

```yaml
case_id: "TC-009"
description: "Verify deactivate_ap() succeeds when already inactive"
category: "edge"
preconditions:
  - "AP already inactive"
test_steps:
  - step: "1"
    action: "Ensure AP inactive"
  - step: "2"
    action: "Call deactivate_ap()"
  - step: "3"
    action: "Verify no errors"
inputs:
  - parameter: "ap_active"
    value: "False"
    type: "state"
expected_outputs:
  - field: "nmcli calls"
    expected_value: "None or minimal"
    validation: "No redundant deactivation attempts"
postconditions:
  - "No exceptions raised"
  - "State remains inactive"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "Completes without exceptions"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-010: Fallback to Open AP

```yaml
case_id: "TC-010"
description: "Verify fallback_to_open_ap() removes WPA2 security"
category: "positive"
preconditions:
  - "WPA2 AP creation failed"
  - "Profile exists but not activated"
test_steps:
  - step: "1"
    action: "Mock WPA2 activation failure"
  - step: "2"
    action: "Call fallback_to_open_ap()"
  - step: "3"
    action: "Verify security removed"
inputs:
  - parameter: "profile_name"
    value: "pi-netconfig-ap"
    type: "string"
expected_outputs:
  - field: "nmcli con modify"
    expected_value: "802-11-wireless-security.key-mgmt ''"
    validation: "Security removed"
  - field: "log_level"
    expected_value: "WARNING"
    validation: "Warning logged about open network"
postconditions:
  - "AP accessible without password"
  - "WARNING log about security risk"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "Open AP created successfully"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-011: Get AP SSID

```yaml
case_id: "TC-011"
description: "Verify get_ap_ssid() returns current SSID"
category: "positive"
preconditions:
  - "AccessPoint initialized"
  - "SSID generated"
test_steps:
  - step: "1"
    action: "Call get_ap_ssid()"
  - step: "2"
    action: "Verify return value"
inputs: []
expected_outputs:
  - field: "ssid"
    expected_value: "PiConfig-XXXX format"
    validation: "Matches generated SSID"
postconditions: []
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "Returns valid SSID string"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-012: Check Active Status

```yaml
case_id: "TC-012"
description: "Verify is_active() reflects current AP state"
category: "positive"
preconditions:
  - "AP in known state (active or inactive)"
test_steps:
  - step: "1"
    action: "Set known AP state"
  - step: "2"
    action: "Call is_active()"
  - step: "3"
    action: "Verify return matches state"
inputs:
  - parameter: "ap_active"
    value: "True or False"
    type: "state"
expected_outputs:
  - field: "return_value"
    expected_value: "Matches ap_active state"
    validation: "Boolean matches internal state"
postconditions: []
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "Returns correct boolean"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-013: Profile Creation Failure

```yaml
case_id: "TC-013"
description: "Verify ProfileCreationError raised on nmcli failure"
category: "negative"
preconditions:
  - "nmcli con add will fail"
test_steps:
  - step: "1"
    action: "Mock nmcli to return error"
  - step: "2"
    action: "Attempt create_ap_profile()"
  - step: "3"
    action: "Catch ProfileCreationError"
inputs:
  - parameter: "nmcli con add"
    value: "CalledProcessError"
    type: "mocked failure"
expected_outputs:
  - field: "exception"
    expected_value: "ProfileCreationError"
    validation: "Correct exception raised"
  - field: "log_level"
    expected_value: "ERROR"
    validation: "Error logged with traceback"
postconditions:
  - "No profile created"
  - "Error logged"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "ProfileCreationError raised with details"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-014: Activation Failure

```yaml
case_id: "TC-014"
description: "Verify APActivationError raised on connection failure"
category: "negative"
preconditions:
  - "Profile exists"
  - "nmcli con up will fail"
test_steps:
  - step: "1"
    action: "Mock nmcli con up to fail"
  - step: "2"
    action: "Call activate_ap()"
  - step: "3"
    action: "Catch APActivationError"
inputs:
  - parameter: "nmcli con up"
    value: "CalledProcessError"
    type: "mocked failure"
expected_outputs:
  - field: "exception"
    expected_value: "APActivationError"
    validation: "Correct exception raised"
  - field: "log_level"
    expected_value: "ERROR"
    validation: "Error logged"
postconditions:
  - "ap_active remains False"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "APActivationError raised"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

### TC-015: State Persistence

```yaml
case_id: "TC-015"
description: "Verify ap_active state persists across method calls"
category: "positive"
preconditions:
  - "AccessPoint instance created"
test_steps:
  - step: "1"
    action: "Activate AP"
  - step: "2"
    action: "Check is_active() returns True"
  - step: "3"
    action: "Deactivate AP"
  - step: "4"
    action: "Check is_active() returns False"
inputs: []
expected_outputs:
  - field: "state_transitions"
    expected_value: "False -> True -> False"
    validation: "State tracked correctly"
postconditions:
  - "State reflects actual AP status"
execution:
  status: "not_run"
  executed_date: ""
  executed_by: ""
  actual_result: ""
  pass_fail_criteria: "State transitions tracked correctly"
defects: []
```

[Return to Table of Contents](<#table of contents>)

---

## Coverage

```yaml
coverage:
  requirements_covered:
    - requirement_ref: "R-APM-001: Generate SSID from MAC"
      test_cases:
        - "TC-003"
        - "TC-004"
    - requirement_ref: "R-APM-002: Create WPA2-PSK AP"
      test_cases:
        - "TC-005"
        - "TC-006"
    - requirement_ref: "R-APM-003: Configure DHCP at 192.168.50.1/24"
      test_cases:
        - "TC-005"
        - "TC-006"
    - requirement_ref: "R-APM-004: Fallback to open AP"
      test_cases:
        - "TC-010"
    - requirement_ref: "R-APM-005: Idempotent operations"
      test_cases:
        - "TC-008"
        - "TC-009"
  code_coverage:
    target: "80%"
    achieved: ""
  untested_areas:
    - component: "Actual WiFi transmission"
      reason: "Requires physical hardware and client devices"
    - component: "DHCP client connections"
      reason: "Integration testing with StateMonitor"
```

[Return to Table of Contents](<#table of contents>)

---

## Test Execution Summary

```yaml
test_execution_summary:
  total_cases: 15
  passed: 0
  failed: 0
  blocked: 0
  skipped: 0
  pass_rate: ""
  execution_time: ""
  test_cycle: "Initial"
```

[Return to Table of Contents](<#table of contents>)

---

## Defect Summary

```yaml
defect_summary:
  total_defects: 0
  critical: 0
  high: 0
  medium: 0
  low: 0
  issues: []
```

[Return to Table of Contents](<#table of contents>)

---

## Verification

```yaml
verification:
  verified_date: ""
  verified_by: ""
  verification_notes: ""
  sign_off: ""
```

[Return to Table of Contents](<#table of contents>)

---

## Traceability

```yaml
traceability:
  requirements:
    - requirement_ref: "R-APM-001"
      test_cases:
        - "TC-003"
        - "TC-004"
    - requirement_ref: "R-APM-002"
      test_cases:
        - "TC-005"
        - "TC-006"
    - requirement_ref: "R-APM-003"
      test_cases:
        - "TC-005"
    - requirement_ref: "R-APM-004"
      test_cases:
        - "TC-010"
    - requirement_ref: "R-APM-005"
      test_cases:
        - "TC-008"
        - "TC-009"
  designs:
    - design_ref: "design-0004-apmanager.md"
      test_cases:
        - "TC-001"
        - "TC-002"
        - "TC-003"
        - "TC-004"
        - "TC-005"
        - "TC-006"
        - "TC-007"
        - "TC-008"
        - "TC-009"
        - "TC-010"
        - "TC-011"
        - "TC-012"
        - "TC-013"
        - "TC-014"
        - "TC-015"
  changes: []
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-12 | William Watson | Initial test document created from design-0004 |

[Return to Table of Contents](<#table of contents>)

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
