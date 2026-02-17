#!/usr/bin/env python3
"""LitForge engine integrity checker.

Commands:
  verify [--quiet]        Check file hashes against INTEGRITY.sha256
  update --i-understand   Regenerate the manifest (human-initiated only)

Covers: _LitForge/Engine/**, _LitForge/Setup/**, _LitForge/Templates/**,
        _LitForge/Dashboard.md, tools/**

Exit codes: 0=PASS, 1=FAIL, 3=KILL_SWITCH
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lf_safe import find_vault_root, check_kill_switch, sha256_file

VAULT = find_vault_root()
check_kill_switch(VAULT)

MANIFEST_PATH = VAULT / "_LitForge" / "Engine" / "INTEGRITY.sha256"

# Files/dirs to exclude from manifest
EXCLUDE_NAMES = {"__pycache__", ".pyc", ".git", ".venv", ".DS_Store"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


def _should_skip(p: Path) -> bool:
    """True if this path should be excluded from integrity tracking."""
    if p.name in EXCLUDE_NAMES:
        return True
    if p.suffix in EXCLUDE_SUFFIXES:
        return True
    if any(part in EXCLUDE_NAMES for part in p.parts):
        return True
    # Exclude the manifest itself
    if p.resolve() == MANIFEST_PATH.resolve():
        return True
    return False


def _covered_files() -> list[Path]:
    """Return sorted list of files under covered directories."""
    roots = [
        VAULT / "_LitForge" / "Engine",
        VAULT / "_LitForge" / "Setup",
        VAULT / "_LitForge" / "Templates",
        VAULT / "tools",
    ]
    singles = [
        VAULT / "_LitForge" / "Dashboard.md",
    ]
    files: list[Path] = []
    for root in roots:
        if root.is_dir():
            for p in sorted(root.rglob("*")):
                if p.is_file() and not _should_skip(p):
                    files.append(p)
    for s in singles:
        if s.is_file() and not _should_skip(s):
            files.append(s)
    return sorted(set(files))


def _parse_manifest() -> dict[str, str]:
    """Parse INTEGRITY.sha256 → {relative_path: expected_hash}."""
    if not MANIFEST_PATH.is_file():
        return {}
    entries: dict[str, str] = {}
    for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)  # sha256sum format: "hash  path"
        if len(parts) != 2:
            continue
        entries[parts[1]] = parts[0]
    return entries


def cmd_verify(quiet: bool = False) -> int:
    """Verify all tracked files.  Returns 0=pass, 1=fail."""
    if not MANIFEST_PATH.is_file():
        if not quiet:
            print("FAIL: INTEGRITY.sha256 not found")
            print(f"  Expected at: {MANIFEST_PATH}")
            print("  Run: python tools/lf_integrity.py update --i-understand")
        return 1

    manifest = _parse_manifest()
    if not manifest:
        if not quiet:
            print("FAIL: INTEGRITY.sha256 is empty or malformed")
        return 1

    errors: list[str] = []
    checked = 0

    for rel_str, expected in sorted(manifest.items()):
        fpath = VAULT / rel_str
        if not fpath.is_file():
            errors.append(f"MISSING  {rel_str}")
            continue
        actual = sha256_file(fpath)
        if actual != expected:
            errors.append(f"CHANGED  {rel_str}")
        checked += 1

    # Also check for new untracked files in covered dirs
    covered = _covered_files()
    for fpath in covered:
        rel = str(fpath.relative_to(VAULT))
        if rel not in manifest:
            errors.append(f"UNTRACKED  {rel}")

    if errors:
        if not quiet:
            print(f"INTEGRITY FAIL  ({len(errors)} issue(s), {checked} checked)")
            for e in errors:
                print(f"  {e}")
            print("  Run: python tools/lf_integrity.py update --i-understand")
        return 1

    if not quiet:
        print(f"INTEGRITY PASS  ({checked} files verified)")
    return 0


def cmd_update() -> int:
    """Regenerate INTEGRITY.sha256.  Returns 0 on success."""
    files = _covered_files()
    lines: list[str] = []
    lines.append("# LitForge Engine Integrity Manifest")
    lines.append("# Format: sha256  relative/path")
    lines.append(f"# Files: {len(files)}")
    lines.append("")
    for fpath in files:
        rel = str(fpath.relative_to(VAULT))
        h = sha256_file(fpath)
        lines.append(f"{h}  {rel}")
    lines.append("")
    content = "\n".join(lines)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(content, encoding="utf-8")
    print(f"INTEGRITY manifest written: {len(files)} files")
    print(f"  Path: {MANIFEST_PATH}")
    return 0


# ── CLI ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "verify":
        quiet = "--quiet" in args
        sys.exit(cmd_verify(quiet=quiet))
    elif args[0] == "update":
        if "--i-understand" not in args:
            print("ERROR: update requires --i-understand flag")
            print("  This regenerates the integrity manifest.")
            print("  Usage: python tools/lf_integrity.py update --i-understand")
            sys.exit(1)
        sys.exit(cmd_update())
    else:
        print("Usage: lf_integrity.py {verify [--quiet] | update --i-understand}")
        sys.exit(1)
