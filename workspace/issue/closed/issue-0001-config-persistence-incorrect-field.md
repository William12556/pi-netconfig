Created: 2025 November 12

# Issue: Config Persistence - Incorrect Field Usage

```yaml
issue_info:
  id: "issue-0001"
  title: "Configuration persistence stores WiFi password in wrong JSON field"
  date: "2025-11-12"
  reporter: "Domain 1"
  status: "resolved"
  severity: "critical"
  type: "defect"

source:
  origin: "code_review"
  test_ref: ""
  description: "Configuration audit identified that persist_configuration() stores WiFi network password in 'ap_password' field instead of keeping default AP password"

affected_scope:
  components:
    - name: "ConfigManager"
      file_path: "src/connectionmanager.py"
  designs:
    - design_ref: "design-0003-connectionmanager"
  version: "Initial generation from prompt-0003"

reproduction:
  steps:
    - "Call ConfigManager.configure_network('TestNet', 'password123')"
    - "Examine /etc/pi-netconfig/config.json"
    - "Observe WiFi password stored in ap_password field"
  frequency: "always"
  preconditions: "ConfigManager instantiated and configure_network called"
  test_data: "SSID: TestNet, Password: password123"
  error_output: "No error - logic defect"

behavior:
  expected: "config.json should contain configured_ssid, last_connected timestamp, and ap_password defaulting to 'piconfig123'. WiFi passwords should not be persisted."
  actual: "config.json stores WiFi password in ap_password field, overwriting default AP password"
  impact: "AP mode will use WiFi password instead of default 'piconfig123', breaking access point functionality"
  workaround: "None - requires code correction"

environment:
  python_version: "3.11+"
  os: "Raspberry Pi OS/Debian"
  dependencies:
    - library: "subprocess"
      version: "stdlib"
    - library: "json"
      version: "stdlib"
  domain: "domain_2"

analysis:
  root_cause: "persist_configuration() method signature accepts password parameter and stores it in ap_password field. Per design specification, ap_password should store default AP password only."
  technical_notes: "Line: config = {'configured_ssid': ssid, 'last_connected': datetime.now().isoformat(), 'ap_password': password}. The password parameter should not be used for ap_password field."
  related_issues: []

resolution:
  assigned_to: "Domain 2"
  target_date: "2025-11-12"
  approach: "Remove password parameter from persist_configuration(). Set ap_password to default 'piconfig123'. WiFi credentials managed by NetworkManager, not persisted to JSON."
  change_ref: "change-0001-connectionmanager-defect-corrections"
  resolved_date: "2025-11-12"
  resolved_by: "Domain 2"
  fix_description: "Modified persist_configuration signature to remove password parameter. Changed config dictionary to set ap_password to 'piconfig123'. Updated configure_network call to pass only ssid parameter."

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

traceability:
  design_refs:
    - "design-0003-connectionmanager"
  change_refs: []
  test_refs: []

notes: "Critical defect - AP mode will fail if WiFi password overwrites default AP password"

version_history:
  - version: "1.0"
    date: "2025-11-12"
    author: "Domain 1"
    changes:
      - "Initial issue creation from configuration audit"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
