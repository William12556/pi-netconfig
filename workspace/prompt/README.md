# Prompts

Prompt documents using T04 Prompt template for Domain 2 (Claude Code) implementation tasks.

## Sequence Notes

**Active Range**: prompt-0001 through prompt-0018
**Sequence Corrections**:
- Duplicate prompt-0012 resolved: webserver handler tests remains in closed/, logging config renumbered to prompt-0017
- Duplicate prompt-0013 resolved: servicecontroller test alignment remains in closed/, installer venv refactor renumbered to prompt-0018
- prompts-0014, 0015, 0016 exist in closed/ directory (comprehensive test fixes and async coordination work)

## Active Prompts

| ID | Title | Status | Priority | Change Ref | Effort |
|----|-------|--------|----------|------------|--------|
| [prompt-0017](prompt-0017-logging_configuration_enhancement.md) | Logging configuration enhancement | ready | medium | change-0012 | TBD |
| [prompt-0018](prompt-0018-installer-venv-refactor.md) | Installer venv deployment refactor | ready | critical | change-0013 | TBD |

## Closed Prompts

| ID | Title | Status | Priority | Change Ref | Date Executed |
|----|-------|--------|----------|------------|---------------|
| [prompt-0001](closed/prompt-0001-installer.md) | Installer module generation | completed | high | design-0005 | 2025-11-08 |
| [prompt-0002](closed/prompt-0002-statemonitor.md) | StateMonitor module generation | completed | high | design-0002 | 2025-11-08 |
| [prompt-0003](closed/prompt-0003-connectionmanager.md) | ConnectionManager module generation | completed | high | design-0003 | 2025-11-08 |
| [prompt-0004](closed/prompt-0004-apmanager.md) | APManager module generation | completed | high | design-0001 | 2025-11-08 |
| [prompt-0005](closed/prompt-0005-connectionmanager-corrections.md) | ConnectionManager defect corrections | completed | high | change-0001 | 2025-11-12 |
| [prompt-0006](closed/prompt-0006-webserver.md) | WebServer module generation | completed | high | design-0004 | 2025-11-08 |
| [prompt-0007](closed/prompt-0007-servicecontroller.md) | ServiceController module generation | completed | high | design-0006 | 2025-11-08 |
| [prompt-0008](closed/prompt-0008-test-generation.md) | Test suite generation | completed | high | design-all | 2025-11-14 |
| [prompt-0009](closed/prompt-0009-apmanager-parsing-fix.md) | APManager nmcli parsing fix | completed | critical | change-0006 | 2025-11-26 |
| [prompt-0010](closed/prompt-0010-statemonitor-test-timing.md) | StateMonitor test timing fix | completed | medium | change-0007 | 2025-11-26 |
| [prompt-0011](closed/prompt-0011-connectionmanager-thread-tests.md) | ConnectionManager thread-safety test refactor | completed | medium | change-0008 | 2025-11-26 |
| [prompt-0012](closed/prompt-0012-webserver-handler-tests.md) | WebServer handler test methodology | completed | high | change-0009 | 2025-11-26 |
| [prompt-0013](closed/prompt-0013-servicecontroller-test-alignment.md) | ServiceController test alignment | completed | high | change-0010 | 2025-11-26 |
| [prompt-0014](closed/prompt-0014-comprehensive-test-fixes.md) | Comprehensive test fixes | completed | high | change-0015 | 2025-11-26 |
| [prompt-0015](closed/prompt-0015-async-timeout-fixes.md) | Async timeout fixes | completed | high | change-0015 | 2025-11-26 |
| [prompt-0016](closed/prompt-0016-statemonitor-async-coordination.md) | StateMonitor async coordination | completed | high | change-0011 | 2025-11-26 |

## Summary Statistics

- **Total Prompts**: 18
- **Active**: 2
- **Closed**: 16
- **Critical Priority**: 1 active
- **Medium Priority**: 1 active

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
