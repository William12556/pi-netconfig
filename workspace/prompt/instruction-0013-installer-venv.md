---
instruction_info:
  id: instruction-0013
  date: 2025-12-03
  author: William Watson
  prompt_ref: prompt-0013-installer-venv-refactor.md
  status: ready
---

Created: 2025 December 03

# Claude Code Execution Instructions - Installer Venv Refactor

## Objective

Refactor `src/pi_netconfig/installer.py` to support venv-based package deployment instead of script-based deployment.

## Context

Current installer fails silently when executed from pip-installed package in venv because it expects script files at `__file__` location. Package deployment requires detecting venv context and generating systemd unit that executes venv Python with module flag.

## Execution Steps

### 1. Environment Setup

```bash
cd /Users/williamwatson/Documents/GitHub/pi-netconfig
source venv/bin/activate
```

### 2. Read Specifications

Read the complete prompt document:
```bash
claude --print "Read /Users/williamwatson/Documents/GitHub/pi-netconfig/workspace/prompt/prompt-0013-installer-venv-refactor.md and summarize the key requirements"
```

### 3. Code Generation

Execute refactoring with direct file output:
```bash
claude --print "Following prompt-0013-installer-venv-refactor.md specifications, refactor src/pi_netconfig/installer.py to support venv-based package deployment. Save directly to src/pi_netconfig/installer.py."
```

### 4. Test Execution

Run unit tests to verify implementation:
```bash
pytest tests/unit/test_installer.py -v
```

Expected: All tests pass or clear indication of required test updates.

### 5. Create Completion Document

```bash
claude --print "Create completion document at workspace/prompt/prompt-0013-completion.md with timestamp, files_created list, status (SUCCESS/FAILURE), and implementation notes"
```

### 6. Verification

Verify generated code contains:
- VenvDetector class with is_venv(), get_venv_python(), validate_package_installed()
- SystemdInstaller.generate_venv_systemd_unit(venv_python: Path)
- Removed copy_application() method
- Updated install() with venv validation
- Systemd ExecStart: `{venv_python} -m pi_netconfig.service_controller`

```bash
grep -n "class VenvDetector" src/pi_netconfig/installer.py
grep -n "generate_venv_systemd_unit" src/pi_netconfig/installer.py
grep -n "copy_application" src/pi_netconfig/installer.py  # Should return no results
grep -n "ExecStart.*-m pi_netconfig.service_controller" src/pi_netconfig/installer.py
```

## Critical Requirements

1. **No script file operations** - Remove all `copy_application()` logic
2. **Venv validation** - Fail fast with clear errors if not in venv
3. **Module execution** - Systemd unit must use `-m pi_netconfig.service_controller`
4. **Absolute paths** - Venv Python path from `sys.executable`
5. **Rollback cleanup** - Remove only service file, not directories

## Success Criteria

- [ ] VenvDetector class fully implemented
- [ ] SystemdInstaller refactored for venv deployment
- [ ] install() function validates venv context
- [ ] No references to copy_application() or script paths
- [ ] Unit tests pass or updated appropriately
- [ ] Completion document created

## Deliverables

1. Refactored `src/pi_netconfig/installer.py`
2. Completion document `workspace/prompt/prompt-0013-completion.md`
3. Updated unit tests if necessary

## Notes

This resolves critical deployment blocker issue-0013. Hardware validation cannot proceed until installer works with pip-installed packages in venv.

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
