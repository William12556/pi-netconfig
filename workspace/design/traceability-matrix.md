Created: 2025 November 13

# Requirements Traceability Matrix

## Functional Requirements

| ID | Requirement | Design | Code | Test | Status |
|----|-------------|--------|------|------|--------|
| FR-001 | Self-installation as systemd service | design-0001-installer | installer.py | test_installer.py | ✓ |
| FR-002 | WiFi connection detection and management | design-0003-connectionmanager | connectionmanager.py | test_connectionmanager.py | ✓ |
| FR-003 | Automatic AP mode activation for configuration | design-0004-apmanager | apmanager.py | test_apmanager.py | ✓ |
| FR-004 | Web-based configuration interface (port 8080) | design-0005-webserver | webserver.py | test_webserver.py | ✓ |
| FR-005 | Systemd service integration | design-0006-servicecontroller | main.py | test_main.py | ✓ |
| FR-006 | Network scanning and selection | design-0003-connectionmanager | connectionmanager.py | test_connectionmanager.py | ✓ |
| FR-007 | Single network configuration persistence | design-0003-connectionmanager | connectionmanager.py | test_connectionmanager.py | ✓ |

## Non-Functional Requirements

### Performance

| ID | Requirement | Target | Design | Code | Test | Status |
|----|-------------|--------|--------|------|------|--------|
| NFR-P01 | Connection detection after boot | < 10 seconds | design-0002-statemonitor | statemonitor.py | test_statemonitor.py | ✓ |
| NFR-P02 | AP mode activation after failed connection | < 15 seconds | design-0002-statemonitor | statemonitor.py | test_statemonitor.py | ✓ |
| NFR-P03 | Web interface response time | < 500ms | design-0005-webserver | webserver.py | test_webserver.py | ✓ |
| NFR-P04 | Boot to ready | < 30 seconds | design-0006-servicecontroller | main.py | test_main.py | ✓ |
| NFR-P05 | Network scan duration | < 5 seconds | design-0003-connectionmanager | connectionmanager.py | test_connectionmanager.py | ✓ |
| NFR-P06 | Configuration application | < 10 seconds | design-0003-connectionmanager | connectionmanager.py | test_connectionmanager.py | ✓ |

### Security

| ID | Requirement | Design | Code | Test | Status |
|----|-------------|--------|------|------|--------|
| NFR-S01 | Root privileges required for service | design-0006-servicecontroller | main.py | test_main.py | ✓ |
| NFR-S02 | WiFi passwords in NetworkManager secure storage | design-0003-connectionmanager | connectionmanager.py | test_connectionmanager.py | ✓ |
| NFR-S03 | Configuration file readable only by root | design-0003-connectionmanager | connectionmanager.py | test_connectionmanager.py | ✓ |
| NFR-S04 | No credential logging | All modules | *.py | test_*.py | ✓ |

### Reliability

| ID | Requirement | Design | Code | Test | Status |
|----|-------------|--------|------|------|--------|
| NFR-R01 | Automatic recovery to AP mode on repeated failures | design-0002-statemonitor | statemonitor.py | test_statemonitor.py | ✓ |
| NFR-R02 | Continue operation if single component fails | design-0002-statemonitor | statemonitor.py | test_statemonitor.py | ✓ |
| NFR-R03 | Graceful degradation if WiFi hardware unavailable | design-0004-apmanager | apmanager.py | test_apmanager.py | ✓ |

## Component Mapping

| Component | Requirements | Design Doc | Source File | Test File |
|-----------|--------------|------------|-------------|-----------|
| Installer | FR-001 | design-0001-installer | installer.py | test_installer.py |
| StateMonitor | NFR-P01, NFR-P02, NFR-R01, NFR-R02 | design-0002-statemonitor | statemonitor.py | test_statemonitor.py |
| ConnectionManager | FR-002, FR-006, FR-007, NFR-P05, NFR-P06, NFR-S02, NFR-S03 | design-0003-connectionmanager | connectionmanager.py | test_connectionmanager.py |
| APManager | FR-003, NFR-R03 | design-0004-apmanager | apmanager.py | test_apmanager.py |
| WebServer | FR-004, NFR-P03 | design-0005-webserver | webserver.py | test_webserver.py |
| ServiceController | FR-005, NFR-P04, NFR-S01 | design-0006-servicecontroller | main.py | test_main.py |

## Design Document Cross-Reference

| Design Doc | Requirements Covered | Code Files | Test Files |
|------------|---------------------|------------|------------|
| design-0000-master | All requirements | All modules | All tests |
| design-0001-installer | FR-001 | installer.py | test_installer.py |
| design-0002-statemonitor | NFR-P01, NFR-P02, NFR-R01, NFR-R02 | statemonitor.py | test_statemonitor.py |
| design-0003-connectionmanager | FR-002, FR-006, FR-007, NFR-P05, NFR-P06, NFR-S02, NFR-S03 | connectionmanager.py | test_connectionmanager.py |
| design-0004-apmanager | FR-003, NFR-R03 | apmanager.py | test_apmanager.py |
| design-0005-webserver | FR-004, NFR-P03 | webserver.py | test_webserver.py |
| design-0006-servicecontroller | FR-005, NFR-P04, NFR-S01 | main.py | test_main.py |

## Test Coverage

| Test File | Requirements Verified | Code Coverage |
|-----------|----------------------|---------------|
| test_installer.py | FR-001 | installer.py |
| test_statemonitor.py | NFR-P01, NFR-P02, NFR-R01, NFR-R02 | statemonitor.py |
| test_connectionmanager.py | FR-002, FR-006, FR-007, NFR-P05, NFR-P06, NFR-S02, NFR-S03 | connectionmanager.py |
| test_apmanager.py | FR-003, NFR-R03 | apmanager.py |
| test_webserver.py | FR-004, NFR-P03 | webserver.py |
| test_main.py | FR-005, NFR-P04, NFR-S01 | main.py |

## Bidirectional Navigation

**Forward Traceability (Requirements → Implementation):**
- Each requirement links to design document(s)
- Each design links to source file(s)
- Each source file links to test file(s)

**Backward Traceability (Implementation → Requirements):**
- Each test file validates specific requirements
- Each source file implements specific design elements
- Each design element satisfies specific requirements

## Audit Trail

| Date | Change | Updated By |
|------|--------|------------|
| 2025-11-13 | Initial traceability matrix created | Domain 1 |
| 2025-11-13 | Requirement IDs FR-001 through FR-007, NFR-P01 through NFR-P06, NFR-S01 through NFR-S04, NFR-R01 through NFR-R03 assigned | Domain 1 |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
