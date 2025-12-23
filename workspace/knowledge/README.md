# Knowledge Base README

Created: 2025-12-04

---

## Purpose

The `workspace/knowledge/` directory captures institutional knowledge, lessons learned, and technical patterns discovered during development. Both Claude Desktop and Claude Code domains must consult this knowledge base when creating documents or code.

---

## Directory Structure

```
workspace/knowledge/
├── README.md                      # This file
└── python-package-imports.md      # Package import requirements and troubleshooting
```

---

## Usage Guidelines

### When to Consult
- Before creating new documents
- Before implementing code changes
- When encountering import errors
- When setting up development environment
- When troubleshooting test failures

### When to Add
- Discovery of non-obvious technical requirements
- Resolution of recurring issues
- Identification of critical patterns
- Documentation of design decisions with rationale
- Capture of environment-specific constraints

### Document Format
All knowledge documents should include:
- Creation date
- Table of contents
- Clear problem/solution structure
- Practical examples
- Version history

---

## Current Knowledge Base

### python-package-imports.md
**Topic:** Python package structure and import requirements

**Key Points:**
- All imports must use `pi_netconfig.` prefix
- Required `pip install -e .` for testing
- Common ModuleNotFoundError solutions

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-04 | System | Initial knowledge base structure |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
