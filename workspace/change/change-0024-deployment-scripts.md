Created: 2025 December 05

```yaml
change_info:
  id: "change-0024"
  title: "Add automated build and deployment verification scripts"
  date: "2025-12-05"
  author: "Claude Desktop"
  status: "proposed"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-0024"
    issue_iteration: 1

source:
  type: "issue"
  reference: "workspace/issue/issue-0024-deployment-verification.md"
  description: "Add build.sh and install.sh to automate version control and deployment verification"

scope:
  summary: "Create shell scripts for Mac build and Pi deployment with version verification"
  affected_components:
    - name: "build.sh"
      file_path: "build.sh"
      change_type: "add"
    - name: "install.sh"
      file_path: "install.sh"
      change_type: "add"
    - name: "__init__.py"
      file_path: "src/pi_netconfig/__init__.py"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "CI/CD integration"
    - "Automated changelog generation"

rational:
  problem_statement: "Version discrepancies during deployment block validation. No automated verification."
  proposed_solution: "Shell scripts for consistent build/deploy with version checks"
  alternatives_considered:
    - option: "Python-based scripts"
      reason_rejected: "Shell more universal, fewer dependencies"
    - option: "Manual verification checklist"
      reason_rejected: "Error-prone, not automated"
  benefits:
    - "Automated version consistency"
    - "Clean deployment process"
    - "Reduced deployment errors"
  risks:
    - risk: "Scripts require bash"
      mitigation: "Standard on Mac and Debian"

technical_details:
  current_behavior: "Manual build and pip install --force-reinstall"
  proposed_behavior: "Automated build.sh and install.sh with verification"
  implementation_approach: |
    build.sh:
    1. Extract version from pyproject.toml
    2. Update __init__.py with __version__
    3. Clean previous builds
    4. Execute python3 -m build
    5. Verify wheel filename
    
    install.sh:
    1. Parse version from wheel filename
    2. Stop service
    3. Uninstall existing package
    4. Clear site-packages cache
    5. Install new wheel
    6. Verify installed version
    7. Start service
  code_changes:
    - component: "build.sh"
      file: "build.sh"
      change_summary: "New build automation script"
      functions_affected: []
      classes_affected: []
    - component: "install.sh"
      file: "install.sh"
      change_summary: "New deployment automation script"
      functions_affected: []
      classes_affected: []
    - component: "__init__.py"
      file: "src/pi_netconfig/__init__.py"
      change_summary: "Add __version__ export"
      functions_affected: []
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal: []
  external:
    - "grep, cut, sed (standard Unix tools)"
  required_changes: []

testing_requirements:
  test_approach: "Execute scripts and verify version consistency"
  test_cases:
    - scenario: "Fresh build"
      expected_result: "Wheel created, version matches pyproject.toml"
    - scenario: "Fresh install"
      expected_result: "Service running, version verified"
    - scenario: "Version mismatch"
      expected_result: "Script exits with error"
  regression_scope:
    - "Manual build still works"
    - "Manual install still works"
  validation_criteria:
    - "build.sh exits 0 on success"
    - "install.sh exits 0 on success"
    - "Runtime version matches pyproject.toml"

implementation:
  effort_estimate: "1 hour"
  implementation_steps:
    - step: "Create build.sh with version extraction and verification"
      owner: "Claude Desktop"
    - step: "Create install.sh with clean uninstall and verification"
      owner: "Claude Desktop"
    - step: "Update __init__.py to export __version__"
      owner: "Claude Desktop"
    - step: "Update deploy_test-guide.md with script usage"
      owner: "Claude Desktop"
  rollback_procedure: "Delete scripts, use manual process"
  deployment_notes: "Scripts executable, version 0.2.6"

verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []

traceability:
  design_updates: []
  related_changes: []
  related_issues:
    - issue_ref: "issue-0024"
      relationship: "resolves"

notes: |
  Scripts simplify deployment workflow and prevent version confusion.
  Both are idempotent and safe to run multiple times.

version_history:
  - version: "1.0"
    date: "2025-12-05"
    author: "Claude Desktop"
    changes:
      - "Initial change specification for deployment scripts"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
