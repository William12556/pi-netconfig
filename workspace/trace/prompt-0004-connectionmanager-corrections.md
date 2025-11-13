Created: 2025 November 12

# T04 Prompt: ConnectionManager Corrections

```yaml
prompt_info:
  id: "prompt-0004"
  task_type: "debug"
  source_ref: "change-0001-connectionmanager-defect-corrections"
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
  purpose: "Correct four defects in ConnectionManager: config field usage, thread safety, error handling, directory creation"
  integration: "Replace existing src/connectionmanager.py"
  constraints:
    - "Maintain all existing functionality"
    - "Apply only specified corrections"
    - "No scope creep"

specification:
  description: "Apply corrections to resolve issues 0001-0004"
  requirements:
    functional:
      - "Same as prompt-0003 plus corrections"
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Thread-safe, comprehensive error handling, debug logging, docstrings, type hints"

design:
  architecture: "Class-based with corrections applied"
  components:
    - name: "ConfigManager"
      type: "class"
      purpose: "Apply corrections"
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
        - "CORRECTION 1: persist_configuration(ssid) - remove password parameter"
        - "CORRECTION 1: Set ap_password to 'piconfig123' always"
        - "CORRECTION 2: Add threading.Lock as class attribute"
        - "CORRECTION 2: Wrap configure_network, persist_configuration, load_configuration with lock"
        - "CORRECTION 3: subprocess.run nmcli delete with check=False"
        - "CORRECTION 4: CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True) before write"

data_schema:
  entities:
    - name: "config.json"
      attributes:
        - name: "configured_ssid"
          type: "str"
          constraints: "Last configured network"
        - name: "last_connected"
          type: "str"
          constraints: "ISO 8601 timestamp"
        - name: "ap_password"
          type: "str"
          constraints: "Always 'piconfig123'"
      validation:
        - "WiFi passwords NOT persisted, managed by NetworkManager only"

error_handling:
  strategy: "Same as original plus graceful nmcli delete handling"
  exceptions:
    - exception: "ConnectionManagerError"
      condition: "Base exception"
      handling: "Log with traceback"
    - exception: "ConfigurationError"
      condition: "Validation or application failure"
      handling: "Return error"
    - exception: "NetworkScanError"
      condition: "nmcli scan failure"
      handling: "Log, return empty list"
  logging:
    level: "DEBUG for commands, INFO for success, WARNING/ERROR for failures"
    format: "Logger 'ConnectionManager'"

testing:
  unit_tests:
    - scenario: "Configure network, verify ap_password = 'piconfig123'"
      expected: "config.json contains default AP password"
    - scenario: "Concurrent configure_network from multiple threads"
      expected: "No race conditions"
    - scenario: "Configure network with no existing profile"
      expected: "Succeeds without nmcli delete error"
    - scenario: "Configure with missing /etc/pi-netconfig/"
      expected: "Directory created, config written"
  edge_cases:
    - "No WiFi networks found"
    - "nmcli not available"
    - "Connection timeout"
    - "JSON parse error"

output_format:
  structure: "code_only"
  integration_notes: "brief"

deliverable:
  files:
    - path: "src/connectionmanager.py"
      content: "Corrected implementation"
  documentation:
    - "Integration: Replace existing file"

success_criteria:
  - "Issue-0001 resolved: ap_password always 'piconfig123'"
  - "Issue-0002 resolved: Thread-safe operations"
  - "Issue-0003 resolved: nmcli delete graceful"
  - "Issue-0004 resolved: Directory auto-created"

notes: "Apply only specified corrections. No other changes."

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

## Detailed Corrections

**CORRECTION 1 - Config Persistence (Critical):**
```python
# WRONG (Issue-0001):
def persist_configuration(ssid: str, password: str):
    config = {'configured_ssid': ssid, 'last_connected': datetime.now().isoformat(), 'ap_password': password}
    
# CORRECT:
def persist_configuration(ssid: str):
    config = {'configured_ssid': ssid, 'last_connected': datetime.now().isoformat(), 'ap_password': 'piconfig123'}
    
# Update call in configure_network:
ConfigManager.persist_configuration(ssid)  # Remove password argument
```

**CORRECTION 2 - Thread Safety (High):**
```python
# Add to ConfigManager class:
_lock = threading.Lock()

# Wrap methods:
@staticmethod
def configure_network(ssid: str, password: str) -> bool:
    with ConfigManager._lock:
        # existing logic

@staticmethod
def persist_configuration(ssid: str):
    with ConfigManager._lock:
        # existing logic
        
@staticmethod
def load_configuration() -> Optional[str]:
    with ConfigManager._lock:
        # existing logic
```

**CORRECTION 3 - nmcli Delete (Medium):**
```python
# WRONG (Issue-0003):
subprocess.run(['nmcli', 'con', 'delete', 'id', ssid], check=True)

# CORRECT:
subprocess.run(['nmcli', 'con', 'delete', 'id', ssid], check=False)
```

**CORRECTION 4 - Directory Creation (Medium):**
```python
# Add before writing config:
ConfigManager.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(ConfigManager.CONFIG_PATH, 'w') as f:
    json.dump(config, f)
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
