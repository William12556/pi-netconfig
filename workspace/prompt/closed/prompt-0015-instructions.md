# Claude Code Execution Instructions: prompt-0015

## Command

```bash
cd /Users/williamwatson/Documents/GitHub/pi-netconfig && claude workspace/prompt/prompt-0015-async-timeout-fixes.md
```

## Expected Outputs

**Modified Files**:
1. `src/tests/servicecontroller/test_main.py`
2. `src/tests/servicecontroller/test_servicecontroller.py`
3. `src/tests/statemonitor/test_statemonitor.py`

**Completion Document**: `workspace/prompt/prompt-0015-completion.md`

## Verification

```bash
pytest src/tests/servicecontroller/ src/tests/statemonitor/ -v --tb=short
```

Expected: All tests complete within 5 seconds, no hangs

---

Created: 2025-11-27
