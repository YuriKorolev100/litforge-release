# ChatGPT Projects + Codex Workflow (Maintainers)

This doc describes how to run LitForge maintenance using **ChatGPT Projects** and **Codex** while keeping a clean, repeatable workflow.

## The 4 project “workspaces” (ChatGPT Projects)

You created:
1) **LF — MANAGER** (orchestrator)
2) **LF — DEV** (engine evolution)
3) **LF — RELEASE** (product hardening + public docs)
4) **LF — PERSONAL** (your writing vault assistance)

### What each workspace is for

**MANAGER**
- Keeps the master plan
- Enforces “3 actions per loop”
- Turns messy work into a linear checklist
- Maintains STATE/DELTA discipline
- Red-teams proposals before they touch code

**DEV**
- Implements requested engine/tool changes (code + templates)
- Outputs PR-ready diffs
- Never touches personal IP

**RELEASE**
- Reviews changes for end-user safety posture
- Ensures “no bash required”, “no network”, “vault boundary”
- Polishes docs and onboarding

**PERSONAL**
- Helps run your writing projects inside the vault
- Produces Work Orders when the engine hurts

## What to attach to each workspace (minimum)

Attach these files (drag-drop):
- `_LitForge/Agent/INVARIANTS.md`
- `_LitForge/Agent/POLICY.md`
- `_LitForge/Operator/06-Sync-and-Repo-Model.md`
- `_LitForge/Sync/STATE.md`
- `_LitForge/Sync/DELTA.md`
- `_LitForge/WorkOrders/WO-TEMPLATE.md`

Optionally attach:
- `_LitForge/Sync/00-Sync-Protocol.md`
- `_LitForge/WorkOrders/README.md`

## The “Work Order → PR” loop (linear)

1) In PERSONAL: write a Work Order (`_LitForge/WorkOrders/WO-YYYYMMDD-HHMM-<slug>.md`)
2) In MANAGER: turn it into **exact acceptance tests** + **exact commands**
3) In DEV or RELEASE: implement
4) Run locally:
   - `python tools/lf_integrity.py verify`
   - `tools/lfctl doctor`
   - `tools/lfctl lint`
5) Push branch + open PR (never push to protected main)
6) Merge after CI passes
7) Sync Release → Personal engine files
8) Update STATE + DELTA

## Why this helps speed

The speed comes from:
- one artifact per request (Work Order)
- one authoritative checklist (Manager)
- one PR per change (small deltas)
- one ritual for verification (doctor + integrity + CI)
