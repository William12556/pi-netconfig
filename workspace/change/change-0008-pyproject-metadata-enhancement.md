# T02 Change Template v1.0 - YAML Format

```yaml
change_info:
  id: "change-0008"
  title: "Enhanced pyproject.toml Metadata"
  date: "2025-11-20"
  author: "Domain 1"
  status: "proposed"
  priority: "low"

source:
  type: "human_request"
  reference: "Audit-0001 Recommendation 11 (MP-1)"
  description: "pyproject.toml missing project.urls and project.readme fields"

scope:
  summary: "Add project.urls, readme, keywords, and classifiers to pyproject.toml"
  affected_components:
    - name: "pyproject.toml"
      file_path: "pyproject.toml"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "PyPI publication (project not intended for PyPI)"
    - "Package distribution changes"

rational:
  problem_statement: "pyproject.toml lacks standard metadata fields for repository links, readme reference, and classification"
  proposed_solution: "Add project.urls, readme, keywords, classifiers per PEP 621 specification"
  alternatives_considered:
    - option: "Leave minimal - project is system tool, not PyPI package"
      reason_rejected: "Standard metadata improves project professionalism and tooling support"
  benefits:
    - "Complete PEP 621 compliance"
    - "Better IDE/tooling integration"
    - "Clear project classification"
  risks: []

technical_details:
  current_behavior: "Minimal metadata - name, version, description, authors, license"
  proposed_behavior: "Enhanced metadata with URLs, readme, keywords, classifiers"
  implementation_approach: "Add standard PEP 621 fields"
  code_changes: []
  data_changes:
    - entity: "pyproject.toml"
      change_type: "metadata"
      details: "Add project.urls, readme, keywords, classifiers"
  interface_changes: []

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Verify pip show, setuptools compatibility"
  test_cases:
    - scenario: "pip install -e ."
      expected_result: "Installation succeeds with metadata visible"
  regression_scope:
    - "Existing pytest configuration unchanged"
  validation_criteria:
    - "Valid pyproject.toml per PEP 621"
    - "All existing functionality preserved"

implementation:
  effort_estimate: "15 minutes"
  implementation_steps:
    - step: "Add project.urls section"
      owner: "Domain 1"
    - step: "Add readme reference"
      owner: "Domain 1"
    - step: "Add keywords"
      owner: "Domain 1"
    - step: "Add classifiers"
      owner: "Domain 1"
  rollback_procedure: "Git revert"
  deployment_notes: "Metadata only - no runtime impact"

verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-0004-version-synchronization.md"
      relationship: "both_modify_pyproject"
  related_issues: []

notes: |
  Note: pi-netconfig is a system tool for Raspberry Pi, not distributed via PyPI.
  Enhanced metadata improves professionalism but is not functionally required.

version_history:
  - version: "1.0.0"
    date: "2025-11-20"
    author: "Domain 1"
    changes:
      - "Initial change document"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

---

## Proposed Changes

```toml
[project]
name = "pi-netconfig"
version = "0.2.0"
description = "Automatic WiFi configuration tool for Raspberry Pi/Debian systems"
readme = "README.md"
authors = [{name = "William Watson"}]
license = {text = "MIT"}
requires-python = ">=3.9"
keywords = ["raspberry-pi", "wifi", "network-configuration", "debian", "systemd"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: System :: Installation/Setup",
    "Topic :: System :: Networking",
]
dependencies = []

[project.urls]
Repository = "https://github.com/williamwatson/pi-netconfig"
Issues = "https://github.com/williamwatson/pi-netconfig/issues"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
