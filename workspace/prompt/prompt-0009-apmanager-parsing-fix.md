Created: 2025 November 26

# T04 Prompt: APManager nmcli Parsing Fix

```yaml
prompt_info:
  id: "prompt-0009"
  task_type: "bugfix"
  source_ref: "change-0006-apmanager-nmcli-parsing-correction"
  date: "2025-11-26"
  priority: "critical"

mcp_config:
  model: "claude-sonnet-4-20250514"
  temperature: 0.2
  max_tokens: 4096
  system_prompt: |
    Expert Python developer. Generate production-quality code following specifications.
    OUTPUT FORMAT: Code only with brief integration notes. No explanations.

context:
  purpose: "Fix get_wifi_interface() to parse columnar nmcli output correctly"
  integration: "Replace method in src/apmanager.py"
  constraints:
    - "Modify only get_wifi_interface() method"
    - "Maintain all existing functionality elsewhere"

specification:
  description: "Correct nmcli device status parsing logic"
  requirements:
    functional:
      - "Parse columnar nmcli output: DEVICE TYPE STATE CONNECTION"
      - "Return first device where TYPE column equals 'wifi'"
      - "Raise InterfaceDetectionError if no wifi interface found"
      - "Raise InterfaceDetectionError on nmcli command failure"
    technical:
      language: "Python"
      version: "3.11+"

design:
  components:
    - name: "AccessPoint.get_wifi_interface"
      type: "method"
      interface:
        inputs: []
        outputs:
          type: "str"
          description: "WiFi interface name (e.g., 'wlan0')"
        raises:
          - "InterfaceDetectionError"
      logic:
        - "Execute: nmcli device status"
        - "Parse columnar output: skip header line"
        - "Split each line by whitespace"
        - "Check if column index 1 equals 'wifi'"
        - "Return column index 0 (device name)"
        - "If no match: raise InterfaceDetectionError"

implementation_details:
  current_code: |
    def get_wifi_interface(self) -> str:
        try:
            output = check_output(["nmcli", "device", "status"]).decode("utf-8")
            for line in output.splitlines():
                if "TYPE=wifi" in line:
                    return line.split()[0]
            raise InterfaceDetectionError("No WiFi interface found")
        except CalledProcessError as e:
            logger.error(f"Failed to get WiFi interface: {e}")
            traceback.print_exc()
            raise InterfaceDetectionError("Failed to get WiFi interface") from e
        except Exception as e:
            logger.critical(f"Unexpected error: {e}")
            traceback.print_exc()
            raise APManagerError("Unexpected error") from e

  corrected_code: |
    def get_wifi_interface(self) -> str:
        try:
            output = check_output(["nmcli", "device", "status"]).decode("utf-8")
            lines = output.splitlines()
            for line in lines[1:]:  # Skip header
                fields = line.split()
                if len(fields) >= 2 and fields[1] == "wifi":
                    return fields[0]
            raise InterfaceDetectionError("No WiFi interface found")
        except CalledProcessError as e:
            logger.error(f"Failed to get WiFi interface: {e}")
            traceback.print_exc()
            raise InterfaceDetectionError("Failed to get WiFi interface") from e

  changes:
    - "Replace 'TYPE=wifi' substring search with column parsing"
    - "Skip header line: lines[1:]"
    - "Check fields[1] == 'wifi' (column 2)"
    - "Remove generic exception wrapper (lines 60-63)"

error_handling:
  strategy: "Let InterfaceDetectionError propagate, remove APManagerError wrapper"
  exceptions:
    - exception: "InterfaceDetectionError"
      condition: "No wifi interface or nmcli failure"
      handling: "Propagate to caller"

testing:
  validation:
    - scenario: "nmcli output: 'DEVICE TYPE STATE\\nwlan0 wifi connected'"
      expected: "Returns 'wlan0'"
    - scenario: "nmcli output: no wifi devices"
      expected: "Raises InterfaceDetectionError"
    - scenario: "nmcli command fails"
      expected: "Raises InterfaceDetectionError"

output_format:
  structure: "method_only"
  integration_notes: "Replace get_wifi_interface() method in AccessPoint class"

deliverable:
  code: "Corrected get_wifi_interface() method only"
  documentation: "Integration: Replace method in src/apmanager.py lines 47-63"

success_criteria:
  - "Parses columnar nmcli output correctly"
  - "All 24 APManager tests pass"
  - "InterfaceDetectionError raised appropriately"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
