# LitForge Quickstart

> For writers on Arch Linux using Obsidian.
> No plugins required. No network required. Everything runs locally.


## Prerequisites

You need Python 3.10+ and PyYAML. On Arch:

```bash
# Check Python version (3.10 or newer required)
python3 --version

# Install PyYAML — pick ONE method:

# System package (simplest on Arch):
sudo pacman -S python-yaml

# Or use a venv (any OS):
cd /path/to/LitForge-DEV
python3 -m venv .venv
source .venv/bin/activate
pip install pyyaml
```

Make the CLI tool executable (one-time):

```bash
chmod +x tools/lfctl
```

You also need Git. Arch ships it or: `sudo pacman -S git`.


## 1. Check vault health

Run this from the vault root (the folder you opened in Obsidian):

```bash
cd /path/to/LitForge-DEV
tools/lfctl doctor
```

You should see numbered PASS lines and a final `RESULT: ALL CLEAR`.
If anything shows FAIL, the doctor prints fix instructions — follow them
and re-run until clear.


## 2. Create your first project

```bash
tools/lfctl init-project "My First Essay"
```

This copies the project template into `Projects/My First Essay/` and
sets up all eight stage files with a unique project ID.

Open Obsidian, navigate to `Projects/My First Essay/Stage/01-Discover.md`,
and start writing.


## 3. Work through the backbone

LitForge enforces a fixed stage order. You work through them one at a time:

    Discover → Position → Outline → Draft → Red-Team → Patch → Repeat → Ship

Each stage file lives in `Projects/<name>/Stage/` and has:
- YAML frontmatter (status, gate rules — leave this alone until you understand it)
- Sections to fill in (concept, constraints, findings, etc.)
- Acceptance test checkboxes at the bottom

Your workflow for each stage:
1. Open the stage file in Obsidian
2. Fill in the required sections
3. Check the acceptance boxes when done
4. Set `status: approved` in the frontmatter
5. Move to the next stage


## 4. Validate your work

After editing, run the linter to catch structural or schema problems:

```bash
tools/lfctl lint
```

`RESULT: PASS` means you're good. `RESULT: FAIL` lists what to fix —
each error names the file and field.


## 5. Verify the Red-Team moat

Once you've been through Red-Team → Patch → Repeat, verify the full
chain is intact:

```bash
tools/lfctl replay "Projects/My First Essay"
```

This checks five things in order:
1. `05-Red-Team.md` has findings with severity grades (hostile audit)
2. `Patches/PatchSpec_*.md` exists (patch spec)
3. `Patches/diffs/*.patch` exists (diff-first)
4. `07-Repeat.md` has completed regression checkboxes (regression)
5. Ship gate math: enough Red-Team cycles, no unresolved Criticals (gate)

All five must pass before Ship can be approved.


## The kill switch

If something goes wrong and you need all tooling to stop immediately:

```bash
touch _LitForge/Agent/KILL_SWITCH.flag
```

Every command — `doctor`, `lint`, `replay`, `init-project`, `integrity` —
checks for this file before doing anything. If it exists, the tool prints
`ABORT: kill switch active` and exits with code 3. No checks run, no
files are written.

To resume normal operation:

```bash
rm _LitForge/Agent/KILL_SWITCH.flag
```


## Complete first-project walkthrough

```bash
# 1. Health check
tools/lfctl doctor

# 2. Create project
tools/lfctl init-project "My First Essay"

# 3. (Open Obsidian, fill in Stage/01-Discover.md through 08-Ship.md)

# 4. Validate structure + schemas
tools/lfctl lint

# 5. Verify moat chain (after Red-Team cycle)
tools/lfctl replay "Projects/My First Essay"
```


## Command reference

| Command | What it does | Exit 0 | Exit 1 | Exit 3 |
|---------|-------------|--------|--------|--------|
| `tools/lfctl doctor` | Check deps, structure, git, integrity | ALL CLEAR | FAIL | Kill switch |
| `tools/lfctl init-project "Name"` | Scaffold a new project | Created | Error | Kill switch |
| `tools/lfctl lint` | Validate schemas + gates + integrity | PASS | FAIL | Kill switch |
| `tools/lfctl replay "Projects/Name"` | Verify Red-Team moat chain | PASS | FAIL | Kill switch |
| `tools/lfctl integrity verify` | Check engine file hashes | PASS | FAIL | Kill switch |

Exit code 2 means a missing dependency (usually PyYAML).


## Terminology

- **Dashboard** — the central navigation file (`_LitForge/Dashboard.md`).
  Always called Dashboard, never anything else.
- **Backbone** — the eight immutable stages from Discover to Ship.
- **Moat** — the Red-Team enforcement chain that replay verifies.
- **Gate** — conditions that must be met before Ship can be approved
  (minimum Red-Team cycles, zero unresolved Criticals).


## Troubleshooting

**"FATAL: cannot locate _LitForge/"**
You're running `tools/lfctl` from outside the vault. `cd` into the vault
root first — the directory that contains `_LitForge/` and `Projects/`.

**"FATAL: PyYAML required"**
Install it: `sudo pacman -S python-yaml` or use a venv (see Prerequisites).

**"ABORT: kill switch active"**
Someone (possibly you) created `_LitForge/Agent/KILL_SWITCH.flag`.
If it's safe to proceed: `rm _LitForge/Agent/KILL_SWITCH.flag`.

**"INTEGRITY FAIL"**
Engine files were modified outside the normal workflow. If intentional,
ask a maintainer to regenerate the manifest (see RELEASE_CHECKLIST.md).
If not, restore from git: `git checkout _LitForge/`.

**Lint shows schema errors after init-project**
The project template's stage files have placeholder values. Fill in
the required sections and set correct `status` values as you work
through each stage.
