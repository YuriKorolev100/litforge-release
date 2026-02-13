#!/usr/bin/env python3
# Minimal LitForge linter (stub).
from pathlib import Path
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()

REQUIRED = [
    ROOT / "_LitForge" / "Dashboard.md",
    ROOT / "_LitForge" / "Engine" / "litforge.manifest.yaml",
    ROOT / "_LitForge" / "Templates" / "01-Discover.md",
    ROOT / "_LitForge" / "Templates" / "08-Ship.md",
    ROOT / "_LitForge" / "Logs" / "provenance" / "2026-02.md",
]

missing = [p for p in REQUIRED if not p.exists()]
if missing:
    print("FAIL: missing required files:")
    for p in missing:
        print(" -", p)
    sys.exit(1)

print("PASS: basic structure present")
