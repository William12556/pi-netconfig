Created: 2025 November 13

# Requirements Traceability Matrix

## Table of Contents

[Introduction](<#introduction>)
[Functional Requirements](<#functional requirements>)
[Non-Functional Requirements](<#non-functional requirements>)
[Traceability Matrix](<#traceability matrix>)
[Bidirectional Navigation](<#bidirectional navigation>)
[Version History](<#version history>)

---

## Introduction

This document establishes bidirectional traceability between requirements, design documents, source code, and tests as required by P02 1.3.7, P05 1.6.2, and P05 1.6.3.

**Purpose**: Enable verification that all requirements are:
- Designed (requirement → design)
- Implemented (design → code)
- Tested (code → test)
- Traceable in both directions

**Scope**: Pi-netconfig project v0.2.0

[Return to Table of Contents](<#table of contents>)

---

## Functional Requirements

Functional requirements extracted from [design-0000-master.md](../design/design-0000-master.md) scope and components sections.

### Installation & Bootstrapping

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-001 | System shall detect if systemd service is installed on execution | High | design-0000 scope |
| FR-002 | System shall self-install as systemd service when not installed | High | design-0000 scope |
| FR-003 | System shall create required directories during installation | High | design-0001 installer |
| FR-004 | System shall copy itself to /usr/local/bin/pi-netconfig/ | High | design-0001 installer |
| FR-005 | System shall generate and install systemd unit file | High | design-0001 installer |
| FR-006 | System shall enable and start systemd service after installation | High | design-0001 installer |
| FR-007 | System shall verify installation success before exiting bootstrap | Medium | design-0001 installer |

### Connectivity Monitoring

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-010 | System shall check WiFi connection status every 30 seconds | High | design-0002 statemonitor |
| FR-011 | System shall detect connection loss within 10 seconds of boot | High | design-0000 constraints |
| FR-012 | System shall test connectivity by pinging known hosts (8.8.8.8, 1.1.1.1) | Medium | design-0003 connectionmanager |
| FR-013 | System shall transition to AP mode after 3 failed connection checks | High | design-0002 statemonitor |

### State Management

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-020 | System shall implement three operational states: CHECKING, CLIENT, AP_MODE | High | design-0002 statemonitor |
| FR-021 | System shall coordinate transitions between operational states | High | design-0002 statemonitor |
| FR-022 | System shall initialize all components on state transitions | High | design-0002 statemonitor |
| FR-023 | System shall shutdown components gracefully on service stop | High | design-0006 servicecontroller |

### WiFi Client Operations

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-030 | System shall scan for available WiFi networks on request | High | design-0003 connectionmanager |
| FR-031 | System shall parse network SSID, signal strength, security, frequency | Medium | design-0003 connectionmanager |
| FR-032 | System shall configure WiFi connection using nmcli | High | design-0003 connectionmanager |
| FR-033 | System shall activate WiFi connection after configuration | High | design-0003 connectionmanager |
| FR-034 | System shall persist last successful SSID to JSON file | Medium | design-0003 connectionmanager |

### Access Point Operations

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-040 | System shall create WiFi access point with predictable SSID | High | design-0004 apmanager |
| FR-041 | System shall use SSID format 'PiConfig-<MAC_LAST_4>' | Medium | design-0004 apmanager |
| FR-042 | System shall secure AP with WPA2 and password 'piconfig123' | Medium | design-0004 apmanager |
| FR-043 | System shall assign IP range 192.168.50.1/24 to AP | Medium | design-0004 apmanager |
| FR-044 | System shall deactivate AP when switching to client mode | High | design-0004 apmanager |
| FR-045 | System shall activate AP within 15 seconds of failed connection | High | design-0000 constraints |

### Web Interface

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-050 | System shall serve web configuration interface on port 8080 | High | design-0005 webserver |
| FR-051 | System shall provide GET / endpoint serving main configuration page | High | design-0005 webserver |
| FR-052 | System shall provide GET /api/scan endpoint returning JSON network list | High | design-0005 webserver |
| FR-053 | System shall provide POST /api/configure endpoint accepting SSID/password | High | design-0005 webserver |
| FR-054 | System shall provide GET /api/status endpoint returning current state | Medium | design-0005 webserver |
| FR-055 | System shall respond to web requests within 500ms | Medium | design-0000 constraints |

### Configuration Persistence

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-060 | System shall store last successful SSID only (single network) | Medium | design-0000 scope |
| FR-061 | System shall persist configuration to /etc/pi-netconfig/config.json | Medium | design-0000 architecture |
| FR-062 | System shall store configuration timestamp in ISO 8601 format | Low | design-0000 data_design |

### Service Lifecycle

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-070 | System shall detect execution mode (bootstrap/service/manual) | High | design-0006 servicecontroller |
| FR-071 | System shall configure logging to /var/log/pi-netconfig.log | High | design-0006 servicecontroller |
| FR-072 | System shall register SIGTERM and SIGINT signal handlers | High | design-0006 servicecontroller |
| FR-073 | System shall perform graceful shutdown on signal receipt | High | design-0006 servicecontroller |
| FR-074 | System shall verify root privileges before service operations | High | design-0006 servicecontroller |

[Return to Table of Contents](<#table of contents>)

---

## Non-Functional Requirements

| ID | Requirement | Target | Priority | Source |
|----|-------------|--------|----------|--------|
| NFR-001 | Boot to ready time | < 30 seconds | High | design-0000 nonfunctional |
| NFR-002 | Network scan time | < 5 seconds | Medium | design-0000 nonfunctional |
| NFR-003 | Configuration application time | < 10 seconds | Medium | design-0000 nonfunctional |
| NFR-004 | Code coverage | 80% minimum | High | design-0000 nonfunctional |
| NFR-005 | Type hints | All functions | Medium | design-0000 constraints |
| NFR-006 | Docstrings | All public methods | Medium | design-0000 nonfunctional |
| NFR-007 | Thread safety | All concurrent operations | High | governance + user prefs |
| NFR-008 | Error logging | Traceback on all exceptions | High | governance + user prefs |
| NFR-009 | PEP 8 compliance | All code | Medium | design-0000 constraints |

[Return to Table of Contents](<#table of contents>)

---

## Traceability Matrix

### Requirement → Design → Code → Test

| Requirement | Design Doc | Code Module | Test Doc | Status |
|-------------|-----------|-------------|----------|--------|
| FR-001 | design-0001 §installer | installer.py::is_service_installed() | - | ⚠ No test |
| FR-002 | design-0001 §installer | installer.py::install() | - | ⚠ No test |
| FR-003 | design-0001 §processing_logic | installer.py::_create_directories() | - | ⚠ No test |
| FR-004 | design-0001 §processing_logic | installer.py::_copy_to_install_location() | - | ⚠ No test |
| FR-005 | design-0001 §processing_logic | installer.py::_install_systemd_unit() | - | ⚠ No test |
| FR-006 | design-0001 §processing_logic | installer.py::_enable_and_start_service() | - | ⚠ No test |
| FR-007 | design-0001 §error_conditions | installer.py::install() return check | - | ⚠ No test |
| FR-010 | design-0002 §processing_logic | statemonitor.py::run() loop | - | ⚠ No test |
| FR-011 | design-0000 §design_constraints | statemonitor.py connection check | - | ⚠ No test |
| FR-012 | design-0003 §processing_logic | connectionmanager.py::test_connection() | - | ⚠ No test |
| FR-013 | design-0002 §processing_logic | statemonitor.py::_handle_state() | - | ⚠ No test |
| FR-020 | design-0002 §key_elements | statemonitor.py::NetworkState enum | - | ⚠ No test |
| FR-021 | design-0002 §responsibilities | statemonitor.py::_transition_state() | - | ⚠ No test |
| FR-022 | design-0002 §responsibilities | statemonitor.py component init | - | ⚠ No test |
| FR-023 | design-0006 §processing_logic | main.py::graceful_shutdown() | - | ⚠ No test |
| FR-030 | design-0003 §processing_logic | connectionmanager.py::scan_networks() | - | ⚠ No test |
| FR-031 | design-0003 §outputs | connectionmanager.py::_parse_scan_output() | - | ⚠ No test |
| FR-032 | design-0003 §processing_logic | connectionmanager.py::configure_network() | - | ⚠ No test |
| FR-033 | design-0003 §processing_logic | connectionmanager.py::configure_network() | - | ⚠ No test |
| FR-034 | design-0003 §processing_logic | connectionmanager.py::_persist_config() | - | ⚠ No test |
| FR-040 | design-0004 §purpose | apmanager.py::activate() | test-0001 TC-001 | ✓ Partial |
| FR-041 | design-0004 §processing_logic | apmanager.py::_generate_ssid() | test-0001 TC-002 | ✓ Partial |
| FR-042 | design-0004 §processing_logic | apmanager.py::activate() | test-0001 TC-003 | ✓ Partial |
| FR-043 | design-0004 §processing_logic | apmanager.py config | test-0001 TC-004 | ✓ Partial |
| FR-044 | design-0004 §responsibilities | apmanager.py::deactivate() | - | ⚠ No test |
| FR-045 | design-0000 §design_constraints | statemonitor.py transition | - | ⚠ No test |
| FR-050 | design-0005 §purpose | webserver.py::WebConfigServer | - | ⚠ No test |
| FR-051 | design-0005 §processing_logic | webserver.py::do_GET() "/" | - | ⚠ No test |
| FR-052 | design-0005 §processing_logic | webserver.py::do_GET() "/api/scan" | - | ⚠ No test |
| FR-053 | design-0005 §processing_logic | webserver.py::do_POST() "/api/configure" | - | ⚠ No test |
| FR-054 | design-0005 §processing_logic | webserver.py::do_GET() "/api/status" | - | ⚠ No test |
| FR-055 | design-0000 §performance_targets | webserver.py response time | - | ⚠ No test |
| FR-060 | design-0000 §scope | connectionmanager.py single SSID | - | ⚠ No test |
| FR-061 | design-0000 §architecture | connectionmanager.py config path | - | ⚠ No test |
| FR-062 | design-0000 §data_design | connectionmanager.py timestamp format | - | ⚠ No test |
| FR-070 | design-0006 §processing_logic | main.py::detect_execution_mode() | - | ⚠ No test |
| FR-071 | design-0006 §processing_logic | main.py::configure_logging() | - | ⚠ No test |
| FR-072 | design-0006 §processing_logic | main.py::register_signal_handlers() | - | ⚠ No test |
| FR-073 | design-0006 §responsibilities | main.py::graceful_shutdown() | - | ⚠ No test |
| FR-074 | design-0006 §processing_logic | main.py::verify_root_privileges() | - | ⚠ No test |

**Legend:**
- ✓ Fully traced: requirement → design → code → test
- ✓ Partial: requirement → design → code (test incomplete)
- ⚠ No test: requirement → design → code (no tests)
- ✗ Missing: gaps in traceability chain

**Statistics:**
- Total functional requirements: 37
- Fully tested: 0 (0%)
- Partially tested: 4 (11%)
- No tests: 33 (89%)

[Return to Table of Contents](<#table of contents>)

---

## Bidirectional Navigation

### Design → Requirements

| Design Document | Requirements Addressed |
|----------------|------------------------|
| design-0000-master.md | All FR/NFR (master specification) |
| design-0001-installer.md | FR-001 through FR-007 |
| design-0002-statemonitor.md | FR-010, FR-011, FR-013, FR-020, FR-021, FR-022 |
| design-0003-connectionmanager.md | FR-012, FR-030 through FR-034, FR-060, FR-061, FR-062 |
| design-0004-apmanager.md | FR-040 through FR-045 |
| design-0005-webserver.md | FR-050 through FR-055 |
| design-0006-servicecontroller.md | FR-023, FR-070 through FR-074 |

### Code → Requirements

| Source File | Requirements Implemented |
|-------------|-------------------------|
| main.py | FR-023, FR-070 through FR-074, NFR-007, NFR-008 |
| installer.py | FR-001 through FR-007 |
| statemonitor.py | FR-010, FR-011, FR-013, FR-020, FR-021, FR-022, FR-045 |
| connectionmanager.py | FR-012, FR-030 through FR-034, FR-060, FR-061, FR-062 |
| apmanager.py | FR-040 through FR-044 |
| webserver.py | FR-050 through FR-055 |

### Test → Requirements

| Test Document | Requirements Verified |
|---------------|----------------------|
| test-0001-apmanager.md | FR-040, FR-041, FR-042, FR-043 (partial) |

**Gap Analysis**: 33/37 functional requirements (89%) lack test coverage.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-13 | Domain 1 | Initial requirements traceability matrix created from design-0000-master.md; extracted 37 functional requirements and 9 non-functional requirements; established bidirectional traceability links |

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
