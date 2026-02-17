#!/usr/bin/env python3
"""LitForge init-project — create a new project from template.

Security:
  - Only writes inside the newly created Projects/<n>/ directory.
  - Refuses to overwrite an existing directory.
  - Rejects control characters in project name.
  - Uses atomic writes for all file edits.
  - Kill switch honored before any work.

Exit codes: 0=success, 1=failure, 3=KILL_SWITCH
"""
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Shared imports ───────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lf_safe import (
    find_vault_root, check_kill_switch,
    atomic_write_text, assert_within_any, read_text_limited,
)

VAULT = find_vault_root()
check_kill_switch(VAULT)

# ── Args ─────────────────────────────────────────────────────────────
if len(sys.argv) < 2 or not sys.argv[1].strip():
    print("Usage: lfctl init-project \"My Project Name\"")
    sys.exit(1)

PROJECT_NAME = sys.argv[1].strip()

# ── Validate project name ────────────────────────────────────────────
FORBIDDEN_CHARS = set("/\\")
FORBIDDEN_NAMES = {".", "..", "_Project-Template"}

if any(c in FORBIDDEN_CHARS for c in PROJECT_NAME):
    print(f"ERROR: project name must not contain / or \\")
    print(f"  You gave: \"{PROJECT_NAME}\"")
    sys.exit(1)

if PROJECT_NAME in FORBIDDEN_NAMES:
    print(f"ERROR: \"{PROJECT_NAME}\" is a reserved name")
    sys.exit(1)

if PROJECT_NAME.startswith("_"):
    print(f"ERROR: project names starting with '_' are reserved for templates")
    print(f"  You gave: \"{PROJECT_NAME}\"")
    sys.exit(1)

if len(PROJECT_NAME) > 200:
    print("ERROR: project name too long (max 200 characters)")
    sys.exit(1)

# Block control characters (U+0000..U+001F, U+007F..U+009F)
if re.search(r"[\x00-\x1f\x7f-\x9f]", PROJECT_NAME):
    print("ERROR: project name contains control characters")
    print("  Use only printable characters.")
    sys.exit(1)

if not PROJECT_NAME:
    print("ERROR: project name cannot be empty")
    sys.exit(1)

# ── Paths ────────────────────────────────────────────────────────────
TEMPLATE_DIR = VAULT / "Projects" / "_Project-Template"
TARGET_DIR = VAULT / "Projects" / PROJECT_NAME

if not TEMPLATE_DIR.is_dir():
    print(f"FATAL: template not found: {TEMPLATE_DIR}")
    print("  Your vault may be incomplete. Run: tools/lfctl doctor")
    sys.exit(1)

if TARGET_DIR.exists():
    print(f"ERROR: directory already exists: Projects/{PROJECT_NAME}")
    print("  Choose a different name or remove the existing directory.")
    sys.exit(1)

# Enforce: target must resolve within Projects/
try:
    assert_within_any(
        VAULT / "Projects" / PROJECT_NAME,
        [VAULT / "Projects"],
    )
except PermissionError as exc:
    print(f"ERROR: {exc}")
    sys.exit(1)

# ── Generate project ID ─────────────────────────────────────────────
ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
PROJECT_ID = f"PROJ_{ts}"

# ── Copy template ────────────────────────────────────────────────────
try:
    shutil.copytree(TEMPLATE_DIR, TARGET_DIR)
except OSError as exc:
    print(f"FATAL: failed to copy template: {exc}")
    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR, ignore_errors=True)
    sys.exit(1)

# Write allowlist: only the newly created project dir
ALLOWED_WRITE_ROOTS = [TARGET_DIR]

# ── YAML field replacement helpers ───────────────────────────────────
def replace_yaml_field(text: str, key: str, new_value: str) -> str:
    pattern = re.compile(
        r'^(' + re.escape(key) + r':\s*)(".*?"|\'.*?\'|\S.*)$',
        re.MULTILINE,
    )
    safe_val = new_value.replace("\\", "\\\\").replace('"', '\\"')
    return pattern.sub(r'\g<1>"' + safe_val + '"', text, count=1)


def update_frontmatter_fields(path: Path, replacements: dict[str, str]) -> bool:
    text = read_text_limited(path)
    if text is None:
        print(f"  WARN: could not read {path.name}")
        return False

    m = re.match(r"^(---\n)(.*?)(\n---)(.*)", text, re.DOTALL)
    if not m:
        return False

    front = m.group(2)
    for key, val in replacements.items():
        front = replace_yaml_field(front, key, val)

    new_text = m.group(1) + front + m.group(3) + m.group(4)
    if new_text == text:
        return False

    atomic_write_text(path, new_text, allowed_roots=ALLOWED_WRITE_ROOTS)
    return True


# ── Update project config ────────────────────────────────────────────
cfg_path = TARGET_DIR / "00-Project-Config.md"
if cfg_path.is_file():
    update_frontmatter_fields(cfg_path, {
        "project_id": PROJECT_ID,
        "title": PROJECT_NAME,
    })
    text = read_text_limited(cfg_path)
    if text and "# Project Config — _Project-Template" in text:
        text = text.replace(
            "# Project Config — _Project-Template",
            f"# Project Config — {PROJECT_NAME}",
        )
        atomic_write_text(cfg_path, text, allowed_roots=ALLOWED_WRITE_ROOTS)

# ── Update stage files ───────────────────────────────────────────────
stage_dir = TARGET_DIR / "Stage"
if stage_dir.is_dir():
    for sf in sorted(stage_dir.glob("*.md")):
        update_frontmatter_fields(sf, {
            "project_id": PROJECT_ID,
            "project_title": PROJECT_NAME,
        })

# ── Update Stage Index (best effort) ────────────────────────────────
idx_path = TARGET_DIR / "00-Stage-Index.md"
idx_updated = False
if idx_path.is_file():
    text = read_text_limited(idx_path)
    if text and "_Project-Template" in text:
        text = text.replace("_Project-Template", PROJECT_NAME)
        try:
            atomic_write_text(idx_path, text, allowed_roots=ALLOWED_WRITE_ROOTS)
            idx_updated = True
        except OSError:
            pass

# ── Success output ───────────────────────────────────────────────────
print("=" * 55)
print("  Project created successfully!")
print("=" * 55)
print()
print(f"  Name:       {PROJECT_NAME}")
print(f"  ID:         {PROJECT_ID}")
print(f"  Location:   Projects/{PROJECT_NAME}/")
print()
if not idx_updated:
    print("  WARN: 00-Stage-Index.md did not contain template title;")
    print("        update it manually if you want a custom heading.")
    print()
print("  Next steps:")
print(f"    1. Open Projects/{PROJECT_NAME}/Stage/01-Discover.md")
print( "    2. Fill in the Concept Snapshot and Constraints")
print( "    3. Check the acceptance boxes when done")
print( "    4. Run: tools/lfctl lint")
print()
sys.exit(0)
