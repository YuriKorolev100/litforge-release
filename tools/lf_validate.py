#!/usr/bin/env python3
"""LitForge schema validator – hardened MVP enforcement.

Validates YAML frontmatter against:
  - stage/v1        (stage.v1.md)
  - project-config/v1  (project-config.v1.md)

Security hardening:
  - Bounded read: only first 64 KiB of any file is touched.
  - YAML aliases/anchors rejected (custom loader).
  - Returns None on any parse or encoding error.
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FATAL: PyYAML required (pip install pyyaml)")
    sys.exit(2)

# Import size constant from lf_safe (co-located in tools/)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lf_safe import MAX_FRONTMATTER_BYTES


# ── Alias-rejecting YAML loader ─────────────────────────────────────
class _NoAliasLoader(yaml.SafeLoader):
    """SafeLoader that refuses anchors/aliases (billion-laughs defence)."""

_def_compose_node = yaml.SafeLoader.compose_node

def _no_alias_compose_node(self, parent, index):
    if self.check_event(yaml.events.AliasEvent):
        raise yaml.YAMLError("YAML aliases/anchors are not permitted")
    return _def_compose_node(self, parent, index)

_NoAliasLoader.compose_node = _no_alias_compose_node  # type: ignore[assignment]


# ── Constants derived verbatim from schema docs ──────────────────────
STAGE_NAMES = [
    "Discover", "Position", "Outline", "Draft",
    "Red-Team", "Patch", "Repeat", "Ship",
]
STATUS_VALUES = ["draft", "in_review", "revise", "approved", "blocked", "shipped"]
LOOP_SPEEDS   = ["FAST", "STRICT"]
PROV_PRESETS  = ["Simple", "Balanced", "Private"]
PROV_NAMES    = ["None", "OpenAI", "Anthropic", "Google", "xAI", "Local", "Other"]


def extract_frontmatter(path: Path) -> dict | None:
    """Return parsed YAML frontmatter or None.

    Bounded read: only the first MAX_FRONTMATTER_BYTES are read.
    Alias/anchor YAML constructs are rejected.
    Returns None on any encoding, I/O, or parse error.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            head = fh.read(MAX_FRONTMATTER_BYTES)
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    m = re.match(r"^---\n(.*?)\n---", head, re.DOTALL)
    if not m:
        return None
    try:
        result = yaml.load(m.group(1), Loader=_NoAliasLoader)
        return result if isinstance(result, dict) else {}
    except yaml.YAMLError:
        return None


# ── Helpers ──────────────────────────────────────────────────────────

def _req(errors: list, fm: dict, key: str, label: str):
    if key not in fm:
        errors.append(f"{label}: missing required key '{key}'")


def _enum(errors: list, fm: dict, key: str, allowed: list, label: str):
    v = fm.get(key)
    if v is not None and v not in allowed:
        errors.append(f"{label}: invalid {key} '{v}' (expected {allowed})")


def _provider_block(errors: list, fm: dict, label: str):
    prov = fm.get("provider")
    if not isinstance(prov, dict):
        errors.append(f"{label}: provider must be a mapping")
        return
    for pk in ("preset", "name", "model"):
        _req(errors, prov, pk, label)
    _enum(errors, prov, "preset", PROV_PRESETS, label)
    _enum(errors, prov, "name", PROV_NAMES, label)
    for bk in ("browsing", "citations"):
        if bk in prov and not isinstance(prov[bk], bool):
            errors.append(f"{label}: provider.{bk} must be bool")


# ── Public validators ────────────────────────────────────────────────
def validate_stage(fm: dict, path: Path) -> list[str]:
    """Validate a stage file's frontmatter against stage/v1."""
    label = str(path)
    if not fm:
        return [f"{label}: no YAML frontmatter found"]
    errors: list[str] = []

    for k in ("lf_schema", "litforge_version", "project_id", "project_title",
              "stage", "status", "loop_speed", "mode_packs"):
        _req(errors, fm, k, label)

    if fm.get("lf_schema") != "stage/v1":
        errors.append(f"{label}: lf_schema must be 'stage/v1', got '{fm.get('lf_schema')}'")

    _enum(errors, fm, "stage",  STAGE_NAMES,    label)
    _enum(errors, fm, "status", STATUS_VALUES,   label)
    _enum(errors, fm, "loop_speed", LOOP_SPEEDS, label)

    if not isinstance(fm.get("mode_packs"), list):
        errors.append(f"{label}: mode_packs must be an array")

    _provider_block(errors, fm, label)

    # gate block
    gate = fm.get("gate")
    if not isinstance(gate, dict):
        errors.append(f"{label}: gate must be a mapping")
    else:
        for gk in ("requires_acceptance", "criticals_open", "overrides"):
            _req(errors, gate, gk, label)
        if "criticals_open" in gate and not isinstance(gate["criticals_open"], int):
            errors.append(f"{label}: gate.criticals_open must be int")

    # artifacts block
    arts = fm.get("artifacts")
    if not isinstance(arts, dict):
        errors.append(f"{label}: artifacts must be a mapping")
    else:
        for ak in ("inputs", "outputs"):
            _req(errors, arts, ak, label)

    # provenance block
    pv = fm.get("provenance")
    if not isinstance(pv, dict) or "log_month" not in (pv or {}):
        errors.append(f"{label}: missing provenance.log_month")

    return errors


def validate_project_config(fm: dict, path: Path) -> list[str]:
    """Validate a project-config file against project-config/v1."""
    label = str(path)
    if not fm:
        return [f"{label}: no YAML frontmatter found"]
    errors: list[str] = []

    if fm.get("lf_schema") != "project-config/v1":
        errors.append(f"{label}: lf_schema must be 'project-config/v1', got '{fm.get('lf_schema')}'")

    for k in ("lf_schema", "litforge_version", "project_id", "title",
              "mode_packs", "loop_speed_default", "current_stage", "next_stage",
              "redteam_cycles_completed", "criticals_open"):
        _req(errors, fm, k, label)

    _enum(errors, fm, "loop_speed_default", LOOP_SPEEDS, label)
    _provider_block(errors, fm, label)

    return errors
