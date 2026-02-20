# DEV Operator Console (Maintainers Only)

> **DEV-only. Not shipped to end users.**  
> This console may use bash, git automation, and other maintainer conveniences.
> Anything in this file is allowed to exist only in DEV/PERSONAL, never as a Release dependency.

---

---
lf_schema: "operator_console/v1"
last_updated: 2026-02-16
---

# Operator Console (PROD)

This turns LitForge into **human-in-the-loop autopilot**:
- you never push broken work
- you never lose changes
- you approve/deny pushes using PRs (GitHub becomes your “approval gate”)

> Goal: **one command per day**: `bash ops/pr.sh`

---

## A) One-time setup (local)

From vault root:

```bash
bash ops/bootstrap.sh
```

What this does (local-only, no network):
- fixes executable permissions on scripts (zip often drops them)
- enables version-controlled git hooks via `core.hooksPath=.githooks`
  - **pre-commit:** blocks commits if `tools/lfctl lint` fails
  - **pre-push:** blocks pushes if `doctor/lint/integrity` fails

If you ever want to disable hooks:
```bash
git config --unset core.hooksPath
```

---

## B) One-time setup (GitHub link)

Recommended: create a **private** repo for PROD (Kraken + RPN drafts are content).

```bash
bash ops/link_github.sh
```

It will:
- ensure `gh` (GitHub CLI) is installed/authenticated
- create or connect to a repo
- set `origin`
- push your current branch

If you want to verify manually:
```bash
git remote -v
```

---

## C) Daily operation (you do this every work session)

From vault root:

```bash
bash ops/pr.sh
```

What happens:
1) Runs LitForge gates: doctor → lint → integrity verify
2) Shows git diff summary
3) Asks: **commit these changes?** (y/n)
4) If yes: commits to a new branch + pushes
5) Opens a PR (GitHub) → you approve/merge there

This is your **approve/deny loop**.

---

## D) “Agentic” loop with external models (patch-only)

Use when you want the model to propose changes without writing your vault directly.

1) Build a bounded packet for the model:
```bash
bash ops/packet.sh "Projects/RPN - 2026-02-15 - Episode 0 - Channel Constitution"
```

2) Upload the generated zip to ChatGPT/Claude.

3) Ask for **unified diff only** output.

4) Save the diff as `Patches/diffs/<name>.patch` and apply:
```bash
bash ops/apply_patch.sh "Projects/RPN - 2026-02-15 - Episode 0 - Channel Constitution/Patches/diffs/<name>.patch"
```

Then run your gates (or just run `bash ops/pr.sh` which runs them anyway).

---

## E) Troubleshooting

### “Permission denied” on scripts
```bash
bash ops/bootstrap.sh
```

### “I committed but don’t see it on GitHub”
You committed locally. You still need a remote + push:
```bash
git remote -v
git push -u origin <branch>
```

But you should just use:
```bash
bash ops/link_github.sh
bash ops/pr.sh
```
