# Work Order — <short title>

**WO ID:** WO-YYYYMMDD-HHMM-<slug>  
**Owner:** Vadim  
**Target repo:** DEV | RELEASE | PERSONAL  
**Priority:** P0 | P1 | P2  
**Risk:** Low | Medium | High  
**Mode packs affected:** (if any)

---

## Problem (what hurts)

Describe the pain in 3–8 lines:
- What you tried to do
- What happened
- Why it’s bad

## Goal (what “good” looks like)

A concrete outcome the user can observe.

## Constraints (non-negotiable)

Examples:
- No network calls
- Python-only tools (Release)
- Vault boundary only (no reads/writes outside vault)
- Must keep canonical backbone stages

## Proposed change (minimal)

What to change (files, behavior). Keep it small.

## Acceptance checks (copy/paste)

Local:
```bash
# from repo root
python tools/lf_integrity.py verify
tools/lfctl doctor
tools/lfctl lint
```

CI:
- GitHub Actions on main must pass
- No new warnings introduced (unless justified)

## Notes / rationale

Anything that helps implementation or prevents drift.
