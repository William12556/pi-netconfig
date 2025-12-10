Created: 2025 December 04

# issue-0020-main-integration-errors.md

```yaml
issue_info:
  id: "issue-0020"
  title: "Main.py integration errors: wrong module name and missing StateMonitor arguments"
  date: "2025-12-04"
  reporter: "William Watson"
  status: "open"
  severity: "critical"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-0020"
    change_iteration: 1

source:
  origin: "user_report"
  test_ref: ""
  description: "Hardware deployment revealed two critical bugs in main.py: (1) installer generates service_controller module name instead of main, (2) StateMonitor instantiated without required arguments"

affected_scope:
  components:
    - name: "Installer"
      file_path: "src/pi_netconfig/installer.py"
    - name: "Main"
      file_path: "src/pi_netconfig/main.py"
  designs:
    - design_ref: "design-0001-installer.md"
    - design_ref: "design-0007-service-controller.md"
  version: "0.2.1"

reproduction:
  prerequisites: "Package 0.2.1 installed on Raspberry Pi"
  steps:
    - "Install service: sudo /opt/pi-netconfig/venv/bin/python -m pi_netconfig.installer --install --systemd-mode"
    - "Observe service file contains: ExecStart=/opt/pi-netconfig/venv/bin/python -m pi_netconfig.service_controller"
    - "Service fails: No module named pi_netconfig.service_controller"
    - "Manual fix: change to pi_netconfig.main"
    - "Service crashes: StateMonitor.__init__() missing 3 required positional arguments"
  frequency: "always"
  reproducibility_conditions: "Any installation on hardware"
  preconditions: "Valid venv with 0.2.1 package"
  test_data: "N/A"
  error_output: |
    Error 1: /opt/pi-netconfig/venv/bin/python: No module named pi_netconfig.service_controller
    Error 2: ERROR: Service execution failed: StateMonitor.__init__() missing 3 required positional arguments: 'connection_manager', 'ap_manager', and 'web_server'

behavior:
  expected: "Service starts, initializes all components with proper dependency order, enters operational state"
  actual: "Service fails to start due to wrong module name, then crashes on StateMonitor instantiation when module name corrected"
  impact: "Complete deployment failure. Application cannot run on hardware"
  workaround: "Manual service file edit + main.py code fix required"

environment:
  python_version: "3.13"
  os: "Debian 12 (Raspberry Pi)"
  dependencies:
    - library: "pi-netconfig"
      version: "0.2.1"
  domain: "domain_2"

analysis:
  root_cause: |
    Bug 1 - Wrong module name:
    installer.py line ~100: SystemdInstaller.generate_venv_systemd_unit() generates:
    ExecStart={venv_python} -m pi_netconfig.service_controller
    
    Should be:
    ExecStart={venv_python} -m pi_netconfig.main
    
    Actual module is main.py, not service_controller.py
    
    Bug 2 - Missing StateMonitor arguments:
    main.py line ~180: state_monitor = StateMonitor()
    
    StateMonitor.__init__ signature requires:
    def __init__(self, connection_manager: ConnectionManager, ap_manager: APManager, web_server: WebServer)
    
    main.py must:
    1. Instantiate ConnectionManager
    2. Instantiate APManager  
    3. Instantiate WebServer
    4. Pass all three to StateMonitor constructor
  technical_notes: |
    Root cause of both bugs: Code generation from outdated or incorrect design specifications.
    
    Design-0007-service-controller.md may specify wrong module name or incorrect initialization sequence.
    
    StateMonitor dependency injection requires specific initialization order per design-0004-statemonitor.md
  related_issues: []

resolution:
  assigned_to: "Claude Code"
  target_date: "2025-12-04"
  approach: |
    Fix 1 - Module name in installer.py:
    Change generate_venv_systemd_unit() to use pi_netconfig.main
    
    Fix 2 - StateMonitor initialization in main.py:
    Add proper component initialization sequence:
    1. Create ConnectionManager instance
    2. Create APManager instance  
    3. Create WebServer instance
    4. Create StateMonitor with all three dependencies
    5. Start StateMonitor.run()
  change_ref: ""
  resolved_date: ""
  resolved_by: ""
  fix_description: ""

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

prevention:
  preventive_measures: "Hardware validation before version tagging. Verify systemd service actually starts and runs on target platform"
  process_improvements: "Add integration test executing installer and verifying service startup on Raspberry Pi hardware"

verification_enhanced:
  verification_steps:
    - "Build 0.2.2 with fixes"
    - "Clean install on Raspberry Pi"
    - "Execute installer"
    - "Verify service file module name correct"
    - "Verify service starts without errors"
    - "Monitor logs for state detection"
    - "Verify 5+ minutes stable operation"
  verification_results: ""

traceability:
  design_refs:
    - "design-0001-installer.md"
    - "design-0007-service-controller.md"
    - "design-0004-statemonitor.md"
  change_refs: []
  test_refs: []

notes: |
  Critical blocker for hardware deployment.
  
  Both bugs prevent application from running on target hardware.
  
  Suggests code generation from incorrect specifications or outdated design documents.

version_history:
  - version: "1.0"
    date: "2025-12-04"
    author: "Claude Desktop"
    changes:
      - "Initial issue creation combining two related integration bugs"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-04 | Claude Desktop | Initial issue creation combining two related integration bugs |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
