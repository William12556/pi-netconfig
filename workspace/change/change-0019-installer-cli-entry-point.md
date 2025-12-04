Created: 2025 December 04

# change-0019-installer-cli-entry-point.md

```yaml
change_info:
  id: "change-0019"
  title: "Add CLI entry point to installer module"
  date: "2025-12-04"
  author: "Claude Desktop"
  status: "proposed"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0019"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-0019-installer-cli-entry-point.md"
  description: "Hardware deployment revealed missing __main__ block prevents documented CLI invocation pattern"

scope:
  summary: "Add __main__ block with argparse CLI to installer.py enabling python -m pi_netconfig.installer invocation"
  affected_components:
    - name: "Installer"
      file_path: "src/pi_netconfig/installer.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-0001-installer.md"
      sections:
        - "§3.7 CLI Interface (new)"
  out_of_scope:
    - "Console scripts entry point in pyproject.toml (alternative approach deferred)"
    - "Uninstallation CLI commands"
    - "Configuration management CLI commands"

rational:
  problem_statement: "Installer module cannot be invoked via python -m pattern. Documented deployment command 'sudo ./venv/bin/python -m pi_netconfig.installer --install --systemd-mode' executes silently with no effect. Users must use undocumented workaround with -c flag"
  proposed_solution: "Add __main__ block to installer.py with argparse-based CLI. Accept --install and --systemd-mode flags. Provide clear success/failure output. Exit with appropriate status codes"
  alternatives_considered:
    - option: "Console scripts entry point via pyproject.toml [project.scripts]"
      reason_rejected: "Requires additional main() wrapper function and command name decision. __main__ approach simpler and directly addresses documented invocation pattern"
    - option: "Interactive installation wizard"
      reason_rejected: "Overengineering. Systemd installation is single-purpose operation requiring only execution trigger"
  benefits:
    - "Enables documented deployment procedure without modification"
    - "Provides user feedback during installation process"
    - "Standard Python CLI pattern (-m module invocation)"
    - "Exit codes enable scripted deployment verification"
  risks:
    - risk: "Argument parsing overhead minimal compared to actual installation work"
      mitigation: "N/A - overhead negligible"

technical_details:
  current_behavior: "Module defines install() function but lacks execution entry point. Python -m invocation loads module but executes nothing"
  proposed_behavior: "Module loads and executes __main__ block. Parses arguments, validates flags, calls install(), exits with status code"
  implementation_approach: |
    Add __main__ block at end of installer.py:
    
    1. Import argparse and sys modules
    2. Create ArgumentParser with description
    3. Add --install action flag (store_true)
    4. Add --systemd-mode action flag (store_true)
    5. Parse arguments
    6. Validate flag combination (both required)
    7. Call install() function
    8. Exit with code 0 on success, 1 on failure
    9. Print clear status messages
    
    Status output examples:
    - Success: "Installation complete. Service enabled and started."
    - Failure: "Installation failed. See errors above."
    - Invalid args: "Error: Both --install and --systemd-mode required."
  code_changes:
    - component: "Installer"
      file: "src/pi_netconfig/installer.py"
      change_summary: "Add __main__ block with argparse CLI at end of file"
      functions_affected:
        - "install() - called from __main__ block"
      classes_affected: []
  data_changes: []
  interface_changes:
    - interface: "CLI invocation pattern"
      change_type: "signature"
      details: "New CLI interface: python -m pi_netconfig.installer --install --systemd-mode"
      backward_compatible: "yes - existing direct import usage unaffected"

dependencies:
  internal: []
  external:
    - library: "argparse"
      version_change: "stdlib - no version constraint"
      impact: "None - standard library module"
  required_changes: []

testing_requirements:
  test_approach: "Hardware validation on Raspberry Pi. Unit tests for argument parsing (optional - low value given simple logic)"
  test_cases:
    - scenario: "Valid invocation with both flags"
      expected_result: "Installation executes, success message printed, exit code 0"
    - scenario: "Missing --install flag"
      expected_result: "Error message, usage help, exit code 2"
    - scenario: "Missing --systemd-mode flag"
      expected_result: "Error message, usage help, exit code 2"
    - scenario: "No flags provided"
      expected_result: "Error message, usage help, exit code 2"
    - scenario: "Installation failure (no root)"
      expected_result: "Error message from install(), exit code 1"
  regression_scope:
    - "Existing direct import usage: from pi_netconfig.installer import install"
    - "ServiceController auto-installation invocation"
  validation_criteria:
    - "Documented deployment command executes successfully"
    - "Service file created and enabled"
    - "Clear user feedback provided"
    - "Appropriate exit codes returned"

implementation:
  effort_estimate: "1 hour"
  implementation_steps:
    - step: "Add __main__ block to installer.py"
      owner: "Claude Code"
    - step: "Test on Raspberry Pi hardware"
      owner: "Human"
    - step: "Update design-0001-installer.md with CLI section"
      owner: "Claude Desktop"
  rollback_procedure: "Revert installer.py to previous version. __main__ block is additive, no breaking changes"
  deployment_notes: "Version 0.2.1 includes this fix. Rebuild and redeploy to Pi"

verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []

traceability:
  design_updates:
    - design_ref: "design-0001-installer.md"
      sections_updated:
        - "§3.7 CLI Interface (new section)"
      update_date: ""
  related_changes: []
  related_issues:
    - issue_ref: "issue-0019"
      relationship: "resolves"

notes: |
  This is a simple additive change. Existing functionality unaffected.
  
  Future enhancement: Add --help and --version flags for completeness.

version_history:
  - version: "1.0"
    date: "2025-12-04"
    author: "Claude Desktop"
    changes:
      - "Initial change document creation from issue-0019"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-04 | Claude Desktop | Initial change document creation from issue-0019 |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
