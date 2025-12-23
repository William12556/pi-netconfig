# T04 Prompt: Comprehensive Test Fixes

## Prompt Information

- **ID**: prompt-0014
- **Task Type**: debug
- **Source**: issue-0006 through issue-0013
- **Date**: 2025-11-27
- **Priority**: critical

## Context

Test suite shows 78 failures (53% pass rate). Root causes identified:

1. **APManager**: Mocks applied after `AccessPoint()` instantiation - subprocess calls execute before mocks active
2. **ConnectionManager**: Attempting to patch read-only `_thread.lock` attributes
3. **StateMonitor**: pytest-asyncio not configured in pyproject.toml
4. **ServiceController**: Function signature mismatches, logging handler mocking issues
5. **WebServer**: Handler instantiation triggers full HTTP protocol stack

## Specification

### Requirements

**Functional**:
- All APManager tests must mock subprocess BEFORE AccessPoint instantiation
- ConnectionManager tests verify thread-safety through actual concurrent execution
- StateMonitor async tests require pytest-asyncio configuration
- ServiceController tests match actual function signatures in main.py
- WebServer tests call handler methods directly without instantiation

**Technical**:
- Python 3.9+
- pytest framework
- unittest.mock for mocking
- pytest-asyncio for async tests

### Performance
- Tests must complete in < 5 seconds total

## Design

### Component 1: pyproject.toml Configuration

**Purpose**: Enable pytest-asyncio plugin

**Changes**:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
testpaths = ["src/tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### Component 2: APManager Test Fixtures

**Purpose**: Mock subprocess before AccessPoint creation

**Pattern**:
```python
@pytest.fixture
def mock_nmcli():
    """Mock nmcli calls before any AccessPoint instantiation."""
    with patch('subprocess.check_output') as mock:
        # Setup all return values
        device_output = b"DEVICE  TYPE  STATE\nwlan0   wifi  connected\n"
        mac_output = b"GENERAL.HWADDR:AA:BB:CC:DD:EE:FF\n"
        mock.side_effect = [device_output, mac_output]
        yield mock

def test_example(mock_nmcli):
    """Test using pre-configured mock."""
    ap = AccessPoint()  # Now mocks are already active
    assert ap.interface == "wlan0"
```

### Component 3: ConnectionManager Concurrency Tests

**Purpose**: Replace lock mocking with actual concurrent execution

**Pattern**:
```python
def test_configure_network_thread_safe(self):
    """Verify thread-safety through concurrent execution."""
    from threading import Thread
    results = []
    errors = []
    
    def worker(suffix):
        try:
            with patch('subprocess.run'), \
                 patch.object(ConfigManager, 'persist_configuration'):
                configure_network(f"SSID{suffix}", "pass123")
                results.append(suffix)
        except Exception as e:
            errors.append(e)
    
    threads = [Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) == 0
    assert len(results) == 10
```

### Component 4: ServiceController Function Signatures

**Purpose**: Match actual main.py implementation

**Required Changes**:
- `signal_handler(signum, frame)` - takes 2 args, not 3
- `register_signal_handlers()` - takes 0 args, not 1
- `graceful_shutdown(monitor)` - takes StateMonitor instance
- Remove `LOG_FILE_PATH` constant patching (doesn't exist in main.py)

### Component 5: WebServer Handler Direct Testing

**Purpose**: Test handler methods without HTTP protocol overhead

**Pattern**:
```python
def test_do_get_serves_html_for_root(self):
    """GET / returns HTML configuration page."""
    handler = ConfigHTTPHandler.__new__(ConfigHTTPHandler)
    handler.path = '/'
    handler.wfile = BytesIO()
    
    with patch.object(handler, 'send_response'), \
         patch.object(handler, 'send_header'), \
         patch.object(handler, 'end_headers'):
        handler.do_GET()
        
        handler.send_response.assert_called_with(200)
        handler.send_header.assert_any_call('Content-Type', 'text/html')
```

## Data Schema

Not applicable - test modifications only.

## Error Handling

**Strategy**: Tests verify error paths without raising exceptions

**Logging**: Test failures provide clear diagnostics

## Testing

**Unit Tests**: Self-validating - tests test themselves

**Edge Cases**:
- Concurrent access patterns
- Async timing variations
- Mock ordering dependencies

## Deliverable

### Format Requirements
- Modify test files in place
- Update pyproject.toml
- Create completion document

### Files

1. `pyproject.toml` - Add asyncio configuration
2. `src/tests/apmanager/test_apmanager.py` - Add fixture-based mocking
3. `src/tests/connectionmanager/test_connectionmanager.py` - Replace lock tests with concurrency tests
4. `src/tests/statemonitor/test_statemonitor.py` - Verify async markers work
5. `src/tests/servicecontroller/test_main.py` - Fix function signatures
6. `src/tests/servicecontroller/test_servicecontroller.py` - Fix function signatures
7. `src/tests/webserver/test_webserver.py` - Direct method testing

### Completion Document

Path: `workspace/prompt/prompt-0014-completion.md`

Required fields:
- timestamp
- files_modified: [list of paths]
- status: SUCCESS or FAILURE
- notes: [any warnings]

## Success Criteria

- pyproject.toml includes asyncio_mode = "auto"
- All APManager tests use fixtures that mock before instantiation
- ConnectionManager thread tests use actual concurrent execution
- ServiceController tests match main.py signatures
- WebServer tests call handler methods directly
- Test suite passes > 95%

## Notes

**Critical**: APManager fixture must configure ALL subprocess.check_output return values before yielding. Tests must use fixture, not inline mocking.

**Implementation Order**:
1. pyproject.toml - enables async tests immediately
2. APManager - highest failure count (24 tests)
3. ConnectionManager - simple pattern (3 tests)
4. ServiceController - signature fixes (16 tests)
5. StateMonitor - should work once pyproject.toml fixed (23 tests)
6. WebServer - method-level testing (12 tests)

---

**Metadata**:
- Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
- Template Version: 1.0
- Schema Type: t04_prompt
