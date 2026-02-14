# LitForge Release Checklist

> For maintainers. Covers integrity management, CI validation,
> and what must be committed for a clean release.


## Engine integrity manifest

The file `_LitForge/Engine/INTEGRITY.sha256` contains SHA-256 hashes
for every tracked engine file. It covers:

- `_LitForge/Engine/**` (manifest, modes, schemas)
- `_LitForge/Setup/**` (wizard, capability check, safety fence)
- `_LitForge/Templates/**` (all eight backbone stage templates)
- `_LitForge/Dashboard.md`
- `tools/**` (all Python scripts and lfctl)

The manifest excludes `__pycache__/`, `.pyc`, `.git/`, `.venv/`,
and itself (`INTEGRITY.sha256`).


### Verifying integrity

```bash
tools/lfctl integrity verify
```

This compares every listed file's current hash against the manifest.
It also detects untracked files in covered directories (new files
added but not yet in the manifest).

Exit 0 = all hashes match. Exit 1 = mismatch, missing, or untracked files.

Quiet mode for scripting (no output on success, nonzero on failure):

```bash
tools/lfctl integrity verify --quiet
```

Both `lint` and `doctor` call integrity verify internally — if the
manifest is stale, lint fails and doctor reports a FAIL line.


### Regenerating the manifest

**Only do this when you intentionally changed engine files.**
Never regenerate to "fix" an unexpected mismatch — investigate first.

```bash
# 1. Verify you understand what changed
git diff --stat

# 2. Regenerate
tools/lfctl integrity update --i-understand

# 3. Verify the new manifest
tools/lfctl integrity verify

# 4. Commit the manifest alongside the files it covers
git add _LitForge/Engine/INTEGRITY.sha256
git add <the files you changed>
git commit -m "engine: update X, regenerate integrity manifest"
```

The `--i-understand` flag is a speed bump, not security — it exists to
prevent accidental regeneration. The manifest must always be committed
in the same commit as the engine changes it covers.


### Rules

1. **Never commit a stale manifest.** If you change any tracked file,
   regenerate before committing.
2. **Never regenerate to paper over unknown changes.** If integrity
   fails and you didn't change anything, something is wrong — check
   `git status` and `git diff`.
3. **CI blocks on integrity failure.** A PR with a stale manifest
   will not pass the pipeline.
4. **The manifest itself is not self-referential.** It does not
   contain its own hash (would create a circular dependency).


## What must be committed

For any release or PR, these must all be present and consistent:

| Item | Path | Notes |
|------|------|-------|
| Integrity manifest | `_LitForge/Engine/INTEGRITY.sha256` | Matches all tracked files |
| Dashboard | `_LitForge/Dashboard.md` | Canonical term: always "Dashboard" |
| All 8 templates | `_LitForge/Templates/01-Discover.md` … `08-Ship.md` | Backbone order is immutable |
| Setup files | `_LitForge/Setup/00-Setup-Wizard.md`, `01-Capability-Check.md`, `02-Safety-Fence.md` | Required by lint + doctor |
| Engine manifest | `_LitForge/Engine/litforge.manifest.yaml` | Required by lint |
| All tools | `tools/lf_*.py`, `tools/lfctl` | Covered by integrity |
| Tests | `tests/test_safe.py` | Run by CI |
| CI config | `.github/workflows/litforge-ci.yml` | Must match current tool names |


## CI pipeline validation

The GitHub Actions workflow (`.github/workflows/litforge-ci.yml`)
runs four steps in order:

1. **Unit tests** — `python -m unittest discover -s tests -v`
2. **Integrity verify** — `python tools/lf_integrity.py verify`
3. **Lint** — `python tools/lf_lint.py .`
4. **Replay** — `python tools/lf_replay.py "Projects/EXAMPLE - Tiny Loop Demo"`

All four must pass. If any step fails, the pipeline fails.

To run the same checks locally before pushing:

```bash
python3 -m unittest discover -s tests -v
tools/lfctl integrity verify
tools/lfctl lint
tools/lfctl replay "Projects/EXAMPLE - Tiny Loop Demo"
```


## Pre-release checklist

```
[ ] git status is clean (no uncommitted changes to tracked files)
[ ] tools/lfctl doctor reports ALL CLEAR
[ ] tools/lfctl integrity verify reports PASS
[ ] tools/lfctl lint reports PASS
[ ] tools/lfctl replay reports PASS for every project in Projects/
[ ] python3 -m unittest discover -s tests -v reports 0 failures
[ ] INTEGRITY.sha256 committed with any engine changes
[ ] No Criticals open in any project claiming shipped status
[ ] Kill switch flag does NOT exist (_LitForge/Agent/KILL_SWITCH.flag)
```


## Invariants to preserve

These are non-negotiable across any release. Violating them is a
ship-blocker.

1. **Backbone order is immutable.**
   Discover → Position → Outline → Draft → Red-Team → Patch → Repeat → Ship.
   Templates must exist for all eight. No stages can be added, removed,
   or reordered.

2. **Red-Team moat is immutable.**
   Hostile audit → patch spec → diff-first → regression → gate.
   Replay enforces this chain. Ship requires at least one completed cycle.

3. **Ship gates cannot be loosened, only tightened.**
   `ship_requires_redteam_cycles` minimum is 1. `criticals_open` maximum
   is 0. Overrides must be explicit in YAML and produce warnings, not
   silent bypasses.

4. **"Dashboard" is the canonical term.**
   Never "Cockpit", never "Control Panel". Lint checks for this.

5. **No network. No plugins. No arbitrary execution.**
   All tools are stdlib + PyYAML. No tool makes network calls. No
   Obsidian plugin is required to use LitForge.


## Adding or modifying engine files

If you add a new file under any tracked directory (`_LitForge/Engine/`,
`_LitForge/Setup/`, `_LitForge/Templates/`, `tools/`), or modify
`_LitForge/Dashboard.md`:

```bash
# 1. Make your changes

# 2. Run lint to check nothing else broke
tools/lfctl lint
# (this will FAIL on integrity — expected)

# 3. Regenerate integrity
tools/lfctl integrity update --i-understand

# 4. Verify
tools/lfctl integrity verify

# 5. Re-run lint (should now pass)
tools/lfctl lint

# 6. Run full test suite
python3 -m unittest discover -s tests -v

# 7. Commit everything together
git add -A
git commit -m "engine: <describe change>"
```

If you are only changing files outside the tracked directories
(e.g. project content in `Projects/`, docs in `docs/`), the integrity
manifest is unaffected and does not need regeneration.


## Exit code reference

| Code | Meaning |
|------|---------|
| 0 | PASS / success |
| 1 | FAIL / validation errors |
| 2 | Missing dependency (PyYAML) |
| 3 | Kill switch active — all work aborted |
