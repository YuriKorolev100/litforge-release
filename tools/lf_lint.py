#!/usr/bin/env python3
"""LitForge linter – MVP enforcement (Session 1).

Checks:
  1. Kill switch (fail-closed)
  2. Vault structure (required files)
  3. Stage schema validation (stage/v1)
  4. Project-config schema validation (project-config/v1)
  5. Ship gate enforcement (redteam_cycles + criticals_open)

Exit codes: 0=PASS, 1=FAIL, 3=KILL_SWITCH
"""
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()

# ── 0. Kill switch (fail-closed) ─────────────────────────────────────
KS = ROOT / "_LitForge" / "Agent" / "KILL_SWITCH.flag"
if KS.exists():
    print(f"ABORT: kill switch active  ({KS})")
    print("No checks executed.  Remove the flag to proceed.")
    sys.exit(3)

# ── Import validator (same tools/ dir) ───────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lf_validate import (
    extract_frontmatter, validate_stage, validate_project_config,
)

errors:   list[str] = []
warnings: list[str] = []

# ── 1. Vault structure ───────────────────────────────────────────────
REQUIRED = [
    "_LitForge/Dashboard.md",
    "_LitForge/Engine/litforge.manifest.yaml",
    "_LitForge/Setup/00-Setup-Wizard.md",
    "_LitForge/Setup/01-Capability-Check.md",
    "_LitForge/Setup/02-Safety-Fence.md",
]
for i, prefix in enumerate(
    ["01-Discover","02-Position","03-Outline","04-Draft",
     "05-Red-Team","06-Patch","07-Repeat","08-Ship"], start=1):
    REQUIRED.append(f"_LitForge/Templates/{prefix}.md")

for rel in REQUIRED:
    if not (ROOT / rel).exists():
        errors.append(f"STRUCT: missing {rel}")

# ── 2. Per-project validation ────────────────────────────────────────
projects_dir = ROOT / "Projects"
if projects_dir.is_dir():
    for proj in sorted(projects_dir.iterdir()):
        if not proj.is_dir() or proj.name.startswith("_"):
            continue  # skip _Project-Template

        tag = proj.name

        # 2a. Project config
        cfg_path = proj / "00-Project-Config.md"
        cfg_fm = None
        if cfg_path.exists():
            cfg_fm = extract_frontmatter(cfg_path)
            errs = validate_project_config(cfg_fm, cfg_path)
            errors.extend(errs)
        else:
            errors.append(f"SCHEMA: missing Projects/{tag}/00-Project-Config.md")

        # 2b. Stage files
        stage_dir = proj / "Stage"
        if not stage_dir.is_dir():
            errors.append(f"STRUCT: missing Projects/{tag}/Stage/")
            continue

        for sf in sorted(stage_dir.glob("*.md")):
            fm = extract_frontmatter(sf)
            if fm:
                errors.extend(validate_stage(fm, sf))
            else:
                warnings.append(f"SCHEMA: no frontmatter in {sf.relative_to(ROOT)}")

        # ── 3. Ship gate ─────────────────────────────────────────────
        ship_path = stage_dir / "08-Ship.md"
        if ship_path.exists() and cfg_fm:
            ship_fm = extract_frontmatter(ship_path)
            if ship_fm:
                ship_gate = ship_fm.get("gate", {})
                ship_status = ship_fm.get("status", "draft")

                # Gate enforced only when Ship claims approved/shipped
                if ship_status in ("approved", "shipped"):
                    req_rt = ship_gate.get("ship_requires_redteam_cycles", 1)
                    act_rt = cfg_fm.get("redteam_cycles_completed", 0)
                    overrides = ship_gate.get("overrides", [])

                    if not isinstance(act_rt, int):
                        errors.append(f"GATE [{tag}]: redteam_cycles_completed is not int")
                    elif act_rt < req_rt:
                        if overrides:
                            warnings.append(
                                f"GATE [{tag}]: Ship overridden — "
                                f"redteam_cycles {act_rt}<{req_rt}, "
                                f"overrides={overrides}")
                        else:
                            errors.append(
                                f"GATE [{tag}]: Ship BLOCKED — "
                                f"redteam_cycles_completed={act_rt} "
                                f"< required={req_rt} (no override)")

                    max_crit = ship_gate.get("criticals_open", 0)
                    act_crit = cfg_fm.get("criticals_open", 0)
                    if isinstance(act_crit, int) and act_crit > max_crit:
                        if overrides:
                            warnings.append(
                                f"GATE [{tag}]: criticals override — "
                                f"{act_crit}>{max_crit}, overrides={overrides}")
                        else:
                            errors.append(
                                f"GATE [{tag}]: Ship BLOCKED — "
                                f"criticals_open={act_crit} "
                                f"> allowed={max_crit} (no override)")

# ── 4. Output ────────────────────────────────────────────────────────
for w in warnings:
    print(f"WARN  {w}")
for e in errors:
    print(f"FAIL  {e}")

n_e, n_w = len(errors), len(warnings)
print(f"\n{'=' * 50}")
if errors:
    print(f"RESULT: FAIL  ({n_e} error(s), {n_w} warning(s))")
    sys.exit(1)
else:
    print(f"RESULT: PASS  ({n_w} warning(s))")
    sys.exit(0)
