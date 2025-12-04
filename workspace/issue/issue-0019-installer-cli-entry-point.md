Created: 2025 December 04

# issue-0019-installer-cli-entry-point.md

```yaml
issue_info:
  id: "issue-0019"
  title: "Installer missing CLI entry point for command-line invocation"
  date: "2025-12-04"
  reporter: "William Watson"
  status: "open"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-0019"
    change_iteration: 1

source:
  origin: "user_report"
  test_ref: ""
  description: "Hardware deployment revealed installer.py lacks __main__ block and CLI argument parsing, preventing documented command-line invocation pattern"

affected_scope:
  components:
    - name: "Installer"
      file_path: "src/pi_netconfig/installer.py"
  designs:
    - design_ref: "design-0001-installer.md"
  version: "0.2.0"

reproduction:
  prerequisites: "Package installed in venv on Raspberry Pi"
  steps:
    - "Execute: sudo /opt/pi-netconfig/venv/bin/python -m pi_netconfig.installer --install --systemd-mode"
    - "Observe no output or error messages"
    - "Verify service not created: sudo systemctl status pi-netconfig"
  frequency: "always"
  reproducibility_conditions: "Any attempt to invoke installer via -m flag with arguments"
  preconditions: "Valid venv with pi-netconfig package installed"
  test_data: "N/A"
  error_output: "No error - command executes silently with no effect"

behavior:
  expected: "Installer executes installation, creates systemd service, provides status output"
  actual: "Command completes immediately with no output, no service created, no errors reported"
  impact: "Documented deployment procedure fails. Users must use undocumented workaround: python -c 'from pi_netconfig.installer import install; install()'"
  workaround: "Direct function invocation via -c flag works but bypasses any CLI argument validation"

environment:
  python_version: "3.13"
  os: "Debian 12 (Raspberry Pi)"
  dependencies:
    - library: "pi-netconfig"
      version: "0.2.0"
  domain: "domain_2"

analysis:
  root_cause: "installer.py module contains only install() function definition with no __main__ block or argparse CLI. Module cannot be invoked via python -m pattern without __main__ execution entry point"
  technical_notes: |
    Current installer.py structure:
    - Defines classes: InstallerError, PrivilegeError, FileSystemError, SystemdError
    - Defines classes: InstallationDetector, VenvDetector, SystemdInstaller
    - Defines function: install() -> bool
    - Missing: if __name__ == '__main__': block
    - Missing: CLI argument parser (argparse)
    - Missing: Exit code handling based on install() return value
    
    Documentation references non-existent CLI:
    - deploy_test-guide.md §2.4 shows: sudo ./venv/bin/python -m pi_netconfig.installer --install --systemd-mode
    - This pattern requires __main__ block to process --install and --systemd-mode arguments
    
    Alternative: pyproject.toml console_scripts entry point could provide CLI without __main__ block
  related_issues: []

resolution:
  assigned_to: "Claude Code"
  target_date: "2025-12-04"
  approach: |
    Add __main__ block to installer.py with argparse CLI:
    - Accept --install flag to trigger installation
    - Accept --systemd-mode flag (for future non-systemd modes)
    - Validate flag combinations
    - Call install() function and exit with appropriate code
    
    Alternative approach: Add console_scripts entry in pyproject.toml:
    [project.scripts]
    pi-netconfig-install = "pi_netconfig.installer:main"
    
    Requires adding main() function to installer.py as CLI entry point
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
  preventive_measures: "Test documented deployment procedures on target hardware before release. Validate all -m module invocations have corresponding __main__ blocks"
  process_improvements: "Hardware validation testing should be mandatory before version tagging. Add deployment validation to test protocol"

verification_enhanced:
  verification_steps:
    - "Build package with CLI entry point"
    - "Install on Raspberry Pi in clean venv"
    - "Execute documented command: sudo ./venv/bin/python -m pi_netconfig.installer --install --systemd-mode"
    - "Verify service file created: cat /etc/systemd/system/pi-netconfig.service"
    - "Verify service enabled and started: sudo systemctl status pi-netconfig"
    - "Verify error handling: attempt installation without root privileges"
    - "Verify error handling: attempt installation outside venv"
  verification_results: ""

traceability:
  design_refs:
    - "design-0001-installer.md"
  change_refs: []
  test_refs: []

notes: |
  Deployment documentation assumes CLI functionality that does not exist in current implementation.
  
  This issue blocks hardware deployment workflow documented in deploy_test-guide.md.
  
  Version increment to 0.3.0 should accompany this fix to distinguish from broken 0.2.0.

version_history:
  - version: "1.0"
    date: "2025-12-04"
    author: "Claude Desktop"
    changes:
      - "Initial issue creation from hardware deployment failure analysis"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-04 | Claude Desktop | Initial issue creation from hardware deployment failure analysis |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
