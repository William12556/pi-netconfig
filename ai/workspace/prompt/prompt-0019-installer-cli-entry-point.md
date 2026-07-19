Created: 2025 December 04

# prompt-0019-installer-cli-entry-point.md

```yaml
prompt_info:
  id: "prompt-0019"
  task_type: "code_generation"
  source_ref: "change-0019-installer-cli-entry-point.md"
  date: "2025-12-04"
  priority: "high"
  iteration: 1
  coupled_docs:
    change_ref: "change-0019"
    change_iteration: 1

context:
  purpose: "Add CLI entry point to installer.py enabling python -m invocation pattern"
  integration: "Existing install() function called from new __main__ block. No changes to ServiceController auto-installation workflow"
  knowledge_references: []
  constraints:
    - "Preserve all existing functionality"
    - "No breaking changes to direct import usage"
    - "Standard library only (argparse)"

specification:
  description: "Add __main__ block with argparse CLI to installer.py supporting --install and --systemd-mode flags"
  requirements:
    functional:
      - "Accept --install flag (required)"
      - "Accept --systemd-mode flag (required)"
      - "Validate both flags present"
      - "Call existing install() function"
      - "Print status messages"
      - "Exit with appropriate codes: 0 (success), 1 (install failure), 2 (arg error)"
    technical:
      language: "Python"
      version: "3.9+"
      standards:
        - "Use argparse for CLI"
        - "Preserve thread safety (N/A for __main__)"
        - "Add comprehensive error handling"
        - "Include docstrings for main() if created"
  performance:
    - target: "Negligible overhead"
      metric: "Argument parsing < 1ms"

design:
  architecture: "Add __main__ block at end of existing installer.py"
  components:
    - name: "__main__ block"
      type: "module execution entry"
      purpose: "Parse CLI arguments and invoke install()"
      interface:
        inputs:
          - name: "sys.argv"
            type: "list[str]"
            description: "Command line arguments"
        outputs:
          type: "int"
          description: "Exit code via sys.exit()"
        raises:
          - "SystemExit (via argparse or sys.exit)"
      logic:
        - "Import argparse, sys at top if not already present"
        - "Create ArgumentParser with description"
        - "Add --install argument (action='store_true', required=True)"
        - "Add --systemd-mode argument (action='store_true', required=True)"
        - "Parse args"
        - "Validate both flags present (argparse handles via required=True)"
        - "Call install() function"
        - "On success: print 'Installation complete. Service enabled and started.', exit 0"
        - "On failure: print 'Installation failed. See errors above.', exit 1"
  dependencies:
    internal:
      - "install() function"
      - "Existing exception classes"
    external:
      - "argparse (stdlib)"
      - "sys (stdlib)"

data_schema:
  entities: []

error_handling:
  strategy: "Catch install() exceptions, print user-friendly message, exit 1. Let argparse handle invalid arguments (exits 2)"
  exceptions:
    - exception: "Any exception from install()"
      condition: "Installation failure"
      handling: "Print failure message, exit 1"
  logging:
    level: "INFO"
    format: "Simple print statements to stdout/stderr"

testing:
  unit_tests:
    - scenario: "Valid flags provided"
      expected: "install() called, success message, exit 0"
    - scenario: "Missing flags"
      expected: "Argparse error, exit 2"
  edge_cases:
    - "Installation failure scenarios (handled by install() function)"
  validation:
    - "Hardware validation on Raspberry Pi"

deliverable:
  format_requirements:
    - "Modify existing src/pi_netconfig/installer.py"
    - "Add __main__ block at end of file"
    - "Preserve all existing code unchanged"
  files:
    - path: "src/pi_netconfig/installer.py"
      content: "Add __main__ block only"

success_criteria:
  - "Command 'python -m pi_netconfig.installer --install --systemd-mode' executes successfully"
  - "Appropriate exit codes returned"
  - "User feedback messages clear"
  - "Existing direct import usage unaffected"

notes: |
  Implementation example:
  
  ```python
  if __name__ == '__main__':
      import argparse
      import sys
      
      parser = argparse.ArgumentParser(
          description='Pi-Netconfig installer - systemd service installation'
      )
      parser.add_argument('--install', action='store_true', required=True,
                          help='Execute installation')
      parser.add_argument('--systemd-mode', action='store_true', required=True,
                          help='Install as systemd service')
      
      args = parser.parse_args()
      
      try:
          result = install()
          if result:
              print('Installation complete. Service enabled and started.')
              sys.exit(0)
          else:
              print('Installation failed. See errors above.')
              sys.exit(1)
      except Exception as e:
          print(f'Installation failed: {e}')
          sys.exit(1)
  ```

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-04 | Claude Desktop | Initial prompt creation from change-0019 |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
