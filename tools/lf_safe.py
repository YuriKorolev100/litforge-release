#!/usr/bin/env python3
"""LitForge shared security primitives.

Every tool imports from here.  No network, no shell, stdlib + pathlib only.
"""
import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────
MAX_FRONTMATTER_BYTES = 64 * 1024   # 64 KiB — generous for any stage file
MAX_FILE_READ_BYTES   = 2 * 1024 * 1024  # 2 MiB default cap


def find_vault_root(start: Path | None = None) -> Path:
    """Walk upward from *start* (default: this file's dir) to find _LitForge/.

    Bounded to 10 levels.  Calls sys.exit(1) if not found.
    """
    candidate = (start or Path(__file__).resolve().parent).resolve()
    for _ in range(10):
        if (candidate / "_LitForge").is_dir():
            return candidate
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent
    print("FATAL: cannot locate _LitForge/ in ancestors")
    sys.exit(1)


def check_kill_switch(vault: Path) -> None:
    """If kill-switch flag exists, print message and exit 3.  Fail-closed."""
    ks = vault / "_LitForge" / "Agent" / "KILL_SWITCH.flag"
    if ks.exists():
        print(f"ABORT: kill switch active  ({ks})")
        sys.exit(3)


def read_text_limited(
    path: Path,
    max_bytes: int = MAX_FILE_READ_BYTES,
) -> str | None:
    """Read a text file with a hard size cap.  Returns None on any error."""
    try:
        size = path.stat().st_size
        if size > max_bytes:
            return None
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError, ValueError):
        return None


def atomic_write_text(
    path: Path,
    content: str,
    allowed_roots: list[Path] | None = None,
) -> None:
    """Write *content* to *path* atomically.

    Security:
      - Refuses if *path* is a symlink (target could be outside vault).
      - If *allowed_roots* given, asserts *path* resolves within one of them.
      - Writes to a temp file in the same directory, then renames.
    """
    path = Path(path)
    if path.is_symlink():
        raise PermissionError(f"refusing to write through symlink: {path}")
    if allowed_roots is not None:
        assert_within_any(path, allowed_roots)
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(parent), prefix=".lf_", suffix=".tmp")
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        os.replace(tmp, str(path))
    except BaseException:
        os.close(fd) if not os.get_inheritable(fd) else None  # noqa: best-effort
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def assert_within_any(path: Path, allowed: list[Path]) -> None:
    """Raise PermissionError unless *path* resolves inside one of *allowed*."""
    resolved = Path(path).resolve()
    for root in allowed:
        try:
            resolved.relative_to(root.resolve())
            return
        except ValueError:
            continue
    raise PermissionError(
        f"path {resolved} is not within any allowed root: "
        f"{[str(r) for r in allowed]}"
    )


def strip_frontmatter(text: str) -> str:
    """Return everything after the closing --- of YAML frontmatter."""
    m = re.match(r"^---\n.*?\n---\n?(.*)", text, re.DOTALL)
    return m.group(1) if m else text


def sha256_file(path: Path) -> str:
    """Return lowercase hex SHA-256 digest of a file.  Reads in 8 KiB chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
