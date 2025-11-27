# Claude Code Execution Instructions: prompt-0014

## Command

```bash
cd /Users/williamwatson/Documents/GitHub/pi-netconfig && claude workspace/prompt/prompt-0014-comprehensive-test-fixes.md
```

## Expected Outputs

**Modified Files**:
1. `pyproject.toml`
2. `src/tests/apmanager/test_apmanager.py`
3. `src/tests/connectionmanager/test_connectionmanager.py`
4. `src/tests/statemonitor/test_statemonitor.py`
5. `src/tests/servicecontroller/test_main.py`
6. `src/tests/servicecontroller/test_servicecontroller.py`
7. `src/tests/webserver/test_webserver.py`

**Completion Document**: `workspace/prompt/prompt-0014-completion.md`

## Verification

After completion, run:
```bash
pytest src/tests/ -v
```

Expected: >95% pass rate (157+/165 tests)

---

Created: 2025-11-27
