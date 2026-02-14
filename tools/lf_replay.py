#!/usr/bin/env python3
"""LitForge moat-chain replay — Session 2.

Enforces the immutable Red-Team moat:
  hostile audit → patch spec → diff-first → regression → gate

Checks (all required for PASS):
  A) Stage/05-Red-Team.md has frontmatter + ≥1 finding bullet/checkbox
  B) Patches/PatchSpec_*.md exists (≥1)
  C) Patches/diffs/*.patch exists (≥1)
  D) Stage/07-Repeat.md has regression header + ≥1 completed [x] checkbox
  E) Ship gate (if Ship status in {approved, shipped}):
     redteam_cycles_completed >= ship_requires_redteam_cycles
     criticals_open <= gate.criticals_open

Exit codes: 0=PASS, 1=FAIL, 2=missing deps, 3=KILL_SWITCH
Reports written to: _LitForge/_DEV_REPORTS/
"""
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FATAL: PyYAML required (pip install pyyaml)")
    sys.exit(2)

# ── Args ─────────────────────────────────────────────────────────────
if len(sys.argv) < 2:
    print("Usage: lf_replay.py <project_path>")
    print("  project_path: absolute or relative path to a project directory")
    print("                e.g. Projects/EXAMPLE\\ -\\ Tiny\\ Loop\\ Demo")
    sys.exit(1)

PROJ = Path(sys.argv[1]).resolve()
if not PROJ.is_dir():
    print(f"FATAL: not a directory: {PROJ}")
    sys.exit(1)

# ── Derive vault root ────────────────────────────────────────────────
# Walk upward from project dir looking for _LitForge/
VAULT = None
candidate = PROJ
for _ in range(10):  # bounded climb, no infinite loops
    if (candidate / "_LitForge").is_dir():
        VAULT = candidate
        break
    parent = candidate.parent
    if parent == candidate:
        break
    candidate = parent

if VAULT is None:
    print("FATAL: cannot locate _LitForge/ in any ancestor of project path")
    sys.exit(1)

# ── Kill switch (fail-closed, checked before ANY work) ───────────────
KS = VAULT / "_LitForge" / "Agent" / "KILL_SWITCH.flag"
if KS.exists():
    print(f"ABORT: kill switch active  ({KS})")
    sys.exit(3)

# ── Helpers ──────────────────────────────────────────────────────────
def extract_frontmatter(path: Path) -> dict | None:
    """Parse YAML frontmatter between --- fences. Returns None on failure."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None


def read_body(path: Path) -> str:
    """Return everything after the closing --- of frontmatter, or full text."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""
    m = re.match(r"^---\n.*?\n---\n?(.*)", text, re.DOTALL)
    if m:
        return m.group(1)
    return text


errors: list[str] = []
warnings: list[str] = []

TAG = PROJ.name  # human-readable project label

ship_status = "draft"

# ══════════════════════════════════════════════════════════════════════
# CHECK A — Hostile audit: Stage/05-Red-Team.md
# ══════════════════════════════════════════════════════════════════════
rt_path = PROJ / "Stage" / "05-Red-Team.md"
if not rt_path.is_file():
    errors.append("MOAT_A: Stage/05-Red-Team.md not found")
else:
    rt_fm = extract_frontmatter(rt_path)
    if rt_fm is None:
        errors.append("MOAT_A: 05-Red-Team.md has no valid YAML frontmatter")
    else:
        if rt_fm.get("stage") != "Red-Team":
            errors.append(
                f"MOAT_A: 05-Red-Team.md stage field is "
                f"'{rt_fm.get('stage')}', expected 'Red-Team'"
            )

    body = read_body(rt_path)

    # Look for a Findings section header
    has_findings_header = bool(
        re.search(r"^##\s+.*[Ff]inding", body, re.MULTILINE)
    )
    if not has_findings_header:
        errors.append(
            "MOAT_A: 05-Red-Team.md has no '## Findings' section header"
        )

    # At least one finding: a bullet "- " or checkbox "- [ ]" / "- [x]"
    # under a ### Finding or similar subheading, OR any bullet in the
    # Findings section.  Be generous: any "- " line after a Findings
    # header counts, but we also accept "### Finding" subheadings.
    has_finding_item = bool(
        re.search(r"^###\s+Finding\s", body, re.MULTILINE)
    ) or bool(
        re.search(r"^- \[[ xX]\]\s+RT-\d{3}", body, re.MULTILINE)
    )
    if not has_finding_item:
        errors.append(
            "MOAT_A: 05-Red-Team.md has no finding entries "
            "(expected '### Finding RT-NNN' or '- [ ] RT-NNN')"
        )

# ══════════════════════════════════════════════════════════════════════
# CHECK B — Patch spec: Patches/PatchSpec_*.md
# ══════════════════════════════════════════════════════════════════════
patches_dir = PROJ / "Patches"
patchspecs = sorted(patches_dir.glob("PatchSpec_*.md")) if patches_dir.is_dir() else []
if not patchspecs:
    errors.append("MOAT_B: no PatchSpec_*.md found in Patches/")

# ══════════════════════════════════════════════════════════════════════
# CHECK C — Diff-first: Patches/diffs/*.patch
# ══════════════════════════════════════════════════════════════════════
diffs_dir = PROJ / "Patches" / "diffs"
diffs = sorted(diffs_dir.glob("*.patch")) if diffs_dir.is_dir() else []
if not diffs:
    errors.append("MOAT_C: no *.patch files found in Patches/diffs/")

# ══════════════════════════════════════════════════════════════════════
# CHECK D — Regression: Stage/07-Repeat.md
# ══════════════════════════════════════════════════════════════════════
rep_path = PROJ / "Stage" / "07-Repeat.md"
if not rep_path.is_file():
    errors.append("MOAT_D: Stage/07-Repeat.md not found")
else:
    rep_body = read_body(rep_path)

    rep_fm = extract_frontmatter(rep_path) or {}
    repeat_status = (rep_fm.get("status") or "draft").lower()
    repeat_is_final = repeat_status in ("accepted", "approved", "shipped")

    has_regression_header = bool(
        re.search(r"^##\s+(Regression|Tests|Acceptance Tests)", rep_body, re.MULTILINE)
    )
    if not has_regression_header:
        errors.append(
            "MOAT_D: 07-Repeat.md missing a regression/tests header (Regression/Tests/Acceptance Tests)"
        )

    ship_is_final = str(ship_status).lower() in ("approved", "shipped")

    completed_checks = re.findall(r"^- \[[xX]\]", rep_body, re.MULTILINE)
    if (repeat_is_final or ship_is_final) and not completed_checks:
        errors.append(
            "MOAT_D: 07-Repeat.md has no completed checkboxes "
            "(expected at least one '- [x]' when Repeat/Ship is final)"
        )
    elif not completed_checks:
        warnings.append(
            "MOAT_D: No completed checkboxes yet (Repeat is not final) — OK during draft"
        )


# ══════════════════════════════════════════════════════════════════════
# CHECK E — Ship gate (conditional: only if Ship claims approved/shipped)
# ══════════════════════════════════════════════════════════════════════
ship_path = PROJ / "Stage" / "08-Ship.md"
cfg_path = PROJ / "00-Project-Config.md"

if ship_path.is_file():
    ship_fm = extract_frontmatter(ship_path)
    if ship_fm is None:
        errors.append("MOAT_E: 08-Ship.md has no valid YAML frontmatter")
    else:
        ship_status = ship_fm.get("status", "draft")
        if ship_status in ("approved", "shipped"):
            # We need project config to read actuals
            if not cfg_path.is_file():
                errors.append(
                    "MOAT_E: Ship is {ship_status} but "
                    "00-Project-Config.md not found"
                )
            else:
                cfg_fm = extract_frontmatter(cfg_path)
                if cfg_fm is None:
                    errors.append(
                        "MOAT_E: 00-Project-Config.md has no valid "
                        "YAML frontmatter"
                    )
                else:
                    ship_gate = ship_fm.get("gate", {})
                    if not isinstance(ship_gate, dict):
                        errors.append("MOAT_E: gate block is not a mapping")
                    else:
                        overrides = ship_gate.get("overrides", [])

                        # E1: redteam cycles
                        req_rt = ship_gate.get(
                            "ship_requires_redteam_cycles", 1
                        )
                        act_rt = cfg_fm.get("redteam_cycles_completed")
                        if not isinstance(act_rt, int):
                            errors.append(
                                "MOAT_E: redteam_cycles_completed "
                                "missing or not int in project config"
                            )
                        elif act_rt < req_rt:
                            if overrides:
                                warnings.append(
                                    f"MOAT_E: Ship overridden — "
                                    f"redteam_cycles {act_rt}<{req_rt}, "
                                    f"overrides={overrides}"
                                )
                            else:
                                errors.append(
                                    f"MOAT_E: Ship BLOCKED — "
                                    f"redteam_cycles_completed={act_rt} "
                                    f"< required={req_rt} (no override)"
                                )

                        # E2: criticals
                        max_crit = ship_gate.get("criticals_open", 0)
                        act_crit = cfg_fm.get("criticals_open")
                        if act_crit is None:
                            warnings.append(
                                "MOAT_E: criticals_open not in project "
                                "config — cannot verify; skipping"
                            )
                        elif not isinstance(act_crit, int):
                            errors.append(
                                "MOAT_E: criticals_open is not int "
                                "in project config"
                            )
                        elif act_crit > max_crit:
                            if overrides:
                                warnings.append(
                                    f"MOAT_E: criticals override — "
                                    f"{act_crit}>{max_crit}, "
                                    f"overrides={overrides}"
                                )
                            else:
                                errors.append(
                                    f"MOAT_E: Ship BLOCKED — "
                                    f"criticals_open={act_crit} "
                                    f"> allowed={max_crit} (no override)"
                                )
else:
    warnings.append("MOAT_E: Stage/08-Ship.md not found — ship gate skipped")

# ══════════════════════════════════════════════════════════════════════
# Report + Output
# ══════════════════════════════════════════════════════════════════════
n_e, n_w = len(errors), len(warnings)

# Write report to _DEV_REPORTS/
reports_dir = VAULT / "_LitForge" / "_DEV_REPORTS"
reports_dir.mkdir(parents=True, exist_ok=True)

ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
safe_tag = re.sub(r"[^A-Za-z0-9_-]", "_", TAG)
report_path = reports_dir / f"replay_{safe_tag}_{ts}.txt"

lines: list[str] = []
lines.append(f"# Replay Report: {TAG}")
lines.append(f"# Timestamp: {ts}")
lines.append(f"# Project:   {PROJ}")
lines.append(f"# Vault:     {VAULT}")
lines.append("")
for w in warnings:
    lines.append(f"WARN   {w}")
for e in errors:
    lines.append(f"ERROR  {e}")
lines.append("")
if errors:
    lines.append(f"RESULT: FAIL  ({n_e} error(s), {n_w} warning(s))")
else:
    lines.append(f"RESULT: PASS  ({n_w} warning(s))")

report_text = "\n".join(lines) + "\n"

try:
    report_path.write_text(report_text, encoding="utf-8")
except OSError as exc:
    print(f"WARN: could not write report: {exc}", file=sys.stderr)

# Console output
for w in warnings:
    print(f"WARN   {w}")
for e in errors:
    print(f"ERROR  {e}")

print(f"\n{'=' * 50}")
if errors:
    print(f"RESULT: FAIL  ({n_e} error(s), {n_w} warning(s))")
    print(f"Report: {report_path}")
    sys.exit(1)
else:
    print(f"RESULT: PASS  ({n_w} warning(s))")
    print(f"Report: {report_path}")
    sys.exit(0)
