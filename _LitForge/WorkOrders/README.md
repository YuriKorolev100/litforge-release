# Work Orders

A Work Order is the **unit of change** in LitForge maintenance.

One Work Order should become:
- one PR (preferred), or
- one clearly scoped series of PRs.

## When to write a Work Order

Write a WO when:
- something is confusing for a real user
- a tool fails or is fragile
- docs are missing or misleading
- a gate needs a clearer error message
- a new mode pack/check is requested

## Routing

- **Release WO**: end-user safety/UX changes; python-only; no network.
- **Dev WO**: maintainer tooling; may allow more power.
- **Personal WO**: your writing workflow pain → becomes Dev/Release WO.

## Definition of Done

A WO is done when:
- acceptance checks are explicit and pass locally
- CI passes on the PR
- doc updates are included if behavior changed
- STATE/DELTA updated
