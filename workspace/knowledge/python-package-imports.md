# Python Package Import Structure

Created: 2025-12-04

---

## Table of Contents
1. [Overview](#overview)
2. [The Problem](#the-problem)
3. [The Solution](#the-solution)
4. [Implementation Rules](#implementation-rules)
5. [Testing Setup](#testing-setup)
6. [Examples](#examples)

---

## 1. Overview

Pi-netconfig uses Python package structure requiring qualified imports throughout source code and tests.

[Return to Table of Contents](#table-of-contents)

---

## 2. The Problem

**Symptom:** Tests fail with `ModuleNotFoundError: No module named 'module'`

**Root Cause:** Python cannot resolve bare imports when code is structured as an installed package.

**Example Error:**
```
src/pi_netconfig/main.py:26: in <module>
    from installer import install, InstallationDetector
E   ModuleNotFoundError: No module named 'installer'
```

[Return to Table of Contents](#table-of-contents)

---

## 3. The Solution

All imports within `src/pi_netconfig/` and `src/tests/` must use package-qualified names with `pi_netconfig.` prefix.

[Return to Table of Contents](#table-of-contents)

---

## 4. Implementation Rules

### Source Code (`src/pi_netconfig/`)
**Rule:** All inter-module imports must be package-qualified.

❌ **Incorrect:**
```python
from installer import install, InstallationDetector
from statemonitor import StateMonitor
```

✅ **Correct:**
```python
from pi_netconfig.installer import install, InstallationDetector
from pi_netconfig.statemonitor import StateMonitor
```

### Test Code (`src/tests/`)
**Rule:** All imports of project modules must be package-qualified.

❌ **Incorrect:**
```python
from apmanager import APManager
from connectionmanager import ConnectionManager
```

✅ **Correct:**
```python
from pi_netconfig.apmanager import APManager
from pi_netconfig.connectionmanager import ConnectionManager
```

### Standard Library and Third-Party Imports
**Rule:** These remain unchanged (no package prefix needed).

✅ **Correct:**
```python
import asyncio
import logging
from pathlib import Path
from unittest.mock import Mock, patch
```

[Return to Table of Contents](#table-of-contents)

---

## 5. Testing Setup

**Required:** Install package in editable mode before running tests.

```bash
cd /Users/williamwatson/Documents/GitHub/pi-netconfig
source venv/bin/activate
pip install -e .
pytest -v
```

The `-e` flag enables editable installation, making `pi_netconfig` importable while allowing code modifications without reinstallation.

[Return to Table of Contents](#table-of-contents)

---

## 6. Examples

### main.py (Service Controller)
```python
from pi_netconfig.installer import install, InstallationDetector
from pi_netconfig.statemonitor import StateMonitor
```

### test_installer.py
```python
from pi_netconfig.installer import (
    install,
    InstallationDetector,
    VenvDetector,
    SystemdInstaller,
    InstallerError
)
```

### statemonitor.py
```python
from pi_netconfig.connectionmanager import ConnectionManager
from pi_netconfig.apmanager import APManager
```

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-04 | System | Initial documentation of package import requirements |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
