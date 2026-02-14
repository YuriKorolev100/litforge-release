#!/usr/bin/env python3
"""LitForge init-project — create a new project from template.

Copies Projects/_Project-Template/ to Projects/<name>/ and updates
YAML frontmatter with the new project identity.

Security:
  - Only writes inside the newly created Projects/<name>/ directory.
  - Refuses to overwrite an existing directory.
  - No network, no shell, no auto-apply.
  - Kill switch honored before any work.

Exit codes: 0=success, 1=failure, 3=KILL_SWITCH
"""
import re
import shutil
import sys
from datetime import datetime, timezone
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
    sys.exit(1)

# ── Kill switch ──────────────────────────────────────────────────────
KS = VAULT / "_LitForge" / "Agent" / "KILL_SWITCH.flag"
if KS.exists():
    print(f"ABORT: kill switch active  ({KS})")
    sys.exit(3)

# ── Args ─────────────────────────────────────────────────────────────
if len(sys.argv) < 2 or not sys.argv[1].strip():
    print("Usage: lfctl init-project \"My Project Name\"")
    sys.exit(1)

PROJECT_NAME = sys.argv[1].strip()

# ── Validate project name ────────────────────────────────────────────
# Fail closed: reject anything that could escape Projects/ or cause
# filesystem trouble.  No auto-sanitization — writer must fix it.
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

# ── Generate project ID ─────────────────────────────────────────────
ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
PROJECT_ID = f"PROJ_{ts}"

# ── Copy template ────────────────────────────────────────────────────
try:
    shutil.copytree(TEMPLATE_DIR, TARGET_DIR)
except OSError as exc:
    print(f"FATAL: failed to copy template: {exc}")
    # Clean up partial copy — fail closed
    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR, ignore_errors=True)
    sys.exit(1)

# ── YAML field replacement helpers ───────────────────────────────────
# We do targeted text replacement on YAML frontmatter lines to avoid
# reformatting the file.  This is intentionally conservative.

def replace_yaml_field(text: str, key: str, new_value: str) -> str:
    """Replace a top-level YAML scalar field's value in frontmatter text.

    Matches lines like:  key: "old"  or  key: old
    Replaces with:       key: "new_value"
    Only operates within the first --- / --- fence.
    """
    # Pattern: start of line, the key, colon, optional space, then value
    pattern = re.compile(
        r'^(' + re.escape(key) + r':\s*)(".*?"|\'.*?\'|\S.*)$',
        re.MULTILINE,
    )
    return pattern.sub(r'\g<1>"' + new_value.replace("\\", "\\\\").replace('"', '\\"') + '"', text, count=1)


def update_frontmatter_fields(path: Path, replacements: dict[str, str]) -> bool:
    """Apply YAML field replacements inside the frontmatter of a markdown file.

    Returns True if the file was modified.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"  WARN: could not read {path.name}: {exc}")
        return False

    m = re.match(r"^(---\n)(.*?)(\n---)(.*)", text, re.DOTALL)
    if not m:
        return False  # no frontmatter

    front = m.group(2)
    for key, val in replacements.items():
        front = replace_yaml_field(front, key, val)

    new_text = m.group(1) + front + m.group(3) + m.group(4)
    if new_text == text:
        return False

    path.write_text(new_text, encoding="utf-8")
    return True


# ── Update project config ────────────────────────────────────────────
cfg_path = TARGET_DIR / "00-Project-Config.md"
if cfg_path.is_file():
    update_frontmatter_fields(cfg_path, {
        "project_id": PROJECT_ID,
        "title": PROJECT_NAME,
    })
    # Also update the body heading if it references the template name
    try:
        text = cfg_path.read_text(encoding="utf-8")
        text = text.replace(
            "# Project Config — _Project-Template",
            f"# Project Config — {PROJECT_NAME}",
        )
        cfg_path.write_text(text, encoding="utf-8")
    except OSError:
        pass  # non-fatal — cosmetic

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
    try:
        text = idx_path.read_text(encoding="utf-8")
        if "_Project-Template" in text:
            text = text.replace("_Project-Template", PROJECT_NAME)
            idx_path.write_text(text, encoding="utf-8")
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
