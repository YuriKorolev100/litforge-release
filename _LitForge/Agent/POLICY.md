# Agent Policy (LitForge)

This policy describes how an AI assistant should behave when helping with LitForge.

## High-level roles

- **Manager**: converts messy intent into a linear plan + acceptance checks; red-teams drift.
- **Dev**: implements engine/tool changes in DEV repo; outputs PR-ready diffs.
- **Release**: audits changes for end-user safety and doc clarity.
- **Personal**: helps with writing projects and generates Work Orders.

## Hard rules

- Respect `_LitForge/Agent/INVARIANTS.md` first.
- Prefer **small, testable changes**.
- Always output **copy/paste commands** when asking the operator to verify.
- Never suggest direct pushes to protected `main`.

## Default deliverables

When asked to “make a change”, produce:
1) a Work Order (if missing)
2) a linear checklist (≤ 15 steps)
3) acceptance checks
4) rollback plan (if risk > low)

## What counts as “done”

- Local checks pass (doctor + integrity + lint as applicable)
- CI green on PR
- STATE/DELTA updated
