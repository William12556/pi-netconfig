# Configuration Audit Template

**Audit ID:** config-audit-NNNN-YYYY-MM-DD  
**Date:** YYYY-MM-DD  
**Auditor:** [Name]  
**Baseline:** [Git tag]  
**Baseline Commit:** [SHA]

---

## Executive Summary

- **Compliance Status:** [Compliant | Non-Compliant | Partial]
- **Implementations Verified:** N/N
- **Deviations Found:** N
- **Critical Issues:** N

---

## Baseline Reference

**Tagged Commit:** [tag]  
**Tag Date:** YYYY-MM-DD  
**Design Documents in Baseline:**
- design-0000-master.md (version X.X)
- [list all design documents]

---

## Verification Checklist

### Module: [Module Name]

**Design Reference:** design-NNNN-[name].md (version X.X from baseline)

| Design Element | Implementation File | Status | Notes |
|----------------|---------------------|--------|-------|
| Class X | src/module.py:L123 | ✓ PASS | Matches specification |
| Method Y | src/module.py:L456 | ✗ FAIL | Missing parameter Z |

**Design Specifications:**
- [ ] All classes implemented
- [ ] All methods implemented
- [ ] All functions implemented
- [ ] Correct signatures
- [ ] Error handling per spec
- [ ] Logging per spec

**Traceability:**
- [ ] Code header references design document
- [ ] Code header references requirements
- [ ] Design references present

**Test Coverage:**
- [ ] Unit tests exist
- [ ] Tests cover specifications
- [ ] Tests reference design

---

## Findings

### Compliant Implementations

1. **Module X:** Description
   - Evidence: Details

### Deviations

#### Critical Deviations

1. **Module Y, Element Z:** Description
   - Design Spec: Reference
   - Expected: Behavior
   - Actual: Behavior
   - Impact: Description

#### Minor Deviations

1. **Module A, Element B:** Description
   - Design Spec: Reference
   - Expected: Behavior
   - Actual: Behavior
   - Impact: Description

---

## Compliance Metrics

| Category | Total | Compliant | Deviation | % Compliant |
|----------|-------|-----------|-----------|-------------|
| Classes | N | N | N | XX% |
| Methods | N | N | N | XX% |
| Functions | N | N | N | XX% |
| Error Handling | N | N | N | XX% |
| Traceability | N | N | N | XX% |
| **Overall** | **N** | **N** | **N** | **XX%** |

---

## Recommendations

1. Action item
2. Action item
3. Action item

---

## Conclusion

[Summary and recommended actions]

---

**Next Audit:** [Date]  
**Approval:** [Signature]

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
