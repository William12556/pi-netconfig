Created: 2026 June 17

# Project Context

---

## 1.0 Project

**Name:** pi-netconfig
**Description:** WiFi configuration service for headless Raspberry Pi/Debian systems with automatic fallback to an access point and a web configuration page.

**Technology stack:** Python 3.9+ | standard library only (no runtime dependencies); NetworkManager via `nmcli`; `http.server` web interface (AP mode, 192.168.50.1:8080); systemd
**Target platform:** Raspberry Pi, Debian-based Linux with NetworkManager (validated on Debian 13 Trixie); root privileges required

---

## 2.0 Commands

| Action | Command |
|---|---|
| Install (dev) | `pip install -e .[dev]` |
| Install (Pi) | `./bin/install.sh` (latest release), `./bin/install.sh <version>` or `./bin/install.sh <path-to-wheel>` |
| Test | `pytest src/tests/` (coverage: `pytest src/tests/ --cov=src --cov-report=html`) |
| Lint | n/a (none configured) |
| Build | `./bin/build.sh` |
| Release | `./bin/release.sh` (requires authenticated `gh` CLI) |

---

## 3.0 Code Style

- PEP 8
- State-based operation: CHECKING → CLIENT ↔ AP_MODE (`statemonitor.py`)
- Network changes through `nmcli` only; single persisted network profile
- Modules: `apmanager`, `connectionmanager`, `installer`, `statemonitor`, `webserver`, `main` under `src/pi_netconfig/`

---

## 4.0 Repository Conventions

**Branches:** `main`; other local branches belong to Claude Code worktrees.
**Commits:** conventional commits (`feat:`, `fix:`, `docs:`, `chore:`).

---

## 5.0 Governance

| Artifact | Location |
|---|---|
| Governance | `ai/governance.md` |
| Designs | `ai/workspace/design/` |
| Changes | `ai/workspace/change/` |
| Prompts | `ai/workspace/prompt/` |
| Issues | `ai/workspace/issue/` |

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-06-17 | Initial template |
| 1.0 | 2026-09-23 | Project context filled in (pi-netconfig) |

---

Copyright (c) 2026 William Watson. MIT License.
