---
lf_schema: "stage/v1"
litforge_version: "0.1.0"
project_id: "EXAMPLE_TINY"
project_title: "EXAMPLE - Tiny Loop Demo"
stage: "Red-Team"
status: "draft"
loop_speed: "STRICT"
mode_packs: ["CORE"]
provider:
  preset: "Balanced"
  name: "None"
  model: ""
  browsing: false
  citations: false
gate:
  requires_acceptance: true
  criticals_open: 0
  overrides: []
artifacts:
  inputs: ["04-Draft"]
  outputs: ["06-Patch"]
redteam_target:
  draft_path: "Drafts/draft_v0.md"
  scope: "FULL"
severity_scale: ["Nit", "Minor", "Major", "Critical"]
provenance:
  log_month: "_LitForge/Logs/provenance/2026-02.md"
---

# 05 — Red-Team (hostile audit)

## Objective (required)
Find failure modes, drift, and genericness. Produce fixable findings.

## Target Artifact
- Draft under review: [[Drafts/draft_v0]]

## Findings (repeat format)
### Finding RT-001 — [Title]
- Severity: (Nit/Minor/Major/Critical)
- Type: (Drift/Uniqueness/Logic/Character/Pacing/Clarity/Voice/Continuity/Other)
- Evidence: quote exact lines/paragraphs (or reference section)
- Impact: what breaks for the reader
- Fix direction: what good looks like (not full rewrite)

## Drift Check (required)
- Position violations:
- Outline violations:
- Uniqueness anchors weakened by:

## Patch Queue (required)
- [ ] RT-001

## Acceptance Tests — Red-Team
- [ ] ≥3 findings written (or justify fewer)
- [ ] Each includes Evidence + Impact + Fix direction
- [ ] Any Critical clearly marked
- [ ] Next stage exists/linked
- [ ] Provenance entry appended

## Revise Plan
-
