Created: 2025 November 13

# T02 Change Template v1.0 - YAML Format

change_info:
  id: "change-0003"
  title: "Clarify governance framework scope as development-time only"
  date: "2025-11-13"
  author: "Domain 1"
  status: "proposed"
  priority: "critical"

source:
  type: "issue"
  reference: "workspace/audit/audit-0001-governance-compliance.md §CI-3"
  description: "Audit identified architecture non-compliance: governance specifies Domain 1/2 MCP communication model, but actual code uses standard Python imports"

scope:
  summary: "Clarify that governance framework protocols apply during development/code generation phase only, not to runtime architecture of generated applications"
  affected_components:
    - name: "governance.md"
      file_path: "governance/governance.md"
      change_type: "modify"
  affected_designs:
    - design_ref: "N/A - governance framework change"
      sections:
        - "P00 §1.1.6 Control"
        - "P00 §1.1.7 Communication"
        - "P00 §1.1.1 Purpose"
  out_of_scope:
    - "Runtime architecture of pi-netconfig application"
    - "Existing source code structure"
    - "Development workflow changes"

rational:
  problem_statement: "Governance framework describes Domain 1/2 architecture with MCP-based communication between orchestrating LLM and code-generating LLM. The pi-netconfig application implements standard monolithic Python architecture with direct module imports. This creates apparent non-compliance with P00 1.1.7, flagged as Critical Issue CI-3 in audit."
  proposed_solution: "Add explicit scope declaration to governance framework stating: (1) Domain 1/2 model applies during development phase when Claude orchestrates code generation, (2) Generated applications are self-contained and do not require MCP integration, (3) Runtime architecture is determined by design documents, not governance protocols."
  alternatives_considered:
    - option: "Refactor pi-netconfig to use MCP communication at runtime"
      reason_rejected: "Unnecessary complexity; MCP is development tool, not runtime requirement. Would add external dependency for no functional benefit."
    - option: "Rewrite governance to match monolithic architecture"
      reason_rejected: "Governance framework is correct for development process. Problem is scope ambiguity, not model incorrectness."
  benefits:
    - "Resolves CI-3 without code changes"
    - "Clarifies governance applicability"
    - "Preserves existing development workflow"
    - "Eliminates architectural confusion"
  risks:
    - risk: "May require re-auditing other projects using governance framework"
      mitigation: "One-time clarification applies to all projects retrospectively"

technical_details:
  current_behavior: "Governance P00 1.1.6-1.1.7 implies Domain 1/2 separation applies to runtime architecture, creating apparent non-compliance when generated code uses direct imports"
  proposed_behavior: "Governance explicitly states Domain 1/2 model is development-time framework; generated applications are self-contained with architecture defined in design documents"
  implementation_approach: "Add new section P00 1.1.13 'Scope and Applicability' clarifying development-time vs runtime architecture distinction"
  code_changes:
    - component: "governance.md"
      file: "governance/governance.md"
      change_summary: "Add P00 1.1.13 section, update version to 2.8"
      functions_affected:
        - "N/A - documentation only"
      classes_affected:
        - "N/A - documentation only"
  data_changes: []
  interface_changes: []

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Re-run audit verification for CI-3 compliance after governance update"
  test_cases:
    - scenario: "Audit P00 1.1.6 Control requirement"
      expected_result: "Status changes from PARTIAL to PASS with note about development-time scope"
    - scenario: "Audit P00 1.1.7 Communication requirement"
      expected_result: "Status changes from FAIL to N/A with note about runtime architecture"
  regression_scope:
    - "Verify other protocol sections remain unaffected"
  validation_criteria:
    - "CI-3 resolved in audit report"
    - "No new ambiguities introduced"

implementation:
  effort_estimate: "1 hour"
  implementation_steps:
    - step: "Add P00 1.1.13 'Scope and Applicability' to governance.md"
      owner: "Domain 1"
    - step: "Update governance version history to 2.8"
      owner: "Domain 1"
    - step: "Update audit document to reflect CI-3 resolution"
      owner: "Domain 1"
  rollback_procedure: "Revert governance.md to version 2.7 if clarification creates confusion"
  deployment_notes: "Change is documentation-only, no deployment required"

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
    - issue_ref: "audit-0001-governance-compliance.md §CI-3"
      relationship: "resolves"

notes: |
  This change addresses fundamental scope ambiguity in governance framework.
  The Domain 1/2 model correctly describes development workflow where:
  - Domain 1 (Claude) orchestrates design/test/trace document creation
  - Domain 1 generates prompts for Domain 2 (LM Studio via MCP)
  - Domain 2 generates source code following specifications
  
  However, generated applications are self-contained and do not require MCP
  integration at runtime. Runtime architecture is specified in design documents,
  not inherited from governance framework architecture.

version_history:
  - version: "1.0"
    date: "2025-11-13"
    author: "Domain 1"
    changes:
      - "Initial change document created from audit CI-3 finding"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
