# prompt-0016-instructions.md

## Claude Code Invocation Command

```bash
cd /Users/williamwatson/Documents/GitHub/pi-netconfig && claude workspace/prompt/prompt-0016-statemonitor-async-coordination.md
```

## Expected Outputs

**Modified Files:**
- `src/pi_netconfig/statemonitor.py` - Add asyncio.Lock coordination
- `src/tests/statemonitor/test_statemonitor.py` - Add concurrent safety test

**Completion Document:**
- `workspace/prompt/prompt-0016-completion.md`

## Verification

After Claude Code completes:
1. Review completion document for SUCCESS status
2. Run test suite: `cd src && pytest tests/statemonitor/test_statemonitor.py -v`
3. Verify all 165 tests pass (164 existing + 1 new)
4. Notify Claude Desktop for audit verification

---

**Copyright**: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
