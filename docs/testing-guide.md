Created: 2024 November 30

# Testing Guide

## Table of Contents

- [Overview](<#overview>)
- [Test Classifications](<#test classifications>)
- [Test Execution Platforms](<#test execution platforms>)
- [Testing Workflow](<#testing workflow>)
- [Mocking Strategy](<#mocking strategy>)
- [Test Organization](<#test organization>)
- [Progressive Validation](<#progressive validation>)
- [Platform-Specific Procedures](<#platform-specific procedures>)
- [Coverage Requirements](<#coverage requirements>)

[Return to Table of Contents](<#table of contents>)

## Overview

The pi-netconfig project employs a comprehensive testing strategy that accommodates cross-platform development: code generation and unit testing on MacOS, deployment and system testing on Raspberry Pi. This guide defines test classifications, execution platforms, and validation workflows.

**Key Principle**: Unit tests verify component behavior through mocking; integration and system tests validate actual hardware interaction.

[Return to Table of Contents](<#table of contents>)

## Test Classifications

### Unit Tests

**Purpose**: Verify individual component behavior in isolation

**Characteristics**:
- Test single module/class/function
- Mock all external dependencies
- Fast execution (<1ms per test)
- No network, filesystem, or system resource access
- Located in `src/tests/<component>/`

**Scope in pi-netconfig**:
- `test_installer.py` - Installation logic, systemd integration
- `test_statemonitor.py` - State machine transitions
- `test_connectionmanager.py` - WiFi operations
- `test_apmanager.py` - Access point management
- `test_webserver.py` - HTTP endpoint handling
- `test_servicecontroller.py` - Service lifecycle

**Execution Platform**: MacOS development environment (primary)

### Integration Tests

**Purpose**: Verify component interaction and interface contracts

**Characteristics**:
- Test multiple components together
- Verify data flow between modules
- May use real subsystems
- Moderate execution time
- Located at `src/tests/integration/`

**Scope in pi-netconfig**:
- StateMonitor ↔ ConnectionManager coordination
- StateMonitor ↔ APManager state transitions
- WebServer ↔ StateMonitor status queries
- Full service startup/shutdown sequences

**Execution Platform**: Raspberry Pi target hardware (required)

### System Tests

**Purpose**: Validate complete system behavior end-to-end

**Characteristics**:
- Full application execution
- Real environment (NetworkManager, systemd)
- External dependency interaction
- Slow execution (seconds to minutes)
- Manual validation procedures

**Scope in pi-netconfig**:
- Complete WiFi client → AP fallback cycle
- Systemd service integration
- HTML configuration interface
- Network persistence across reboots

**Execution Platform**: Raspberry Pi target hardware (exclusively)

### Acceptance Tests

**Purpose**: Verify system meets stakeholder requirements

**Characteristics**:
- Business/user scenario validation
- Manual or semi-automated
- Validates against functional requirements
- May incorporate user feedback

**Scope in pi-netconfig**:
- FR-001: Self-install on clean Raspberry Pi
- FR-007: Auto-connect to known networks
- FR-015: Fallback to AP mode when no network available
- FR-026: HTML configuration interface accessibility

**Execution Platform**: Raspberry Pi target hardware (exclusively)

### Regression Tests

**Purpose**: Ensure existing functionality remains intact after changes

**Characteristics**:
- Permanent test suite (not ephemeral)
- Executed after every code change
- Cumulative (grows over time)
- Automated execution required

**Scope in pi-netconfig**:
- All unit tests in `src/tests/<component>/` are regression tests
- Maintained permanently in repository
- Executed via pytest in full suite runs

**Execution Platform**: MacOS (primary), Raspberry Pi (validation)

### Performance Tests

**Purpose**: Validate non-functional performance requirements

**Characteristics**:
- Measure timing, throughput, resource usage
- Baseline establishment
- Trend analysis over time
- Requires actual hardware

**Scope in pi-netconfig**:
- NFR-001: State transitions <100ms
- NFR-002: Network scan <30s
- NFR-003: Connection establishment <10s
- FR-055: Service startup <5s

**Execution Platform**: Raspberry Pi target hardware (exclusively)

[Return to Table of Contents](<#table of contents>)

## Test Execution Platforms

### MacOS Development Platform

**Supported Test Types**:
- Unit tests (primary execution)
- Regression tests (primary execution)

**Why MacOS Works**:
- Comprehensive mocking of external dependencies
- Fast iteration during development
- Immediate feedback on code changes
- No hardware setup required

**Limitations**:
- Cannot test actual NetworkManager integration
- Cannot verify real wireless hardware behavior
- Cannot validate systemd service lifecycle
- Performance measurements unreliable

**Mocking Requirements**:
- Mock all nmcli commands via `subprocess.check_output`
- Mock systemd/systemctl via `subprocess.run`
- Mock network connectivity via `socket.socket`
- Use `tempfile.TemporaryDirectory` for filesystem isolation
- Use `unittest.mock.AsyncMock` for async components

### Raspberry Pi Target Platform

**Supported Test Types**:
- Integration tests (required)
- System tests (required)
- Acceptance tests (required)
- Performance tests (required)
- Unit tests (validation)
- Regression tests (validation)

**Why Raspberry Pi Required**:
- Actual NetworkManager daemon
- Real nmcli command-line interface
- Actual WiFi hardware and radio
- Systemd service manager integration
- D-Bus communication
- True performance characteristics

**Test Execution**:
```bash
# Unit test validation
pytest --pyargs pi_netconfig -v

# Integration tests
pytest src/tests/integration/ -v --slow

# System tests (manual)
sudo systemctl start pi-netconfig
# Validate actual WiFi behavior

# Performance measurements
pytest src/tests/performance/ -v --benchmark
```

[Return to Table of Contents](<#table of contents>)

## Testing Workflow

### Development Cycle (MacOS)

1. **Code Change**
   - Implement fix or feature
   - Update relevant design documents

2. **Targeted Unit Test**
   ```bash
   pytest src/tests/<component>/ -v
   ```

3. **Full Regression Suite**
   ```bash
   pytest src/tests/ -v --cov=src --cov-report=html
   ```

4. **Coverage Verification**
   - Review HTML coverage report
   - Ensure >90% code coverage maintained

5. **Commit**
   ```bash
   git commit -m "fix: description"
   git push
   ```

### Debug Cycle

When tests fail, follow progressive validation:

1. **Targeted Validation** (Immediate fix verification)
   ```bash
   # Create ephemeral validation script
   # Example: src/tests/validate_issue_0042.py
   pytest src/tests/validate_issue_0042.py -v
   ```

2. **Integration Validation** (Dependent components)
   ```bash
   pytest src/tests/statemonitor/ src/tests/connectionmanager/ -v
   ```

3. **Full Regression** (Complete suite)
   ```bash
   pytest src/tests/ -v --cov=src
   ```

4. **Iteration Management**
   - If validation fails: increment iteration number in coupled documents
   - Git commit iteration increment
   - Repeat cycle

### Deployment Validation (Raspberry Pi)

1. **Build Distribution**
   ```bash
   # On MacOS
   cd /Users/williamwatson/Documents/GitHub/pi-netconfig
   rm -rf dist/ build/ *.egg-info/
   python -m build
   ```

2. **Transfer to Pi**
   ```bash
   scp dist/pi_netconfig-0.1.0-py3-none-any.whl pi@raspberrypi:~
   ```

3. **Install on Pi**
   ```bash
   ssh pi@raspberrypi
   pip install ~/pi_netconfig-0.1.0-py3-none-any.whl
   ```

4. **Unit Test Validation**
   ```bash
   pytest --pyargs pi_netconfig -v
   ```

5. **Integration Tests**
   ```bash
   pytest src/tests/integration/ -v --slow
   ```

6. **System Tests** (Manual validation)
   ```bash
   sudo systemctl start pi-netconfig
   # Verify:
   # - Service starts without errors
   # - Connects to known WiFi
   # - Falls back to AP if no network
   # - Web interface accessible at 192.168.4.1
   ```

7. **Performance Validation**
   ```bash
   pytest src/tests/performance/ -v --benchmark
   ```

[Return to Table of Contents](<#table of contents>)

## Mocking Strategy

### External Dependencies Requiring Mocking

**NetworkManager (nmcli)**:
```python
@patch('subprocess.check_output')
def test_scan_networks(mock_check):
    mock_check.return_value = b'SSID1:85:WPA2\nSSID2:72:WPA2\n'
    networks = connection_manager.scan_networks()
    assert len(networks) == 2
```

**Systemd (systemctl)**:
```python
@patch('subprocess.run')
def test_install_service(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    result = installer.install_systemd_unit()
    assert result is True
```

**Network Sockets**:
```python
@patch('socket.socket')
def test_connectivity(mock_socket):
    mock_socket.return_value.connect.return_value = None
    assert connection_manager.test_connectivity() is True
```

**Async Components**:
```python
from unittest.mock import AsyncMock

@pytest.fixture
def mock_connection_manager():
    manager = AsyncMock()
    manager.scan_networks.return_value = ['Network1', 'Network2']
    return manager
```

### Filesystem Isolation

```python
import tempfile
import shutil

@pytest.fixture
def temp_config_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_save_config(temp_config_dir):
    config_path = Path(temp_config_dir) / "config.json"
    save_configuration(config_path, {"ssid": "test"})
    assert config_path.exists()
```

### Mocking Principles

1. **Isolation**: Each test creates and destroys its own environment
2. **Determinism**: Mock returns consistent, predictable values
3. **Verification**: Assert mock interactions where appropriate
4. **Cleanup**: Use fixtures with teardown for resource cleanup

[Return to Table of Contents](<#table of contents>)

## Test Organization

### Directory Structure

```
src/
└── tests/
    ├── installer/
    │   └── test_installer.py
    ├── statemonitor/
    │   └── test_statemonitor.py
    ├── connectionmanager/
    │   └── test_connectionmanager.py
    ├── apmanager/
    │   └── test_apmanager.py
    ├── webserver/
    │   └── test_webserver.py
    ├── servicecontroller/
    │   └── test_servicecontroller.py
    ├── integration/
    │   └── test_full_cycle.py
    ├── performance/
    │   └── test_benchmarks.py
    └── validate_issue_NNNN.py  # Ephemeral validation scripts
```

### Permanent vs. Ephemeral Tests

**Permanent Tests** (`src/tests/<component>/`):
- Part of regression suite
- Maintained indefinitely
- Executed on every test run
- Never deleted

**Ephemeral Validation Scripts** (`src/tests/validate_*.py`):
- Created for specific issue verification
- Located at tests/ root level
- Referenced in issue/change documents
- Removed after successful verification
- May be moved to deprecated/ for historical reference

### Test Naming Conventions

**Test Files**: `test_<component>.py`

**Test Functions**: `test_<scenario>_<expected_outcome>`

Examples:
- `test_scan_networks_returns_list`
- `test_configure_network_with_invalid_ssid_raises_error`
- `test_transition_to_connected_updates_state`

[Return to Table of Contents](<#table of contents>)

## Progressive Validation

Progressive validation provides graduated confidence during debug cycles:

### Phase 1: Targeted Validation

**Purpose**: Verify specific fix resolves reported issue

**Approach**:
```bash
# Create minimal validation script
# src/tests/validate_issue_0042.py

pytest src/tests/validate_issue_0042.py -v
```

**Criteria**: Test directly exercises fixed code path

### Phase 2: Integration Validation

**Purpose**: Verify fix doesn't break dependent components

**Approach**:
```bash
# Test affected component and its dependencies
pytest src/tests/statemonitor/ src/tests/connectionmanager/ -v
```

**Criteria**: All component interdependencies verified

### Phase 3: Full Regression

**Purpose**: Verify entire system remains functional

**Approach**:
```bash
# Execute complete test suite
pytest src/tests/ -v --cov=src --cov-report=html
```

**Criteria**: 
- All tests pass
- Code coverage ≥90%
- No new failures introduced

### Validation Script Lifecycle

1. **Creation**: When issue created, validation script designed
2. **Execution**: During debug cycle, script verifies fix
3. **Documentation**: Script referenced in issue/change documents
4. **Archival**: After closure, script removed or moved to deprecated/

[Return to Table of Contents](<#table of contents>)

## Platform-Specific Procedures

### MacOS Development Environment

**Setup**:
```bash
cd /Users/williamwatson/Documents/GitHub/pi-netconfig
python3 -m venv venv
source venv/bin/activate
pip install -e .[dev]
```

**Test Execution**:
```bash
# Single component
pytest src/tests/statemonitor/ -v

# Full suite with coverage
pytest src/tests/ -v --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Continuous Testing**:
```bash
# Install pytest-watch for continuous execution
pip install pytest-watch

# Watch for file changes and re-run tests
ptw src/tests/ -- -v
```

### Raspberry Pi Target Platform

**Initial Setup**:
```bash
# Install from wheel
pip install pi_netconfig-0.1.0-py3-none-any.whl

# Verify installation
python -c "import pi_netconfig; print(pi_netconfig.__version__)"
```

**Unit Test Validation**:
```bash
# Run installed package tests
pytest --pyargs pi_netconfig -v
```

**Integration Testing**:
```bash
# Requires cloned repository on Pi
git clone https://github.com/William12556/pi-netconfig.git
cd pi-netconfig
pytest src/tests/integration/ -v --slow
```

**System Testing** (Manual):
```bash
# Install as systemd service
sudo python -m pi_netconfig.installer

# Start service
sudo systemctl start pi-netconfig

# Monitor logs
sudo journalctl -u pi-netconfig -f

# Validate WiFi behavior
nmcli device status
nmcli connection show

# Test web interface
curl http://192.168.4.1
```

**Performance Benchmarking**:
```bash
# Execute performance test suite
pytest src/tests/performance/ -v --benchmark

# Generate benchmark report
pytest-benchmark compare
```

[Return to Table of Contents](<#table of contents>)

## Coverage Requirements

### Code Coverage Targets

**Overall Project**: ≥90% line coverage

**Component Minimums**:
- installer.py: ≥95%
- statemonitor.py: ≥95%
- connectionmanager.py: ≥90%
- apmanager.py: ≥90%
- webserver.py: ≥85%
- servicecontroller.py: ≥90%

### Coverage Measurement

```bash
# Generate coverage report
pytest src/tests/ --cov=src --cov-report=term --cov-report=html

# Terminal output shows coverage summary
# HTML report in htmlcov/index.html provides detailed analysis
```

### Coverage Analysis

**Uncovered Code Categories**:
- Exception handlers for unlikely error conditions
- Defensive programming checks
- Platform-specific code paths
- Deprecated functionality

**Exemptions**:
```python
# Use pragma to exclude specific lines
if platform.system() != 'Linux':  # pragma: no cover
    raise RuntimeError("Requires Linux")
```

### Requirements Traceability

Every functional requirement must have corresponding test coverage:

- Traceability matrix links: Requirement → Design → Code → Test
- Gap analysis identifies untested requirements
- Test documentation references requirement IDs

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-11-30 | Initial testing guide creation |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
