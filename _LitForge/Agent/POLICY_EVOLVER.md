# POLICY — EVOLVER (STRICT PROFILE)

This policy applies ONLY to the Evolver runtime. It is stricter than POLICY.md.

## Non-negotiables
- Vault is mounted READ-ONLY at runtime.
- Network is DISABLED (Docker --network none).
- NO shell execution, NO browsing, NO messaging.
- Evolver may only PROPOSE changes as patch files and reports.
- Human applies patches manually using `lfctl apply <patchfile>`.

## Allowed writes (ONLY)
- `_LitForge/_DEV_PATCHES/`  (unified diffs / patch proposals)
- `_LitForge/_DEV_REPORTS/`  (run logs, lint/replay results)

## Forbidden
- Writing anywhere else in the vault.
- Modifying `_LitForge/Engine/` directly.
- Modifying templates/modes directly.
- Touching `.obsidian/` or any credential-like files.
- Expanding tool permissions.

## Required workflow
1) Read inputs (allowlisted paths only)
2) Produce patch -> write to `_DEV_PATCHES`
3) Run `lfctl lint` and `lfctl replay` -> write results to `_DEV_REPORTS`
4) STOP
