Created: 2025 November 12

# Issue: nmcli Delete Operation Fails on Non-Existent Connection

```yaml
issue_info:
  id: "issue-0003"
  title: "configure_network() fails when deleting non-existent connection profile"
  date: "2025-11-12"
  reporter: "Domain 1"
  status: "resolved"
  severity: "medium"
  type: "defect"

source:
  origin: "code_review"
  test_ref: ""
  description: "Configuration audit identified that nmcli con delete will fail with error if connection profile does not exist, causing configure_network() to raise ConfigurationError"

affected_scope:
  components:
    - name: "ConfigManager"
      file_path: "src/connectionmanager.py"
  designs:
    - design_ref: "design-0003-connectionmanager"
  version: "Initial generation from prompt-0003"

reproduction:
  steps:
    - "Call ConfigManager.configure_network('NewNetwork', 'password123')"
    - "Observe nmcli con delete id NewNetwork fails (connection doesn't exist)"
    - "ConfigurationError raised, network configuration aborted"
  frequency: "always"
  preconditions: "First-time configuration of new network with no existing profile"
  test_data: "SSID: NewNetwork (not previously configured)"
  error_output: "subprocess.CalledProcessError from nmcli con delete"

behavior:
  expected: "configure_network() should gracefully handle deletion of non-existent profiles, continuing to create new connection"
  actual: "nmcli con delete raises CalledProcessError when profile doesn't exist, causing entire configuration to fail"
  impact: "Cannot configure new networks on first attempt - only works after one failed attempt creates profile"
  workaround: "Manually create dummy connection profile before calling configure_network()"

environment:
  python_version: "3.11+"
  os: "Raspberry Pi OS/Debian"
  dependencies:
    - library: "subprocess"
      version: "stdlib"
    - library: "NetworkManager"
      version: "system"
  domain: "domain_2"

analysis:
  root_cause: "subprocess.run(['nmcli', 'con', 'delete', 'id', ssid], check=True) raises exception when connection doesn't exist. Should use check=False or catch specific error."
  technical_notes: "nmcli con delete returns non-zero exit code when connection not found. Requires error suppression or existence check before deletion."
  related_issues: []

resolution:
  assigned_to: "Domain 2"
  target_date: "2025-11-12"
  approach: "Change subprocess.run to check=False for delete operation, or wrap in try-except catching CalledProcessError and continuing"
  change_ref: "change-0001-connectionmanager-defect-corrections"
  resolved_date: "2025-11-12"
  resolved_by: "Domain 2"
  fix_description: "Changed subprocess.run(['nmcli', 'con', 'delete', 'id', ssid], check=True) to check=False, allowing graceful handling of non-existent connection profiles."

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

notes: "Medium severity - affects first-time configuration attempts"

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
