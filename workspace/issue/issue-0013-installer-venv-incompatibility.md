issue_info:
  id: issue-0013
  title: Installer incompatible with venv-based package deployment
  date: 2025-12-03
  reporter: William Watson
  status: open
  severity: critical
  type: defect
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

source:
  origin: user_report
  test_ref: ""
  description: Hardware deployment testing on Raspberry Pi revealed installer module fails silently when package installed via pip in virtual environment

affected_scope:
  components:
    - name: Installer
      file_path: src/pi_netconfig/installer.py
  designs:
    - design_ref: design-0001-component_installer.md
  version: "0.2.0"

reproduction:
  prerequisites: "Raspberry Pi with NetworkManager, Python 3.9+, package built as wheel"
  steps:
    - "Create venv: sudo python3 -m venv /opt/pi-netconfig/venv"
    - "Install package: sudo /opt/pi-netconfig/venv/bin/pip install pi_netconfig-*.whl"
    - "Run installer: sudo /opt/pi-netconfig/venv/bin/python -m pi_netconfig.installer --install --systemd-mode"
    - "Check service: sudo systemctl status pi-netconfig"
  frequency: "always"
  reproducibility_conditions: "Any venv-based package installation"
  preconditions: "Package installed in venv at /opt/pi-netconfig/venv/"
  test_data: "pi_netconfig-0.2.0-py3-none-any.whl"
  error_output: |
    Exit code: 5 (silent failure)
    No systemd service file created at /etc/systemd/system/pi-netconfig.service
    No error messages printed to stdout/stderr

behavior:
  expected: "Installer detects venv installation, generates systemd unit executing venv Python with package module, creates service file, enables and starts service"
  actual: "Installer exits silently with code 5, no service file created, no error messages"
  impact: "Complete deployment failure - application cannot be installed on target hardware"
  workaround: "None - installer fundamentally incompatible with packaging workflow"

environment:
  python_version: "3.11.2"
  os: "Debian GNU/Linux 12 (bookworm)"
  dependencies:
    - library: "NetworkManager"
      version: "1.42.4"
  domain: "domain_2"

analysis:
  root_cause: |
    Installer designed for script-based deployment, predates Python packaging implementation:
    
    1. InstallationDetector.get_current_script_path() returns None when module executed via -m flag
    2. SystemdInstaller.copy_application() expects script file to copy to /usr/local/bin/pi-netconfig/main.py
    3. SystemdInstaller.generate_systemd_unit() hardcodes ExecStart=/usr/bin/python3 /usr/local/bin/pi-netconfig/main.py
    4. Design assumes script files, not installed packages in site-packages
    
    When package installed in venv:
    - No script file at installer.__file__ (returns None)
    - Package at /opt/pi-netconfig/venv/lib/python3.11/site-packages/pi_netconfig/
    - Systemd unit must execute: /opt/pi-netconfig/venv/bin/python -m pi_netconfig.service_controller
    
    Current design incompatible with:
    - Python packaging standards (pyproject.toml, pip install)
    - Virtual environment deployment
    - Debian PEP 668 externally-managed-environment policy
  technical_notes: |
    Package __file__ attribute returns None when module executed as script via python -m.
    
    Correct venv detection approach:
    - sys.prefix != sys.base_prefix indicates venv active
    - sys.executable provides path to venv Python interpreter
    
    Systemd unit ExecStart must reference venv Python absolute path and module execution.
  related_issues: []

resolution:
  assigned_to: "Claude Code"
  target_date: "2025-12-03"
  approach: |
    Redesign installer for venv-based package deployment:
    
    1. Detect venv: Check sys.prefix != sys.base_prefix
    2. Get venv paths: Use sys.executable for Python, sys.prefix for venv root
    3. Remove script copy operation: Package already in site-packages
    4. Generate systemd unit with venv-aware ExecStart:
       ExecStart={sys.executable} -m pi_netconfig.service_controller
    5. Remove rollback of /usr/local/bin/pi-netconfig (no longer created)
    6. Update logging to show venv detection and paths
  change_ref: "change-0013"
  resolved_date: ""
  resolved_by: ""
  fix_description: ""

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

prevention:
  preventive_measures: "Hardware validation testing during initial development phase would have detected incompatibility before design finalization"
  process_improvements: "Include target platform deployment validation in test protocol before closing design documents"

verification_enhanced:
  verification_steps:
    - "Build package: python3 -m build"
    - "Transfer to Pi: scp dist/*.whl admin@deb1:/tmp/"
    - "Create venv on Pi: sudo python3 -m venv /opt/pi-netconfig/venv"
    - "Install in venv: sudo /opt/pi-netconfig/venv/bin/pip install /tmp/pi_netconfig-*.whl"
    - "Run installer: sudo /opt/pi-netconfig/venv/bin/python -m pi_netconfig.installer --install --systemd-mode"
    - "Verify service file created: ls -l /etc/systemd/system/pi-netconfig.service"
    - "Verify ExecStart uses venv Python: grep ExecStart /etc/systemd/system/pi-netconfig.service"
    - "Verify service starts: sudo systemctl start pi-netconfig && sudo systemctl status pi-netconfig"
    - "Verify state detection: sudo journalctl -u pi-netconfig -n 50 | grep 'State:'"
  verification_results: ""

traceability:
  design_refs:
    - "design-0000-master_pi-netconfig.md"
    - "design-0001-component_installer.md"
  change_refs: []
  test_refs: []

notes: |
  Critical deployment blocker. All hardware validation testing blocked until resolved.
  
  Deployment guide (docs/deploy_test-guide.md) documents correct venv-based procedure but installer implementation incompatible.

version_history:
  - version: "1.0"
    date: "2025-12-03"
    author: "William Watson"
    changes:
      - "Initial issue creation from hardware deployment failure"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
