# Repo Model and Sync Workflow

LitForge is split to protect your IP and keep the product clean.

## The 3 repos

### 1) Release (product)
**Repo:** `litforge-release` (public)  
Contains:
- `_LitForge/` engine templates + docs for end users
- `tools/` python tools (doctor/lint/integrity/replay/lfctl)
- `.github/workflows/` CI gates

Must NOT contain:
- dev-only ops scripts
- experimental tooling
- personal writing projects
- any private research packets

### 2) Dev (engine evolver)
**Repo:** `litforge-dev` (public)  
Contains:
- experiments, prototypes, hardening work
- optional automation scripts (may include shell)
- docs for maintainers

May be “less strict” because it’s not shipped to users.

### 3) Personal (working vault)
**Repo:** `litforge-personal` (private)  
Contains:
- your actual writing + research packets
- your session logs (STATE/DELTA)
- work orders that spawn engine improvements

## The sync rule

**Only Release is the product.**  
Dev exists to evolve Release.  
Personal consumes Release and generates improvements.

Direction:
- Dev → (PR) → Release
- Release → (sync) → Personal (engine updates only)
- Personal → (Work Orders) → Dev (requirements, bugs, UX pain)

## Anti-drift session ritual

Every maintainer session uses three artifacts:
- `_LitForge/Sync/STATE.md` — snapshot of current reality
- `_LitForge/Sync/DELTA.md` — what changed this session (diff narrative)
- `_LitForge/WorkOrders/*.md` — one work order per change request

See: `_LitForge/Sync/00-Sync-Protocol.md`
