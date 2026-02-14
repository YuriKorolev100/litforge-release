#!/usr/bin/env python3
"""LitForge doctor — vault health check for writers.

Checks:
  1. Vault root (must find _LitForge/ and Projects/)
  2. Python version (>= 3.10 recommended)
  3. PyYAML importable
  4. Required LitForge files present
  5. Git repo present and working tree clean

Exit codes: 0=PASS (warnings ok), 1=FAIL, 2=missing deps, 3=KILL_SWITCH
"""
import os
import subprocess
import sys
from pathlib import Path

# ── Resolve vault root ───────────────────────────────────────────────
VAULT = None
candidate = Path(__file__).resolve().parent
for _ in range(10):
    if (candidate / "_LitForge").is_dir():
        VAULT = candidate
        break
    parent = candidate.parent
    if parent == candidate:
        break
    candidate = parent

if VAULT is None:
    print("FATAL: cannot locate _LitForge/ in ancestors of this script")
    print("  Are you running from inside the LitForge vault?")
    sys.exit(1)

# ── Kill switch (fail-closed, before ANY work) ───────────────────────
KS = VAULT / "_LitForge" / "Agent" / "KILL_SWITCH.flag"
if KS.exists():
    print(f"ABORT: kill switch active  ({KS})")
    sys.exit(3)

# ── State ────────────────────────────────────────────────────────────
passes: list[str] = []
warns:  list[str] = []
fails:  list[str] = []
fixes:  list[str] = []
dep_missing = False

def ok(msg: str) -> None:
    passes.append(msg)

def warn(msg: str) -> None:
    warns.append(msg)

def fail(msg: str, fix: str = "") -> None:
    fails.append(msg)
    if fix:
        fixes.append(fix)


# ══════════════════════════════════════════════════════════════════════
# 1. Vault root
# ══════════════════════════════════════════════════════════════════════
if (VAULT / "_LitForge").is_dir() and (VAULT / "Projects").is_dir():
    ok("Vault root found: _LitForge/ and Projects/ present")
else:
    if not (VAULT / "_LitForge").is_dir():
        fail("_LitForge/ directory not found at vault root")
    if not (VAULT / "Projects").is_dir():
        fail("Projects/ directory not found at vault root")

# ══════════════════════════════════════════════════════════════════════
# 2. Python version
# ══════════════════════════════════════════════════════════════════════
py_major, py_minor = sys.version_info[:2]
if (py_major, py_minor) >= (3, 10):
    ok(f"Python {py_major}.{py_minor} (>= 3.10)")
else:
    warn(
        f"Python {py_major}.{py_minor} detected — 3.10+ recommended. "
        "Older versions may work but are untested."
    )

# ══════════════════════════════════════════════════════════════════════
# 3. PyYAML
# ══════════════════════════════════════════════════════════════════════
try:
    import yaml  # noqa: F401
    ok("PyYAML importable")
except ImportError:
    dep_missing = True
    fail(
        "PyYAML not installed",
        "Install PyYAML (pick ONE method):\n"
        "\n"
        "  # Recommended — use a venv (any OS):\n"
        "  python3 -m venv .venv\n"
        "  source .venv/bin/activate      # bash/zsh\n"
        "  # .venv\\Scripts\\activate.bat  # Windows cmd\n"
        "  pip install pyyaml\n"
        "\n"
        "  # Arch Linux system package:\n"
        "  sudo pacman -S python-yaml\n"
        "\n"
        "  # macOS / generic:\n"
        "  pip install --user pyyaml\n"
    )

# ══════════════════════════════════════════════════════════════════════
# 4. Required files
# ══════════════════════════════════════════════════════════════════════
REQUIRED_FILES = [
    "_LitForge/Setup/00-Setup-Wizard.md",
    "_LitForge/Setup/01-Capability-Check.md",
    "_LitForge/Setup/02-Safety-Fence.md",
    "_LitForge/Dashboard.md",
    "tools/lf_lint.py",
    "tools/lf_replay.py",
]

missing_files: list[str] = []
for rel in REQUIRED_FILES:
    if (VAULT / rel).is_file():
        ok(f"Found {rel}")
    else:
        missing_files.append(rel)
        fail(f"Missing required file: {rel}")

if missing_files:
    fixes.append(
        "Missing files may indicate a corrupt or incomplete vault.\n"
        "  Re-clone or restore from backup, then re-run: tools/lfctl doctor"
    )

# ══════════════════════════════════════════════════════════════════════
# 5. Git repo + clean working tree
# ══════════════════════════════════════════════════════════════════════
git_dir = VAULT / ".git"
if git_dir.exists():
    ok("Git repository found (.git/ present)")
    # Check working tree — read-only, safe: just `git status --porcelain`
    try:
        result = subprocess.run(
            ["git", "-C", str(VAULT), "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            if result.stdout.strip():
                dirty_count = len(result.stdout.strip().splitlines())
                warn(
                    f"Git working tree has {dirty_count} uncommitted change(s). "
                    "Consider committing before running LitForge stages."
                )
            else:
                ok("Git working tree clean")
        else:
            warn("Could not read git status (git returned non-zero)")
    except FileNotFoundError:
        warn("'git' command not found — cannot check working tree")
    except subprocess.TimeoutExpired:
        warn("git status timed out")
else:
    warn(
        "No .git/ directory found. "
        "Version control is strongly recommended.\n"
        "         Initialize with: git init && git add -A && git commit -m 'init'"
    )

# ══════════════════════════════════════════════════════════════════════
# Report
# ══════════════════════════════════════════════════════════════════════
print("=" * 55)
print("  LitForge Doctor")
print("=" * 55)
print(f"  Vault: {VAULT}")
print()

idx = 0
for p in passes:
    idx += 1
    print(f"  {idx}. PASS  {p}")
for w in warns:
    idx += 1
    print(f"  {idx}. WARN  {w}")
for f in fails:
    idx += 1
    print(f"  {idx}. FAIL  {f}")

print()
print("-" * 55)

if fixes:
    print()
    print("  How to fix:")
    for i, fix in enumerate(fixes, 1):
        # Indent multiline fix text
        lines = fix.splitlines()
        print(f"  {i}) {lines[0]}")
        for line in lines[1:]:
            print(f"     {line}")
    print()

n_f, n_w = len(fails), len(warns)
if dep_missing:
    print(f"  RESULT: BLOCKED — missing dependencies ({n_f} fail, {n_w} warn)")
    print("  Fix the above, then re-run: tools/lfctl doctor")
    sys.exit(2)
elif fails:
    print(f"  RESULT: FAIL  ({n_f} fail, {n_w} warn)")
    print("  Fix the above, then re-run: tools/lfctl doctor")
    sys.exit(1)
else:
    print(f"  RESULT: ALL CLEAR  ({n_w} warning(s))")
    if warns:
        print("  Warnings are non-blocking but worth reviewing.")
    print()
    print("  You're ready to write. Start with:")
    print("    tools/lfctl init-project \"My Project Name\"")
    sys.exit(0)
