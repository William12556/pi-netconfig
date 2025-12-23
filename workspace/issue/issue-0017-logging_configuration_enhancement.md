# Issue-0012: Logging Configuration Enhancement

Created: 2025-12-03

---

## Table of Contents

- [Issue Information](<#issue information>)
- [Source](<#source>)
- [Affected Scope](<#affected scope>)
- [Reproduction](<#reproduction>)
- [Behavior](<#behavior>)
- [Environment](<#environment>)
- [Analysis](<#analysis>)
- [Resolution](<#resolution>)
- [Verification](<#verification>)
- [Prevention](<#prevention>)
- [Traceability](<#traceability>)
- [Version History](<#version history>)

---

## Issue Information

```yaml
issue_info:
  id: "issue-0012"
  title: "Logging Configuration Enhancement"
  date: "2025-12-03"
  reporter: "Human"
  status: "open"
  severity: "medium"
  type: "enhancement"
  iteration: 1
  coupled_docs:
    change_ref: "change-0012"
    change_iteration: null
```

[Return to Table of Contents](<#table of contents>)

---

## Source

```yaml
source:
  origin: "human_request"
  test_ref: ""
  description: "Request for configurable logging with debug/normal modes, rotation policy, and flat file format"
```

**Description:**

Current logging lacks:
1. Configurable log levels for service vs test execution
2. Log rotation policy (disk exhaustion risk)
3. Clear debug/normal mode separation

[Return to Table of Contents](<#table of contents>)

---

## Affected Scope

```yaml
affected_scope:
  components:
    - name: "ServiceController"
      file_path: "src/pi_netconfig/main.py"
  designs:
    - design_ref: "design-0000-master_pi-netconfig"
  version: "0.1.0"
```

[Return to Table of Contents](<#table of contents>)

---

## Reproduction

```yaml
reproduction:
  prerequisites: "Pi-netconfig installed"
  steps:
    - "Run service in production"
    - "Observe unbounded log growth"
    - "No runtime debug toggle"
  frequency: "always"
  reproducibility_conditions: "Normal operation"
  preconditions: "Service running"
  test_data: "N/A"
  error_output: "N/A"
```

[Return to Table of Contents](<#table of contents>)

---

## Behavior

```yaml
behavior:
  expected: "Configurable log levels (debug/normal), automatic rotation, environment variable control"
  actual: "Fixed log level, no rotation, no runtime configuration"
  impact: "Cannot toggle debug logging, risk of disk exhaustion"
  workaround: "Manual log file management"
```

[Return to Table of Contents](<#table of contents>)

---

## Environment

```yaml
environment:
  python_version: "3.9+"
  os: "Debian (Raspberry Pi OS)"
  dependencies:
    - library: "logging"
      version: "stdlib"
    - library: "logging.handlers"
      version: "stdlib"
  domain: "domain_1"
```

[Return to Table of Contents](<#table of contents>)

---

## Analysis

```yaml
analysis:
  root_cause: "Logging configuration lacks environment-based control and rotation"
  technical_notes: "Need RotatingFileHandler and PI_NETCONFIG_DEBUG environment variable"
  related_issues: []
```

**Root Cause:**

`configure_logging()` in `main.py` uses basic `FileHandler` without rotation and no environment variable checks.

[Return to Table of Contents](<#table of contents>)

---

## Resolution

```yaml
resolution:
  assigned_to: "Claude Code"
  target_date: "2025-12-03"
  approach: "Modify configure_logging() for environment-based control and rotation"
  change_ref: "change-0012"
  resolved_date: ""
  resolved_by: ""
  fix_description: ""
```

**Approach:**

1. Add `PI_NETCONFIG_DEBUG` environment variable (default: true)
2. Implement `RotatingFileHandler`: 10MB max, 3 backups
3. Debug mode: logs INFO and ERROR
4. Normal mode: logs INFO only (filter ERROR)
5. Format: `timestamp level logger message`

[Return to Table of Contents](<#table of contents>)

---

## Verification

```yaml
verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""
```

**Verification Steps:**

1. Test `PI_NETCONFIG_DEBUG=true` - INFO and ERROR logged
2. Test `PI_NETCONFIG_DEBUG=false` - INFO only logged
3. Verify rotation at 10MB
4. Confirm backup files (.1, .2, .3)
5. Verify log format

[Return to Table of Contents](<#table of contents>)

---

## Prevention

```yaml
prevention:
  preventive_measures: "Document environment variable in README and systemd service template"
  process_improvements: "Add logging configuration to design specifications"
```

[Return to Table of Contents](<#table of contents>)

---

## Traceability

```yaml
traceability:
  design_refs:
    - "design-0000-master_pi-netconfig"
  change_refs:
    - "change-0012"
  test_refs: []
```

[Return to Table of Contents](<#table of contents>)

---

## Notes

Implements proposal-0001-logging_enhancement.md per human requirements.

---

## Version History

| Version | Date       | Author | Changes                  |
|---------|------------|--------|--------------------------|
| 1.0     | 2025-12-03 | Claude | Initial issue creation   |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
