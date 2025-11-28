# issue-0011-statemonitor-async-timing.md

```yaml
issue_info:
  id: "issue-0011"
  title: "StateMonitor async timing race condition in concurrent transitions"
  date: "2025-11-28"
  reporter: "Claude Desktop"
  status: "open"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-0011"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "workspace/audit/audit-0002-governance-compliance-v4.md §HP-001"
  description: "Audit identified potential async timing race condition in StateMonitor concurrent state transitions"

affected_scope:
  components:
    - name: "StateMonitor"
      file_path: "src/pi_netconfig/statemonitor.py"
  designs:
    - design_ref: "workspace/design/design-0002-domain_state-monitoring.md"
  version: "0.2.0"

reproduction:
  prerequisites: "StateMonitor in active operation with components initialized"
  steps:
    - "Multiple concurrent connection checks returning different results"
    - "Rapid state transition requests (e.g., check_connection() calls overlapping)"
    - "Concurrent calls to transition_to_client() or transition_to_ap_mode()"
  frequency: "intermittent"
  reproducibility_conditions: "High-frequency monitoring or concurrent transition requests"
  preconditions: "Async event loop with multiple concurrent tasks accessing StateMonitor"
  test_data: "N/A - timing-dependent race condition"
  error_output: |
    Potential race condition scenarios:
    1. Multiple concurrent transition attempts
    2. State change during active transition
    3. Component activation/deactivation overlap

behavior:
  expected: "State transitions execute atomically with proper coordination"
  actual: "Concurrent transitions may conflict without explicit async coordination"
  impact: |
    - Potential state corruption in edge cases
    - Component activation/deactivation conflicts
    - Inconsistent failure_count updates
    - Test suite incomplete (hypothetical test case identified)
  workaround: "Normal operation unaffected (single-threaded monitoring loop)"

environment:
  python_version: "3.9+"
  os: "Debian/Raspbian Linux"
  dependencies:
    - library: "asyncio"
      version: "stdlib"
  domain: "domain_1"

analysis:
  root_cause: |
    StateMonitor lacks explicit async locking for state transitions. While normal
    operation uses a single monitoring_loop task, the design does not prevent
    concurrent transition attempts if multiple tasks call transition methods.
    
    Specific concerns:
    1. transition_to_client() and transition_to_ap_mode() lack async coordination
    2. current_state and failure_count updates not atomic
    3. Component operations (AP activate/deactivate, web start/stop) may overlap
    
    Current implementation relies on single-task monitoring loop for serialization,
    but API does not enforce this constraint.
  technical_notes: |
    StateMonitor uses:
    - asyncio.Event for shutdown coordination (correct)
    - No asyncio.Lock for state transition coordination (missing)
    
    Potential race scenarios:
    - monitoring_loop calls transition_to_client()
    - Concurrent manual shutdown triggers transition_to_ap_mode()
    - Both transitions execute simultaneously
    
    While unlikely in current usage pattern, API design does not prevent this.
  related_issues:
    - issue_ref: "N/A"
      relationship: "First identified concurrency issue"

resolution:
  assigned_to: "Claude Code"
  target_date: "2025-11-29"
  approach: |
    Implement asyncio.Lock for state transition coordination:
    1. Add self._transition_lock = asyncio.Lock()
    2. Wrap transition_to_client() with async with self._transition_lock
    3. Wrap transition_to_ap_mode() with async with self._transition_lock
    4. Add test case test_concurrent_transition_safety to verify coordination
    5. Ensure thread-safe operation under concurrent access
  change_ref: "change-0011-statemonitor-async-coordination"
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
    - Add async concurrency test cases during initial module development
    - Review async APIs for explicit coordination mechanisms
    - Document thread-safety and concurrency assumptions in module docstrings
  process_improvements: |
    - Include concurrent access testing in P06 test strategy
    - Add concurrency review checklist to P07 quality assurance

verification_enhanced:
  verification_steps:
    - "Run test_concurrent_transition_safety with concurrent transitions"
    - "Verify no state corruption under concurrent access"
    - "Confirm component activation/deactivation serialization"
    - "Validate failure_count updates remain consistent"
  verification_results: ""

traceability:
  design_refs:
    - "workspace/design/design-0002-domain_state-monitoring.md"
  change_refs:
    - "change-0011-statemonitor-async-coordination"
  test_refs:
    - "workspace/test/test-0003-statemonitor.md"

notes: |
  Issue identified during P08 governance audit. While current single-task monitoring
  loop prevents concurrent transitions in practice, API design does not enforce this
  constraint. Adding explicit async coordination improves robustness and enables
  comprehensive concurrent testing.
  
  Priority: High due to test completeness requirement (100% pass rate for deployment).
  Impact: Low for current usage pattern (single monitoring task).

version_history:
  - version: "1.0"
    date: "2025-11-28"
    author: "Claude Desktop"
    changes:
      - "Initial issue creation from audit-0002 finding HP-001"
      - "Detailed analysis of async timing race condition"
      - "Defined resolution approach with asyncio.Lock"
```

---

**Copyright**: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
