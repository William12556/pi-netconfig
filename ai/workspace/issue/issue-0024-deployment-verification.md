Created: 2025 December 05

```yaml
issue_info:
  id: "issue-0024"
  title: "Version control and deployment verification gaps"
  date: "2025-12-05"
  reporter: "William Watson"
  status: "open"
  severity: "medium"
  type: "enhancement"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

source:
  origin: "hardware validation"
  test_ref: "Hardware deployment revealed version discrepancies"
  description: "Version 0.2.5 deployed but 0.2.4 behavior observed. Need automated build verification, clean uninstall, and post-deployment version confirmation."

affected_scope:
  components:
    - name: "Build process"
      file_path: "Project root"
    - name: "Deployment process"
      file_path: "Raspberry Pi"
  designs:
    - design_ref: "N/A - deployment infrastructure"
  version: "All versions"

reproduction:
  prerequisites: "Build and deploy any version"
  steps:
    - "Build wheel on Mac: python3 -m build"
    - "Deploy to Pi: pip install --force-reinstall"
    - "Check version: pip show pi_netconfig"
    - "Check runtime: python -c 'import pi_netconfig; print(pi_netconfig.__version__)'"
    - "Observe: Version may not match, cached files persist"
  frequency: "intermittent"
  reproducibility_conditions: "When Python cache or incomplete uninstall occurs"
  preconditions: "Previous version installed"
  test_data: "N/A"
  error_output: "Version mismatch between expected and actual"

behavior:
  expected: |
    - Build verifies version consistency
    - Deployment completely removes old version
    - Post-install confirms correct version running
    - Single source of truth for version number
  actual: |
    - No build-time verification
    - --force-reinstall may leave cached files
    - No post-install verification
    - Manual version checking required
  impact: |
    - Hardware validation blocked by version uncertainty
    - Debugging complicated by version confusion
    - Deployment confidence reduced
  workaround: "Manual verification at each step"

environment:
  python_version: "3.9+ (Mac), 3.13 (Pi)"
  os: "MacOS (build), Debian 12 (deploy)"
  dependencies: []
  domain: "deployment infrastructure"

analysis:
  root_cause: |
    Three gaps in deployment infrastructure:
    
    1. Build process:
       - No automated version verification
       - Version in pyproject.toml not exported to __init__.py
       - No check that wheel filename matches pyproject.toml version
    
    2. Deployment process:
       - pip --force-reinstall may leave Python cache
       - No explicit cleanup of site-packages
       - Service not guaranteed stopped before install
    
    3. Verification:
       - No post-install version check
       - No runtime version confirmation
       - Manual checking error-prone
    
  technical_notes: |
    Best practices:
    - Single source of truth: pyproject.toml version
    - Export to __init__.py for runtime access
    - Build script verifies wheel version matches
    - Install script stops service, uninstalls cleanly, verifies result
    - Both scripts exit with error codes on failure
    
  related_issues: []

resolution:
  assigned_to: "Claude Desktop"
  target_date: "2025-12-05"
  approach: |
    Create two scripts:
    
    1. build.sh (Mac, project root):
       - Extract version from pyproject.toml
       - Update src/pi_netconfig/__init__.py with __version__
       - Clean previous builds
       - Run python3 -m build
       - Verify wheel filename matches version
       - Display build summary with version
    
    2. install.sh (Pi, project root):
       - Accept wheel filename as argument
       - Extract expected version from filename
       - Stop pi-netconfig service
       - Uninstall existing package
       - Clean site-packages cache
       - Install new wheel
       - Verify installed version matches expected
       - Start service
       - Display installation summary
    
    Both scripts:
    - Exit 0 on success, 1 on failure
    - Output clear success/failure messages
    - Idempotent (safe to run multiple times)
    
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
  preventive_measures: |
    - Always use build.sh instead of manual python3 -m build
    - Always use install.sh instead of manual pip install
    - Document scripts in deploy_test-guide.md
  process_improvements: |
    - Add version verification to CI/CD if implemented
    - Consider semantic versioning automation
    - Add changelog generation

verification_enhanced:
  verification_steps:
    - "Run ./build.sh on Mac, verify version output"
    - "Transfer wheel to Pi"
    - "Run ./install.sh pi_netconfig-X.Y.Z-py3-none-any.whl"
    - "Verify version confirmation in output"
    - "Check service logs show correct version"
    - "Test with version mismatch (expect failure)"
  verification_results: ""

traceability:
  design_refs: []
  change_refs: []
  test_refs: []

notes: |
  Scripts should be shell-based (bash) for portability.
  
  Mac build.sh requirements:
  - Extract version from pyproject.toml
  - Write to src/pi_netconfig/__init__.py
  - Build wheel
  - Verify output
  
  Pi install.sh requirements:
  - Parse version from wheel filename
  - Clean uninstall
  - Fresh install
  - Version verification
  - Service management

version_history:
  - version: "1.0"
    date: "2025-12-05"
    author: "Claude Desktop"
    changes:
      - "Initial issue creation for deployment infrastructure"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
