---
lf_schema: "operator_console/v1"
last_updated: 2026-02-19
audience: "end_user"
---

# Operator Console (Release / End Users)

This is the **safe, low-friction** way to run LitForge without requiring GitHub or shell scripts.

LitForge is an Obsidian vault. Your “operations” are simply:
1) keep the vault healthy
2) run the stage flow
3) take backups so you can’t lose work

## A) Daily safety check (30 seconds)

From vault root:

```bash
python tools/lf_integrity.py verify
tools/lfctl doctor
```

If either fails, stop and follow the tool’s “How to fix” instructions.

## B) Versioning without Git (recommended default)

If you don’t want GitHub:

1) Create a **whole-vault snapshot** (zip) at meaningful milestones:
   - after Outline passes
   - after a major Draft revision
   - after each Red-Team/Patch loop you want to keep
   - at Ship

2) Store snapshots somewhere safe (external drive or cloud).

**Recovery is simple:** unzip a snapshot and open it as an Obsidian vault.

## C) Optional Git for power users (pointer only)

If you already use Git, you can track your vault with version control.
LitForge does not require it and does not provide platform-specific automation in Release.

**We only provide pointers:**
- Git official docs
- GitHub docs (if you choose GitHub)

## D) When something feels broken

Run:
```bash
tools/lfctl doctor
```

Then:
- fix the first failure
- re-run doctor
- repeat until green

That’s the whole philosophy: **small fixes, verified fast.**
