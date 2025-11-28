# Domain 2 Test Generation Instructions

## Invocation

Execute from project root:

```bash
cd /Users/williamwatson/Documents/GitHub/pi-netconfig
claude code "Read and implement workspace/prompt/prompt-0007-test-generation.md"
```

## Expected Outputs

### Test Files (5 files in component subdirectories):

1. **src/tests/installer/test_installer.py**
   - 15 test cases covering FR-001 through FR-007
   - Installer detection, privilege checking, directory creation, systemd integration

2. **src/tests/statemonitor/test_statemonitor.py**
   - 12 test cases covering FR-010, FR-011, FR-013, FR-020, FR-021, FR-022, FR-045
   - State machine transitions, connection monitoring, component coordination

3. **src/tests/connectionmanager/test_connectionmanager.py**
   - 15 test cases covering FR-012, FR-030-034, FR-060-062
   - Connectivity testing, network scanning, configuration, thread safety

4. **src/tests/webserver/test_webserver.py**
   - 12 test cases covering FR-050 through FR-055
   - HTTP endpoints, JSON APIs, server lifecycle

5. **src/tests/servicecontroller/test_servicecontroller.py**
   - 17 test cases covering FR-023, FR-070-074
   - Entry point, execution modes, signal handling, graceful shutdown

### Total Coverage
- 71 test cases implementing all test specifications
- Minimum 80% code coverage target
- All 37 functional requirements verified

## Verification Steps

After Domain 2 completes:

1. **Check files created:**
   ```bash
   ls -la src/tests/*/test_*.py
   ```

2. **Run test suite:**
   ```bash
   cd src
   pytest tests/ -v
   ```

3. **Check coverage:**
   ```bash
   pytest tests/ --cov=. --cov-report=term-missing
   ```

4. **Verify completion document:**
   ```bash
   cat workspace/prompt/prompt-0007-completion.md
   ```

## Completion

Create **workspace/prompt/prompt-0007-completion.md** containing:

```markdown
# Test Generation Completion Report

**Timestamp:** <ISO 8601 datetime>

**Files Created:**
- src/tests/installer/test_installer.py
- src/tests/statemonitor/test_statemonitor.py  
- src/tests/connectionmanager/test_connectionmanager.py
- src/tests/webserver/test_webserver.py
- src/tests/servicecontroller/test_servicecontroller.py

**Test Cases Implemented:** 71

**Coverage Achieved:** <percentage>%

**Status:** SUCCESS

**Notes:**
- <Any warnings or observations>
- <Test execution results>
```

## Post-Completion Actions

Notify Domain 1 when complete. Domain 1 will:
1. Verify completion document indicates SUCCESS
2. Review test coverage reports
3. Update traceability matrix with test coverage
4. Update audit-0001 remediation status
5. Conduct follow-up audit verifying CI-1 resolution

---

**Date:** 2025-11-14
**Source:** prompt-0007-test-generation.md
**Audit Finding:** CI-1 - No Unit Tests (Critical)
**Governance:** P06 Test, P09 Prompt

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
