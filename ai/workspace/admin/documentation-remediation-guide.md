Created: 2025 January 08

# Documentation Remediation Guide

## Table of Contents

- [1. Overview](<#1 overview>)
- [2. High Priority Changes](<#2 high priority changes>)
  - [2.1 User Guide Python Version](<#2.1 user guide python version>)
  - [2.2 Deploy Test Guide Version References](<#2.2 deploy test guide version references>)
  - [2.3 Entry Point Configuration](<#2.3 entry point configuration>)
  - [2.4 README Installation Commands](<#2.4 readme installation commands>)
- [3. Medium Priority Changes](<#3 medium priority changes>)
  - [3.1 Build Script Python Version](<#3.1 build script python version>)
  - [3.2 AP Mode Test Commands Metadata](<#3.2 ap mode test commands metadata>)
  - [3.3 Install Script Enhancement](<#3.3 install script enhancement>)
- [4. Low Priority Changes](<#4 low priority changes>)
  - [4.1 Docs README Enhancement](<#4.1 docs readme enhancement>)
- [5. Validation Checklist](<#5 validation checklist>)
- [6. Version History](<#6 version history>)

---

## 1. Overview

This document provides specific remediation instructions for documentation inconsistencies identified between `docs/`, `src/`, root scripts, and `pyproject.toml`.

**Authoritative Source:** `pyproject.toml` defines version (1.0.0) and Python requirement (>=3.9).

[Return to Table of Contents](<#table of contents>)

---

## 2. High Priority Changes

### 2.1 User Guide Python Version

**File:** `docs/user-guide.md`

**Location:** Section 1. Introduction, "System Requirements" paragraph

**Current Text:**
```
- Python 3.11 or higher
```

**Replace With:**
```
- Python 3.9 or higher
```

**Rationale:** Aligns with `pyproject.toml` specification `requires-python = ">=3.9"`.

[Return to Table of Contents](<#table of contents>)

---

### 2.2 Deploy Test Guide Version References

**File:** `docs/deploy_test-guide.md`

**Change 1 - Section 3.1**

**Location:** Section 3.1 Creating Distribution Package

**Current Text:**
```
This creates `dist/pi_netconfig-0.2.0-py3-none-any.whl`
```

**Replace With:**
```
This creates `dist/pi_netconfig-1.0.0-py3-none-any.whl`
```

---

**Change 2 - Section 3.2**

**Location:** Section 3.2 Deployment to Raspberry Pi, "Transfer wheel file" code block

**Current Text:**
```bash
scp dist/pi_netconfig-0.2.0-py3-none-any.whl admin@raspberry-pi:/tmp/
```

**Replace With:**
```bash
scp dist/pi_netconfig-1.0.0-py3-none-any.whl admin@raspberry-pi:/tmp/
```

---

**Change 3 - Section 3.2**

**Location:** Section 3.2 Deployment to Raspberry Pi, "Install on Raspberry Pi" code block

**Current Text:**
```bash
sudo pip install /tmp/pi_netconfig-0.2.0-py3-none-any.whl
```

**Replace With:**
```bash
sudo pip install /tmp/pi_netconfig-1.0.0-py3-none-any.whl
```

---

**Change 4 - Section 6.5**

**Location:** Section 6.5 Import Errors After Install, "Reinstall if needed" code block

**Current Text:**
```bash
sudo pip install --force-reinstall /tmp/pi_netconfig-0.2.0-py3-none-any.whl
```

**Replace With:**
```bash
sudo pip install --force-reinstall /tmp/pi_netconfig-1.0.0-py3-none-any.whl
```

---

**Rationale:** Version 1.0.0 is current per `pyproject.toml` and `src/pi_netconfig/__init__.py`.

[Return to Table of Contents](<#table of contents>)

---

### 2.3 Entry Point Configuration

**File:** `pyproject.toml`

**Location:** After `[project.optional-dependencies]` section

**Add New Section:**
```toml
[project.scripts]
pi-netconfig = "pi_netconfig.main:main"
```

**Complete Context (insert after line 27):**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
]

[project.scripts]
pi-netconfig = "pi_netconfig.main:main"

[build-system]
```

**Rationale:** README documents `sudo pi-netconfig` command. Without entry point, this command does not exist after pip install.

[Return to Table of Contents](<#table of contents>)

---

### 2.4 README Installation Commands

**File:** `README.md`

**Location:** Quick Start section, "Install on Raspberry Pi" code block

**Current Text:**
```bash
# Install on Raspberry Pi
ssh admin@raspberry-pi
sudo pip install /tmp/pi_netconfig-1.0.0-py3-none-any.whl

# Run installer (first execution triggers automatic installation)
sudo pi-netconfig

# Start service
sudo systemctl start pi-netconfig
```

**Replace With:**
```bash
# Install on Raspberry Pi
ssh admin@raspberry-pi

# Create virtual environment (recommended)
sudo mkdir -p /opt/pi-netconfig
cd /opt/pi-netconfig
sudo python3 -m venv venv
sudo ./venv/bin/pip install /tmp/pi_netconfig-1.0.0-py3-none-any.whl

# Run installer (creates and starts systemd service)
sudo ./venv/bin/python -m pi_netconfig.installer --install --systemd-mode
```

**Rationale:** 
1. Aligns with deploy_test-guide.md procedures
2. Uses venv as required by installer.py validation
3. Removes redundant `systemctl start` (installer does this)

[Return to Table of Contents](<#table of contents>)

---

## 3. Medium Priority Changes

### 3.1 Build Script Python Version

**File:** `build.sh`

**Location:** Lines 8-13 (python version check)

**Current Text:**
```bash
# Verify python3.11 is available
if ! command -v python3.11 >/dev/null 2>&1; then
    echo "ERROR: python3.11 not found"
    echo "Install: brew install python@3.11"
    exit 1
fi
```

**Replace With:**
```bash
# Verify python3 is available and meets minimum version
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found"
    exit 1
fi

# Check Python version >= 3.9
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 9 ]); then
    echo "ERROR: Python 3.9+ required, found $PYTHON_VERSION"
    exit 1
fi
```

---

**Location:** Lines 15-19 (build module check)

**Current Text:**
```bash
# Verify build module is available
if ! python3.11 -m build --version >/dev/null 2>&1; then
    echo "ERROR: build module not found for python3.11"
    echo "Install: python3.11 -m pip install build"
    exit 1
fi
```

**Replace With:**
```bash
# Verify build module is available
if ! python3 -m build --version >/dev/null 2>&1; then
    echo "ERROR: build module not found"
    echo "Install: python3 -m pip install build"
    exit 1
fi
```

---

**Location:** Line 38 (build command)

**Current Text:**
```bash
python3.11 -m build
```

**Replace With:**
```bash
python3 -m build
```

**Rationale:** Aligns with pyproject.toml requires-python = ">=3.9".

[Return to Table of Contents](<#table of contents>)

---

### 3.2 AP Mode Test Commands Metadata

**File:** `docs/ap-mode-test-commands.md`

**Location:** Beginning of file (line 1)

**Current Text:**
```markdown
# AP Mode Testing Commands
```

**Replace With:**
```markdown
Created: 2025 December 23

# AP Mode Testing Commands
```

---

**Location:** End of file (after final `---`)

**Current Text:**
```markdown
---

**Notes:**
- Connection checks occur every 30 seconds
...
```

**Replace With:**
```markdown
---

**Notes:**
- Connection checks occur every 30 seconds
- Transition to AP mode requires 3 consecutive failures (≈90 seconds)
- Transition to CLIENT mode occurs on first successful connectivity check
- Web server binds to 0.0.0.0:8080 (accessible from all interfaces)
- AP network uses 192.168.50.0/24 subnet

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-23 | Initial command reference |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
```

**Rationale:** Aligns with project documentation standards per governance.md.

[Return to Table of Contents](<#table of contents>)

---

### 3.3 Install Script Enhancement

**File:** `install.sh`

**Location:** After line 19 (`sudo rm -rf /opt/pi-netconfig/venv/lib/python*/site-packages/pi_netconfig*`)

**Add Venv Existence Check:**
```bash
# Verify venv exists
if [ ! -d "/opt/pi-netconfig/venv" ]; then
    echo "ERROR: Virtual environment not found at /opt/pi-netconfig/venv"
    echo "For first-time installation, use deploy_test-guide.md procedures"
    exit 1
fi
```

**Complete Context (lines 15-24):**
```bash
# Uninstall existing package
echo "==> Cleaning existing installation..."
sudo /opt/pi-netconfig/venv/bin/pip uninstall -y pi_netconfig 2>/dev/null || true

# Verify venv exists
if [ ! -d "/opt/pi-netconfig/venv" ]; then
    echo "ERROR: Virtual environment not found at /opt/pi-netconfig/venv"
    echo "For first-time installation, use deploy_test-guide.md procedures"
    exit 1
fi

# Clear cache
echo "==> Clearing package cache..."
```

**Rationale:** Script assumes venv exists but provides no error handling if missing.

[Return to Table of Contents](<#table of contents>)

---

## 4. Low Priority Changes

### 4.1 Docs README Enhancement

**File:** `docs/README.md`

**Current Content:**
```markdown
# Documentation

Technical documentation and reference materials.

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
```

**Replace With:**
```markdown
# Documentation

Technical documentation and reference materials for pi-netconfig.

## Contents

| Document | Description |
|----------|-------------|
| [user-guide.md](user-guide.md) | Installation, deployment, service management, architecture |
| [deploy_test-guide.md](deploy_test-guide.md) | Build, deploy, and test procedures |
| [ap-mode-test-commands.md](ap-mode-test-commands.md) | AP mode testing command reference |

## Related Documentation

- [README.md](../README.md) - Project overview and quick start
- [ai/governance.md](../ai/governance.md) - Development governance framework

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
```

**Rationale:** Provides navigation to documentation files.

[Return to Table of Contents](<#table of contents>)

---

## 5. Validation Checklist

After applying changes, verify:

- [ ] `grep -r "3.11" docs/` returns no Python version requirements
- [ ] `grep -r "0.2.0" docs/` returns no matches
- [ ] `pip install -e .` creates `pi-netconfig` command
- [ ] `build.sh` executes with python3 (any version >=3.9)
- [ ] All docs files have Version History sections
- [ ] All docs files have Created timestamps

[Return to Table of Contents](<#table of contents>)

---

## 6. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-08 | Initial remediation guide |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
